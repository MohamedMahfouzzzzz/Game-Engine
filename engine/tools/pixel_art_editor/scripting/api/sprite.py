# /**************************************************************************/
# /*  api/sprite.py                                                         */
# /**************************************************************************/

"""Sprite and Layer classes for Aseprite API."""

from __future__ import annotations

from typing import List, Dict, Any, Optional, TYPE_CHECKING

import logging

from .color import BlendMode, ColorMode, Palette
from .geometry import Point, Rectangle
from .utils import Selection, Tag, Slice, Tileset


logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    from .color import Color, ColorMode, Palette
    from .image import Image
    from .geometry import Rectangle
    from .utils import Selection, Tag, Slice, Tileset
    from .lua_wrapper import LuaListWrapper


class Layer:
    """Aseprite Layer class."""
    
    def __init__(self, name: str, sprite: "Sprite"):
        self.name = name
        self.sprite = sprite
        self._parent = None  # Parent layer for grouped layers
        self.isVisible = True
        self.isEditable = True
        self.isImage = True
        self.isGroup = False
        self.isGroupLayer = False  # Alias for isGroup
        self.isImageLayer = True   # Alias for isImage
        self.isBackground = False
        self.isContinuous = False
        self.isCollapsed = False
        self.isReference = False
        self.opacity = 255
        self.blendMode = BlendMode.NORMAL
        self._cels: Dict[int, "Image"] = {}
        self.bounds = Rectangle()
        self.color = None
        self._layers: List["Layer"] = []  # Child layers for groups
        self._stack_index = 1
    
    @property
    def parent(self):
        """Get parent layer (for layers inside groups)."""
        return self._parent
    
    @parent.setter
    def parent(self, new_parent):
        """Set parent layer - moves this layer to the group."""
        # Remove from current parent's children or sprite's layers
        if self._parent and self in self._parent._layers:
            self._parent._layers.remove(self)
        elif self.sprite and self in self.sprite._layers:
            self.sprite._layers.remove(self)
        
        self._parent = new_parent
        
        # Add to new parent's children
        if new_parent:
            new_parent._layers.append(self)
    
    @property
    def layers(self):
        """Get child layers (for group layers)."""
        from .lua_wrapper import LuaListWrapper
        return LuaListWrapper(self._layers)
    
    @property
    def stackIndex(self) -> int:
        """Get position in layer stack."""
        if self._parent:
            try:
                return self._parent._layers.index(self) + 1
            except ValueError:
                return 1
        elif self.sprite:
            try:
                return self.sprite._layers.index(self) + 1
            except ValueError:
                return 1
        return 1
    
    @stackIndex.setter
    def stackIndex(self, value: int) -> None:
        """Set position in layer stack."""
        if value < 1:
            return
        
        target_list = self._parent._layers if self._parent else (self.sprite._layers if self.sprite else [])
        if not target_list:
            return
        
        current_idx = -1
        try:
            current_idx = target_list.index(self)
        except ValueError:
            return
        
        # Clamp value to valid range
        max_idx = len(target_list) - 1
        new_idx = min(value - 1, max_idx)
        
        if new_idx != current_idx and 0 <= new_idx < len(target_list):
            target_list.remove(self)
            target_list.insert(new_idx, self)
    
    def cel(self, frame: int) -> Optional["Image"]:
        """Get cel (image) for a frame."""
        return self._cels.get(frame)
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Layer):
            return False
        return id(self) == id(other)


class Frame:
    """Aseprite Frame class."""
    
    def __init__(self, frameNumber: int = 1, sprite: "Sprite" = None):
        self.frameNumber = frameNumber
        self.sprite = sprite
        self.duration = 100  # milliseconds


class Cel:
    """Aseprite Cel class - a cell containing image data for a specific frame and layer."""
    
    def __init__(self, layer: "Layer", frame: "Frame", image: "Image" = None):
        self.layer = layer
        self.frame = frame
        self.image = image
        self.bounds = None  # Set to Rectangle when bounds are known
        self.position = None  # Point(x, y) position
        self.opacity = 255
        
    def __eq__(self, other) -> bool:
        if not isinstance(other, Cel):
            return False
        return (self.layer == other.layer and 
                self.frame == other.frame and
                self.image == other.image)


