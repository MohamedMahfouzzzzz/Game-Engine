# /**************************************************************************/
# /*  layer.py                                                              */
# /**************************************************************************/

"""Layer model for pixel art documents.

Equivalent to Aseprite's doc::Layer class.
"""

from typing import List, Optional, Dict
from enum import Enum, auto
from .cel import Cel, LinkedCel
from .blend_mode import BlendMode


class LayerFlags(Enum):
    """Layer flags."""
    VISIBLE = auto()
    EDITABLE = auto()
    LOCK_MOVEMENT = auto()
    BACKGROUND = auto()
    PREFER_LINKED_CELS = auto()
    COLLAPSED = auto()
    REFERENCE = auto()


class Layer:
    """A layer in the sprite.
    
    A layer contains cels for each frame of animation.
    In non-animated sprites, there's just one cel at frame 0.
    """
    
    _id_counter = 0
    
    def __init__(self, name: str = "Layer", is_background: bool = False):
        Layer._id_counter += 1
        self.id = Layer._id_counter
        self.name = name
        self._sprite = None  # Parent sprite (set by sprite.add_layer)
        
        # Layer properties
        self.visible = True
        self.editable = True
        self.opacity = 255  # 0-255
        self.blend_mode = BlendMode.NORMAL
        
        # Cels indexed by frame number
        self._cels: Dict[int, Cel] = {}
        
        # For background layers
        self._is_background = is_background
        self._is_transparent = not is_background
        
        # For groups
        self._parent: Optional['LayerGroup'] = None
    
    @property
    def is_background(self) -> bool:
        """Check if this is a background layer."""
        return self._is_background
    
    @property
    def is_transparent(self) -> bool:
        """Check if layer supports transparency."""
        return self._is_transparent
    
    def get_cel(self, frame: int) -> Optional[Cel]:
        """Get cel at frame."""
        return self._cels.get(frame)
    
    def set_cel(self, frame: int, cel: Cel) -> None:
        """Set cel at frame."""
        cel.layer_id = self.id
        cel.frame = frame
        self._cels[frame] = cel
    
    def remove_cel(self, frame: int) -> None:
        """Remove cel at frame."""
        if frame in self._cels:
            del self._cels[frame]
    
    def get_cels(self) -> List[Cel]:
        """Get all cels in this layer."""
        return list(self._cels.values())
    
    def add_cel(self, frame: int, cel: Cel) -> None:
        """Add a cel to this layer at frame."""
        cel.layer_id = self.id
        cel.frame = frame
        self._cels[frame] = cel
    
    def is_continuous(self) -> bool:
        """Check if layer has cels in all frames."""
        if not self._sprite:
            return len(self._cels) > 0
        return len(self._cels) == self._sprite.frame_count
    
    def get_affected_frames(self) -> List[int]:
        """Get frames that have cels in this layer."""
        return sorted(self._cels.keys())
    
    def copy(self) -> 'Layer':
        """Create a copy of this layer with copied cels."""
        new_layer = Layer(f"{self.name} copy", self._is_background)
        new_layer.visible = self.visible
        new_layer.editable = self.editable
        new_layer.opacity = self.opacity
        new_layer.blend_mode = self.blend_mode
        
        # Copy all cels
        for frame, cel in self._cels.items():
            new_cel = cel.copy()
            new_layer._cels[frame] = new_cel
        
        return new_layer
    
    def flatten(self) -> Cel:
        """Flatten all cels into one (returns first frame cel for simplicity)."""
        if not self._cels:
            return None
        return self._cels.get(0, list(self._cels.values())[0])


class LayerGroup(Layer):
    """A group of layers (layer folder).
    
    Groups can be nested and have their own visibility/opacity.
    """
    
    def __init__(self, name: str = "Group"):
        super().__init__(name)
        self._children: List[Layer] = []
        self._collapsed = False  # UI collapsed state
    
    @property
    def children(self) -> List[Layer]:
        """Get child layers."""
        return self._children.copy()
    
    def add_layer(self, layer: Layer) -> None:
        """Add layer to group."""
        layer._parent = self
        self._children.append(layer)
    
    def remove_layer(self, layer: Layer) -> None:
        """Remove layer from group."""
        if layer in self._children:
            layer._parent = None
            self._children.remove(layer)
    
    def insert_layer(self, index: int, layer: Layer) -> None:
        """Insert layer at position."""
        layer._parent = self
        self._children.insert(index, layer)
    
    def get_layer_index(self, layer: Layer) -> int:
        """Get index of layer in group."""
        return self._children.index(layer)
    
    @property
    def collapsed(self) -> bool:
        """Get collapsed state."""
        return self._collapsed
    
    @collapsed.setter
    def collapsed(self, value: bool) -> None:
        self._collapsed = value
    
    def is_empty(self) -> bool:
        """Check if group has no children."""
        return len(self._children) == 0
    
    def get_all_layers(self) -> List[Layer]:
        """Get all layers recursively (flattens hierarchy)."""
        result = []
        for child in self._children:
            result.append(child)
            if isinstance(child, LayerGroup):
                result.extend(child.get_all_layers())
        return result