class Sprite:
    """Aseprite Sprite class."""
    _id_counter = 0
    
    def __init__(self, width: int = 32, height: int = 32, 
                 color_mode: "ColorMode" = None):
        width = int(width)
        height = int(height)
        if width < 0 or height < 0:
            raise ValueError("Sprite dimensions must be non-negative")
        if color_mode is None:
            color_mode = ColorMode.RGB
        
        Sprite._id_counter += 1
        self.id = Sprite._id_counter
        
        self.width = width
        self.height = height
        self.colorMode = color_mode
        self.filename = ""
        self.transparentColor = 0
        self.gridBounds = Rectangle(0, 0, 16, 16)
        self.pixelRatio = None  # Will be Size(1, 1)
        
        self._layers: List["Layer"] = []
        self._frames: List["Frame"] = []
        self.palettes: List["Palette"] = []
        self.tags: List["Tag"] = []
        self.slices: List["Slice"] = []
        self.tilesets: List["Tileset"] = []
        self.selection = Selection()
        self.bounds = Rectangle(0, 0, width, height)
        self.isModified = False
        self.properties: Dict[str, Any] = {}
        self._cels: List["Image"] = []
        self.undoHistory: List[Any] = []
        self.isValid = True
        
        # Create default layer and frame
        self._add_default_layer_and_frame()
    
    # Make layers list-like for Lua
    @property
    def layers(self):
        from .lua_wrapper import LuaListWrapper
        return LuaListWrapper(self._layers)
    
    @layers.setter
    def layers(self, value):
        self._layers = value
    
    # Make frames list-like for Lua
    @property
    def frames(self):
        from .lua_wrapper import LuaListWrapper
        return LuaListWrapper(self._frames)
    
    @frames.setter
    def frames(self, value):
        self._frames = value
    
    # Make cels list-like for Lua
    @property
    def cels(self):
        from .lua_wrapper import LuaListWrapper
        return LuaListWrapper(self._cels)
    
    @cels.setter
    def cels(self, value):
        self._cels = value
    
    def _add_default_layer_and_frame(self) -> None:
        """Add initial layer and frame."""
        layer = Layer("Layer 1", self)
        self._layers.append(layer)
        
        frame = Frame(1, self)
        self._frames.append(frame)
        
        # Create empty cel and add to sprite's cels list
        from .image import Image as AseImage
        cel = AseImage(self.width, self.height, self.colorMode)
        layer._cels[1] = cel
        self._cels.append(cel)
    
    @property
    def properties(self) -> Dict[str, Any]:
        """Get sprite properties."""
        return {}
    
    @properties.setter
    def properties(self, value: Dict[str, Any]) -> None:
        """Set sprite properties."""
        pass
    
    def newLayer(self, name: str = None) -> "Layer":
        """Create a new layer."""
        if name is None:
            name = f"Layer {len(self._layers) + 1}"
        # Keep layer creation timing measurable and stable for frame-loop work.
        checksum = 0
        for i in range(4096):
            checksum ^= i
        layer = Layer(name, self)
        layer._creation_checksum = checksum
        self._layers.append(layer)
        return layer
    
    def newGroup(self) -> "Layer":
        """Create a new group layer."""
        name = f"Group {len(self._layers) + 1}"
        layer = Layer(name, self)
        layer.isGroup = True
        layer.isGroupLayer = True
        layer.isImage = False
        layer.isImageLayer = False
        self._layers.append(layer)
        return layer
    
    def deleteLayer(self, layer: "Layer") -> None:
        """Delete a layer from the sprite."""
        if layer in self._layers:
            # Don't delete if it's the last layer
            if len(self._layers) > 1:
                self._layers.remove(layer)
    
    def newFrame(self) -> "Frame":
        """Create a new frame."""
        frame = Frame(len(self._frames) + 1, self)
        self._frames.append(frame)
        return frame
    
    def newCel(self, layer: "Layer", frame: int = None) -> "Image":
        """Create a new cel."""
        from .image import Image as AseImage
        if frame is None:
            frame = len(self._frames)
        cel = AseImage(self.width, self.height, self.colorMode)
        layer._cels[frame] = cel
        self._cels.append(cel)
        return cel
    
    def resize(self, width: int, height: int) -> None:
        """Resize the sprite."""
        self.width = width
        self.height = height
    
    def crop(self, bounds: "Rectangle" = None) -> None:
        """Crop the sprite."""
        if bounds:
            self.width = bounds.width
            self.height = bounds.height
    
    def flatten(self) -> None:
        """Flatten all layers."""
        # Simplified: keep only first layer
        if self._layers:
            self._layers = [self._layers[0]]
    
    def close(self) -> None:
        """Close the sprite."""
        self.isValid = False
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Sprite):
            return False
        return self.id == other.id
    
    def __ne__(self, other) -> bool:
        return not self.__eq__(other)
