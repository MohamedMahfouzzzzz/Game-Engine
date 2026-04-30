# /**************************************************************************/
# /*  aseprite_api.py                                                       */
# /**************************************************************************/

"""Aseprite-compatible Lua API for running Aseprite scripts/tests.

This module provides an Aseprite-compatible API that allows running
Aseprite Lua scripts and tests within the engine's pixel art editor.
"""

from __future__ import annotations

import io
import sys
import math
import json
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import IntEnum

try:
    import lupa
    from lupa import LuaRuntime
    LUPA_AVAILABLE = True
except ImportError:
    LUPA_AVAILABLE = False

from PIL import Image as PILImage

import logging



logger = logging.getLogger(__name__)

class ColorMode(IntEnum):
    """Aseprite color modes."""
    RGB = 0
    GRAYSCALE = 1
    INDEXED = 2
    TILEMAP = 3


class BlendMode(IntEnum):
    """Blend modes for drawing operations."""
    NORMAL = 0
    MULTIPLY = 1
    SCREEN = 2
    OVERLAY = 3
    DARKEN = 4
    LIGHTEN = 5
    COLOR_DODGE = 6
    COLOR_BURN = 7
    HARD_LIGHT = 8
    SOFT_LIGHT = 9
    DIFFERENCE = 10
    EXCLUSION = 11
    HSL_HUE = 12
    HSL_SATURATION = 13
    HSL_COLOR = 14
    HSL_LUMINOSITY = 15
    ADDITION = 16
    SUBTRACT = 17
    DIVIDE = 18


class ColorSpace:
    """Color space representation."""
    
    def __init__(self, name: str = "sRGB"):
        self.name = name
    
    @staticmethod
    def sRGB() -> "ColorSpace":
        return ColorSpace("sRGB")


class ImageSpec:
    """Image specification for creating images."""
    
    def __init__(self, width: int = 0, height: int = 0, colorMode: int = 0, 
                 transparentColor: int = 0, bitsPerPixel: int = 32):
        self.width = width
        self.height = height
        self.colorMode = colorMode
        self.transparentColor = transparentColor
        self.bitsPerPixel = bitsPerPixel


@dataclass
class LuaListWrapper:
    """Wrapper to make Python lists work with Lua # operator and indexing."""
    
    def __init__(self, items: List[Any]):
        self._items = items
    
    def __len__(self) -> int:
        return len(self._items)
    
    def __getitem__(self, index: int) -> Any:
        # Lua uses 1-based indexing
        if isinstance(index, int):
            if index >= 1:
                index -= 1
            if 0 <= index < len(self._items):
                return self._items[index]
        return None
    
    def __setitem__(self, index: int, value: Any) -> None:
        if isinstance(index, int):
            if index >= 1:
                index -= 1
            if 0 <= index < len(self._items):
                self._items[index] = value
    
    def append(self, item: Any) -> None:
        self._items.append(item)
    
    def __iter__(self):
        return iter(self._items)


@dataclass
class Color:
    """Aseprite color representation."""
    r: int = 0
    g: int = 0
    b: int = 0
    a: int = 255
    red: int = 0
    green: int = 0
    blue: int = 0
    alpha: int = 255
    
    def __post_init__(self):
        """Sync r/g/b/a with red/green/blue/alpha."""
        if self.red == 0 and self.r != 0:
            self.red = self.r
        if self.green == 0 and self.g != 0:
            self.green = self.g
        if self.blue == 0 and self.b != 0:
            self.blue = self.b
        if self.alpha == 255 and self.a != 255:
            self.alpha = self.a
    
    @property
    def rgbaPixel(self) -> int:
        """RGBA pixel value as integer."""
        return (self.r << 0) | (self.g << 8) | (self.b << 16) | (self.a << 24)
    
    def __int__(self) -> int:
        """Convert to Aseprite color integer format (RGBA)."""
        return (self.r << 0) | (self.g << 8) | (self.b << 16) | (self.a << 24)
    
    @classmethod
    def from_int(cls, color_int: int) -> "Color":
        """Create color from Aseprite integer format."""
        return cls(
            r=(color_int >> 0) & 0xFF,
            g=(color_int >> 8) & 0xFF,
            b=(color_int >> 16) & 0xFF,
            a=(color_int >> 24) & 0xFF
        )


class PixelColor:
    """Aseprite app.pixelColor API."""
    
    @staticmethod
    def rgba(r: int, g: int, b: int, a: int = 255) -> int:
        """Create RGBA color integer."""
        return Color(r, g, b, a).__int__()
    
    @staticmethod
    def rgbaR(color: int) -> int:
        """Get red component."""
        return (color >> 0) & 0xFF
    
    @staticmethod
    def rgbaG(color: int) -> int:
        """Get green component."""
        return (color >> 8) & 0xFF
    
    @staticmethod
    def rgbaB(color: int) -> int:
        """Get blue component."""
        return (color >> 16) & 0xFF
    
    @staticmethod
    def rgbaA(color: int) -> int:
        """Get alpha component."""
        return (color >> 24) & 0xFF
    
    @staticmethod
    def gray(v: int, a: int = 255) -> int:
        """Create grayscale color integer."""
        return Color(v, v, v, a).__int__()
    
    @staticmethod
    def grayaV(color: int) -> int:
        """Get grayscale value."""
        return (color >> 0) & 0xFF
    
    @staticmethod
    def grayaA(color: int) -> int:
        """Get grayscale alpha."""
        return (color >> 24) & 0xFF
    
    # Single letter aliases used by some scripts
    @staticmethod
    def grayV(color: int) -> int:
        """Get grayscale value (alias)."""
        return (color >> 0) & 0xFF
    
    @staticmethod
    def grayA(color: int) -> int:
        """Get grayscale alpha (alias)."""
        return (color >> 24) & 0xFF
    
    @staticmethod
    def graya(v: int, a: int = 255) -> int:
        """Create grayscale color integer."""
        return Color(v, v, v, a).__int__()


class Image:
    """Aseprite Image class."""
    _id_counter = 0
    
    def __init__(self, width: int, height: int, color_mode: ColorMode = ColorMode.RGB):
        self.width = width
        self.height = height
        self.colorMode = color_mode
        self._pixels: List[List[Color]] = [
            [Color(0, 0, 0, 0) for _ in range(width)]
            for _ in range(height)
        ]
        Image._id_counter += 1
        self.id = Image._id_counter
        self.rowStride = width * 4  # 4 bytes per pixel (RGBA)
        self.image = None  # PIL Image reference
    
    @classmethod
    def from_pil(cls, pil_image: PILImage.Image) -> "Image":
        """Create Image from PIL Image."""
        pil_image = pil_image.convert("RGBA")
        img = cls(pil_image.width, pil_image.height, ColorMode.RGB)
        for y in range(img.height):
            for x in range(img.width):
                r, g, b, a = pil_image.getpixel((x, y))
                img._pixels[y][x] = Color(r, g, b, a)
        return img
    
    def getPixel(self, x: int, y: int) -> int:
        """Get pixel color at position."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return int(self._pixels[y][x])
        return 0
    
    def putPixel(self, x: int, y: int, color: int) -> None:
        """Set pixel color at position."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self._pixels[y][x] = Color.from_int(color)
    
    def clear(self, color: int = 0) -> None:
        """Clear image to a color."""
        c = Color.from_int(color)
        for row in self._pixels:
            for i in range(len(row)):
                row[i] = c
    
    def clone(self) -> "Image":
        """Create a copy of the image."""
        img = Image(self.width, self.height, self.colorMode)
        for y in range(self.height):
            for x in range(self.width):
                img._pixels[y][x] = Color(
                    self._pixels[y][x].r,
                    self._pixels[y][x].g,
                    self._pixels[y][x].b,
                    self._pixels[y][x].a
                )
        return img
    
    def drawPixel(self, x: int, y: int, color: int) -> None:
        """Draw a pixel with blending."""
        self.putPixel(x, y, color)
    
    def drawImage(self, src: "Image", x: int, y: int) -> None:
        """Draw another image onto this one."""
        for sy in range(src.height):
            for sx in range(src.width):
                dx, dy = x + sx, y + sy
                if 0 <= dx < self.width and 0 <= dy < self.height:
                    color = src._pixels[sy][sx]
                    if color.a > 0:  # Simple alpha check
                        self._pixels[dy][dx] = color


class Layer:
    """Aseprite Layer class."""
    
    def __init__(self, name: str, sprite: "Sprite"):
        self.name = name
        self.sprite = sprite
        self.parent = None  # Parent layer for grouped layers
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
        self._cels: Dict[int, Image] = {}
    
    def cel(self, frame: int) -> Optional[Image]:
        """Get cel (image) for a frame."""
        return self._cels.get(frame)
    
    def isEmpty(self) -> bool:
        """Check if layer has no cels."""
        return len(self._cels) == 0


class Sprite:
    """Aseprite Sprite class."""
    
    def __init__(self, width: int, height: int, color_mode: ColorMode = ColorMode.RGB):
        self.width = width
        self.height = height
        self.colorMode = color_mode
        self.filename = ""
        self._layers: List[Layer] = []
        self._frames: List["Frame"] = []
        self.palettes: List["Palette"] = []
        self.tags: List["Tag"] = []
        self.slices: List["Slice"] = []
        self.tilesets: List["Tileset"] = []
        self.selection = Selection()
        self.bounds = Rectangle(0, 0, width, height)
        self.isModified = False
        self.properties: Dict[str, Any] = {}
        self._cels: List[Image] = []
        self.undoHistory: List[Any] = []
        
        # Create default layer and frame
        self._add_default_layer_and_frame()
    
    # Make layers list-like for Lua
    @property
    def layers(self):
        return LuaListWrapper(self._layers)
    
    @layers.setter
    def layers(self, value):
        self._layers = value
    
    # Make frames list-like for Lua
    @property
    def frames(self):
        return LuaListWrapper(self._frames)
    
    # Make cels list-like for Lua
    @property
    def cels(self):
        return LuaListWrapper(self._cels)
    
    @cels.setter
    def cels(self, value):
        self._cels = value
    
    @frames.setter
    def frames(self, value):
        self._frames = value
    
    def _add_default_layer_and_frame(self) -> None:
        """Add initial layer and frame."""
        from .frame import Frame
        
        layer = Layer("Layer 1", self)
        self._layers.append(layer)
        
        frame = Frame(1, self)
        self._frames.append(frame)
        
        # Create empty cel and add to sprite's cels list
        cel = Image(self.width, self.height, self.colorMode)
        layer._cels[1] = cel
        self._cels.append(cel)
    
    @property
    def bounds(self) -> Rectangle:
        """Get sprite bounds."""
        return Rectangle(0, 0, self.width, self.height)
    
    @bounds.setter
    def bounds(self, value: Rectangle) -> None:
        """Set sprite bounds (resize)."""
        if isinstance(value, Rectangle):
            self.resize(value.width, value.height)
    
    @property
    def isModified(self) -> bool:
        """Check if sprite has been modified."""
        return False
    
    @isModified.setter
    def isModified(self, value: bool) -> None:
        """Set modified flag."""
        pass
    
    @property
    def properties(self) -> Dict[str, Any]:
        """Get sprite properties."""
        return {}
    
    @properties.setter
    def properties(self, value: Dict[str, Any]) -> None:
        """Set sprite properties."""
        pass
    
    def newLayer(self, name: str) -> Layer:
        """Create a new layer."""
        layer = Layer(name, self)
        self._layers.append(layer)
        return layer
    
    def newSlice(self, x: int = 0, y: int = 0, width: int = 0, height: int = 0) -> Slice:
        """Create a new slice."""
        slice_obj = Slice("Slice", bounds=Rectangle(x, y, width, height), sprite=self)
        self.slices.append(slice_obj)
        return slice_obj
    
    def newFrame(self) -> Frame:
        """Create a new frame."""
        from .frame import Frame
        
        frame_number = len(self._frames) + 1
        frame = Frame(frame_number, self)
        self._frames.append(frame)
        
        # Create empty cels for all layers
        for layer in self._layers:
            if not layer.isGroup:
                layer._cels[frame_number] = Image(self.width, self.height, self.colorMode)
        
        return frame
    
    def flatten(self) -> None:
        """Merge all layers."""
        if len(self.layers) <= 1:
            return
        
        # Create merged image for frame 1
        merged = Image(self.width, self.height, self.colorMode)
        
        # Merge bottom to top
        for layer in reversed(self.layers):
            if layer.isVisible and not layer.isEmpty():
                cel = layer.cel(1)
                if cel:
                    merged.drawImage(cel, 0, 0)
        
        # Replace with single layer
        self.layers.clear()
        layer = Layer("Background", self)
        layer._cels[1] = merged
        self.layers.append(layer)
    
    def resize(self, width: int, height: int) -> None:
        """Resize the sprite."""
        self.width = width
        self.height = height
        
        # Resize all cels
        for layer in self.layers:
            for frame_num, cel in list(layer._cels.items()):
                new_cel = Image(width, height, self.colorMode)
                new_cel.drawImage(cel, 0, 0)
                layer._cels[frame_num] = new_cel
    
    def crop(self, x: int, y: int, width: int, height: int) -> None:
        """Crop the sprite."""
        self.width = width
        self.height = height
        
        # Crop all cels
        for layer in self.layers:
            for frame_num, cel in list(layer._cels.items()):
                new_cel = Image(width, height, self.colorMode)
                new_cel.drawImage(cel, -x, -y)
                layer._cels[frame_num] = new_cel


class Rectangle:
    """Aseprite Rectangle class."""
    
    def __init__(self, x: int = 0, y: int = 0, width: int = 0, height: int = 0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    def __len__(self) -> int:
        return 4
    
    def __getitem__(self, index):
        # Support both integer and string indexing for Lua
        if isinstance(index, int):
            return [self.x, self.y, self.width, self.height][index]
        elif isinstance(index, str):
            return getattr(self, index, None)
        return None
    
    def __setitem__(self, index, value):
        if isinstance(index, str):
            setattr(self, index, value)
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Rectangle):
            return False
        return (self.x == other.x and self.y == other.y and 
                self.width == other.width and self.height == other.height)
    
    def __repr__(self) -> str:
        return f"Rectangle({self.x}, {self.y}, {self.width}, {self.height})"


class Size:
    """Aseprite Size class."""
    
    def __init__(self, width: int = 0, height: int = 0):
        self.width = width
        self.height = height
    
    def __len__(self) -> int:
        return 2
    
    def __getitem__(self, index):
        if isinstance(index, int):
            return [self.width, self.height][index]
        elif isinstance(index, str):
            return getattr(self, index, None)
        return None
    
    def __setitem__(self, index, value):
        if isinstance(index, str):
            setattr(self, index, value)
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Size):
            return False
        return self.width == other.width and self.height == other.height


class Point:
    """Aseprite Point class."""
    
    def __init__(self, x: int = 0, y: int = 0):
        self.x = x
        self.y = y
    
    def __len__(self) -> int:
        return 2
    
    def __getitem__(self, index):
        if isinstance(index, int):
            return [self.x, self.y][index]
        elif isinstance(index, str):
            return getattr(self, index, None)
        return None
    
    def __setitem__(self, index, value):
        if isinstance(index, str):
            setattr(self, index, value)
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Point):
            return False
        return self.x == other.x and self.y == other.y


class Uuid:
    """Aseprite UUID class."""
    
    def __init__(self, value: str = ""):
        self.value = value or self._generate()
    
    def _generate(self) -> str:
        import uuid
        return str(uuid.uuid4())
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Uuid):
            return self.value == other.value
        return self.value == str(other)
    
    def __ne__(self, other) -> bool:
        return not self.__eq__(other)
    
    def __len__(self) -> int:
        return 16
    
    def __getitem__(self, index: int):
        # Return bytes of UUID for indexing
        import uuid
        try:
            u = uuid.UUID(self.value)
            bytes_list = list(u.bytes)
            if 1 <= index <= 16:
                return bytes_list[index - 1]
        except:
            pass
        return None


class Selection:
    """Aseprite Selection class."""
    
    def __init__(self):
        self.isEmpty = True
        self.bounds = Rectangle()
        self.origin = Point()
    
    def select(self, x: int = 0, y: int = 0, width: int = 0, height: int = 0) -> None:
        """Set selection rectangle."""
        self.isEmpty = False
        self.bounds = Rectangle(x, y, width, height)
        self.origin = Point(x, y)
    
    def selectNone(self) -> None:
        """Clear selection."""
        self.isEmpty = True
        self.bounds = Rectangle()
        self.origin = Point()
    
    def contains(self, x: int, y: int) -> bool:
        """Check if point is in selection."""
        if self.isEmpty:
            return True
        return (self.bounds.x <= x < self.bounds.x + self.bounds.width and
                self.bounds.y <= y < self.bounds.y + self.bounds.height)


class Clipboard:
    """Aseprite clipboard API."""
    
    def __init__(self):
        self.image = None
    
    def clear(self) -> None:
        """Clear the clipboard."""
        self.image = None
    
    def setImage(self, image: Image) -> None:
        """Set clipboard image."""
        self.image = image
    
    def getImage(self) -> Optional[Image]:
        """Get clipboard image."""
        return self.image


@dataclass
class Palette:
    """Aseprite Palette class."""
    colors: List[Color] = None
    
    def __post_init__(self):
        if self.colors is None:
            self.colors = []
    
    def __len__(self) -> int:
        return len(self.colors)
    
    def __getitem__(self, index: int) -> Color:
        # Lua uses 1-based indexing
        if isinstance(index, int):
            if index >= 1:
                index -= 1
            if 0 <= index < len(self.colors):
                return self.colors[index]
        return None
    
    def __setitem__(self, index: int, value: Color) -> None:
        if isinstance(index, int):
            if index >= 1:
                index -= 1
            if 0 <= index < len(self.colors):
                self.colors[index] = value
    
    def resize(self, count: int) -> None:
        """Resize palette to have count colors."""
        while len(self.colors) < count:
            self.colors.append(Color())
        self.colors = self.colors[:count]


# Stub classes for Frame, Tag, Slice, Tileset
@dataclass
class Frame:
    """Aseprite Frame class."""
    frameNumber: int
    sprite: Sprite
    duration: int = 100


@dataclass
class Tag:
    """Aseprite Tag class."""
    name: str = ""
    fromFrame: int = 1
    toFrame: int = 1
    color: str = ""
    data: str = ""
    repeats: int = 0
    aniDir: int = 0


@dataclass
class Slice:
    """Aseprite Slice class."""
    name: str = ""
    bounds: Rectangle = None
    center: Rectangle = None
    pivot: Point = None
    sprite: "Sprite" = None
    data: str = ""
    
    def __post_init__(self):
        if self.bounds is None:
            self.bounds = Rectangle()


@dataclass
class Tileset:
    """Aseprite Tileset class."""
    name: str = ""
    grid: Tuple[int, int] = (16, 16)


class Version:
    """Aseprite Version class."""
    
    def __init__(self, version_str: str = ""):
        self._str = version_str or "0.0.0"
        parts = self._str.replace("-dev", "").replace("-beta", ".").replace("-alpha", ".").split(".")
        self.major = int(parts[0]) if parts else 0
        self.minor = int(parts[1]) if len(parts) > 1 else 0
        self.patch = int(parts[2]) if len(parts) > 2 else 0
        self.prereleaseLabel = ""
        self.prereleaseNumber = 0
        
        if "-dev" in self._str:
            self.prereleaseLabel = "dev"
        elif "-beta" in self._str:
            self.prereleaseLabel = "beta"
            if len(parts) > 3:
                self.prereleaseNumber = int(parts[3])
        elif "-alpha" in self._str:
            self.prereleaseLabel = "alpha"
            if len(parts) > 3:
                self.prereleaseNumber = int(parts[3])
    
    def __str__(self) -> str:
        return self._str
    
    def __repr__(self) -> str:
        return f'Version("{self._str}")'
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Version):
            other = Version(str(other))
        return (self.major == other.major and 
                self.minor == other.minor and 
                self.patch == other.patch and
                self.prereleaseLabel == other.prereleaseLabel and
                self.prereleaseNumber == other.prereleaseNumber)
    
    def __lt__(self, other) -> bool:
        if not isinstance(other, Version):
            other = Version(str(other))
        if self.major != other.major:
            return self.major < other.major
        if self.minor != other.minor:
            return self.minor < other.minor
        if self.patch != other.patch:
            return self.patch < other.patch
        # Prerelease comparison
        labels = {"": 3, "dev": 0, "alpha": 1, "beta": 2}
        self_label_val = labels.get(self.prereleaseLabel, 0)
        other_label_val = labels.get(other.prereleaseLabel, 0)
        if self_label_val != other_label_val:
            return self_label_val < other_label_val
        return self.prereleaseNumber < other.prereleaseNumber
    
    def __le__(self, other) -> bool:
        return self == other or self < other
    
    def __gt__(self, other) -> bool:
        return not self <= other
    
    def __ge__(self, other) -> bool:
        return not self < other


class App:
    """Aseprite app API."""
    
    def __init__(self):
        self.sprite: Optional[Sprite] = None
        self.layer: Optional[Layer] = None
        self.frame: Optional[Frame] = None
        self.pixelColor = PixelColor()
        self.activeBrush = Brush()
        self.activeSprite: Optional[Sprite] = None
        self.activeImage: Optional[Image] = None
        self.activeLayer: Optional[Layer] = None
        self.activeFrame: Optional[Frame] = None
        self.site = Site()
        self.preferences = {}
        self._clipboards: List[Image] = []
        self.fs = FileSystem()
        self.command = CommandAPI()
        self.activeTool = "pencil"
        self._version = Version("1.3.0")
        self.clipboard = Clipboard()
        self.params = {}
        self.isUIAvailable = False
        self.events = {}
        self.tool = "pencil"
        self.experimental = {}
        self.undoHistory = []
        self.transaction = False
    
    def Sprite(self, width: int = 0, height: int = 0, color_mode: int = 0) -> Sprite:
        """Create a new sprite."""
        # Handle case where only one arg is passed (square sprite)
        if height == 0 and width != 0:
            height = width
        sprite = Sprite(width, height, ColorMode(color_mode))
        self.sprite = sprite
        self.activeSprite = sprite
        self.layer = sprite.layers[0] if sprite.layers else None
        self.frame = sprite.frames[0] if sprite.frames else None
        self.activeLayer = self.layer
        self.activeFrame = self.frame
        self.site.sprite = sprite
        self.site.layer = self.layer
        self.site.frame = self.frame
        return sprite
    
    def Image(self, width: int, height: int) -> Image:
        """Create a new image."""
        return Image(width, height, ColorMode.RGB)
    
    def Brush(self) -> Brush:
        """Create a new brush."""
        return Brush()
    
    def isTileModeEnabled(self) -> bool:
        """Check if tile mode is enabled."""
        return False
    
    def useTool(self, tool: str) -> None:
        """Set active tool."""
        self.activeTool = tool
    
    def refresh(self) -> None:
        """Refresh UI."""
        pass
    
    def newFile(self, width: int, height: int, color_mode: int = 0) -> Sprite:
        """Create new file."""
        return self.Sprite(width, height, color_mode)
    
    def open(self, filename: str) -> Optional[Sprite]:
        """Open a file."""
        return None
    
    def save(self, filename: Optional[str] = None) -> bool:
        """Save current sprite."""
        return True
    
    def exit(self) -> None:
        """Exit application."""
        pass
    
    def undo(self) -> None:
        """Undo last action."""
        pass
    
    def redo(self) -> None:
        """Redo last undone action."""
        pass
    
    def cut(self) -> None:
        """Cut selection."""
        pass
    
    def copy(self) -> None:
        """Copy selection."""
        pass
    
    def paste(self) -> None:
        """Paste clipboard."""
        pass
    
    def getClipboard(self) -> Optional[Image]:
        """Get image from clipboard."""
        if self._clipboards:
            return self._clipboards[-1]
        return None
    
    def setClipboard(self, image: Image) -> None:
        """Set clipboard image."""
        self._clipboards.append(image)


class BrushType:
    """Brush types."""
    CIRCLE = 0
    SQUARE = 1
    LINE = 2


class Brush:
    """Aseprite Brush class."""
    
    def __init__(self):
        self.size = 1
        self.pattern = None
        self.color = 0
        self.type = BrushType.CIRCLE
        self.angle = 0
        self.center = Point()


class Site:
    """Aseprite Site class (context info)."""
    
    def __init__(self):
        self.sprite: Optional[Sprite] = None
        self.layer: Optional[Layer] = None
        self.frame: Optional[Frame] = None
        self.image: Optional[Image] = None
        self.frameNumber: int = 1
        self.layerIndex: int = 0


class FileSystem:
    """File system operations."""
    
    def __init__(self):
        from os import sep
        self.pathSeparator = sep
    
    def filePath(self, path: str) -> str:
        """Get full file path."""
        return str(Path(path).resolve())
    
    def fileName(self, path: str) -> str:
        """Get file name."""
        return Path(path).name
    
    def filePathSeparator(self) -> str:
        """Get path separator."""
        return self.pathSeparator


class CommandAPI:
    """Command API for executing commands."""
    
    def __init__(self):
        self._commands: Dict[str, Callable] = {
            "NewLayer": self._new_layer,
            "LayerFromBackground": self._layer_from_background,
        }
    
    def execute(self, name: str, params: Optional[Dict] = None) -> bool:
        """Execute a command."""
        if name in self._commands:
            self._commands[name](params or {})
            return True
        return True
    
    def __getattr__(self, name: str) -> Callable:
        """Allow commands to be called as methods."""
        def method(**kwargs):
            return self.execute(name, kwargs)
        return method
    
    def __getitem__(self, name: str) -> Callable:
        """Allow commands to be accessed via subscript."""
        return self.__getattr__(name)
    
    def _new_layer(self, params: Dict) -> None:
        """Create new layer command."""
        pass
    
    def _layer_from_background(self, params: Dict) -> None:
        """Convert background to layer."""
        pass


class AsepriteAPI:
    """Main Aseprite API wrapper for Lua integration."""
    
    def __init__(self):
        self.app = App()
        self.ColorMode = ColorMode
        self.BlendMode = BlendMode
        self._lua: Optional[Any] = None
        self._output: List[str] = []
    
    def create_lua_runtime(self, cwd: Optional[Path] = None) -> Any:
        """Create a Lua runtime with Aseprite API exposed."""
        if not LUPA_AVAILABLE:
            raise RuntimeError("lupa is not installed. Install it with: pip install lupa")
        
        lua = LuaRuntime()
        
        # Expose Aseprite globals
        lua.globals().app = self.app
        lua.globals().ColorMode = self.ColorMode
        lua.globals().BlendMode = self.BlendMode
        
        # Expose classes as constructors using proper functions
        def make_sprite(w=0, h=0, cm=0):
            return self.app.Sprite(w, h, cm)
        
        def make_image(w, h):
            return self.app.Image(w, h)
        
        def make_brush():
            return self.app.Brush()
        
        def make_size(w=0, h=0):
            return Size(w, h)
        
        def make_point(x=0, y=0):
            return Point(x, y)
        
        def make_uuid(v=""):
            return Uuid(v)
        
        def make_version(s=""):
            return Version(s)
        
        def make_color(r=0, g=0, b=0, a=255):
            return Color(r, g, b, a)
        
        lua.globals().Sprite = make_sprite
        lua.globals().Image = make_image
        lua.globals().Brush = make_brush
        lua.globals().Frame = Frame
        lua.globals().Layer = Layer
        lua.globals().Palette = Palette
        lua.globals().Tag = Tag
        lua.globals().Slice = Slice
        lua.globals().Tileset = Tileset
        lua.globals().Selection = Selection
        lua.globals().Rectangle = Rectangle
        lua.globals().Size = make_size
        lua.globals().Point = make_point
        lua.globals().Uuid = make_uuid
        lua.globals().Color = make_color
        lua.globals().BrushType = BrushType
        
        # Add ImageSpec and ColorSpace
        lua.globals().ImageSpec = lambda **kwargs: ImageSpec(**kwargs)
        lua.globals().ColorSpace = lambda name="sRGB": ColorSpace(name)
        lua.globals().ColorSpace.sRGB = ColorSpace.sRGB
        
        # Add version info
        self.app.version = Version("1.3.0")
        lua.globals().Version = make_version
        lua.globals()._G = lua.globals()
        
        # Add json module as an object with functions
        import json as json_module
        
        class JsonModule:
            @staticmethod
            def decode(s):
                return json_module.loads(s)
            @staticmethod
            def encode(obj):
                return json_module.dumps(obj)
        
        lua.globals().json = JsonModule()
        
        # Add missing constants
        lua.globals().GRAY = ColorMode.GRAYSCALE
        lua.globals().RGB = ColorMode.RGB
        lua.globals().INDEXED = ColorMode.INDEXED
        
        # Helper functions
        lua.globals().print = lambda *args: self._output.append(" ".join(str(a) for a in args))
        
        # Expose test utilities
        self._expose_test_utils(lua)
        
        # Set up dofile to work with cwd
        if cwd:
            import lupa
            lua.execute(f'''
                local original_dofile = dofile
                dofile = function(filename)
                    return original_dofile("{str(cwd).replace('\\', '/')}/" .. filename)
                end
            ''')
        
        self._lua = lua
        return lua
    
    def _expose_test_utils(self, lua: Any) -> None:
        """Expose test utility functions."""
        
        def expect_eq(a, b):
            if a != b:
                msg = f"Expected A == B but:\n - Value A = {a}\n - Value B = {b}"
                raise AssertionError(msg)
        
        def expect_clr(color, expected):
            if color != expected:
                pc = self.app.pixelColor
                actual = f"rgba({pc.rgbaR(color)},{pc.rgbaG(color)},{pc.rgbaB(color)},{pc.rgbaA(color)})"
                exp = f"rgba({pc.rgbaR(expected)},{pc.rgbaG(expected)},{pc.rgbaB(expected)},{pc.rgbaA(expected)})"
                raise AssertionError(f"Expected color {exp} but got {actual}")
        
        def expect_img(image, expected_pixels):
            # Check size
            if image.width * image.height != len(expected_pixels):
                raise AssertionError(
                    f"Expected {len(expected_pixels)} pixels but image is {image.width}x{image.height}"
                )
            
            # Check pixels
            for y in range(image.height):
                for x in range(image.width):
                    idx = y * image.width + x
                    actual = image.getPixel(x, y)
                    expected = expected_pixels[idx]
                    if actual != expected:
                        raise AssertionError(
                            f"Pixel ({x}, {y}) mismatch: expected {expected}, got {actual}"
                        )
        
        lua.globals().expect_eq = expect_eq
        lua.globals().expect_clr = expect_clr
        lua.globals().expect_img = expect_img
    
    def run_script(self, source: str, cwd: Optional[Path] = None) -> Dict[str, Any]:
        """Run a Lua script with the Aseprite API."""
        self._output.clear()
        
        lua = self.create_lua_runtime(cwd=cwd)
        
        try:
            result = lua.execute(source)
            return {
                "success": True,
                "result": result,
                "output": "\n".join(self._output)
            }
        except Exception as e:
            import traceback
            return {
                "success": False,
                "error": str(e),
                "output": "\n".join(self._output),
                "traceback": traceback.format_exc()
            }
    
    def run_script_file(self, path: Path) -> Dict[str, Any]:
        """Run a Lua script file."""
        source = path.read_text(encoding="utf-8")
        self._output.append(f"Loading: {path.name}")
        return self.run_script(source, cwd=path.parent)


def run_lua_test(test_path: Path) -> Dict[str, Any]:
    """Run a single Lua test file.
    
    Args:
        test_path: Path to the Lua test file
    
    Returns:
        Dict with success, error, and output
    """
    if not LUPA_AVAILABLE:
        return {
            "success": False,
            "error": "lupa is not installed. Install it with: pip install lupa",
            "output": ""
        }
    
    api = AsepriteAPI()
    result = api.run_script_file(test_path)
    result["file"] = str(test_path)
    return result


def run_all_tests(test_dir: Path) -> List[Dict[str, Any]]:
    """Run all Lua tests in a directory.
    
    Args:
        test_dir: Directory containing Lua test files
    
    Returns:
        List of test results
    """
    results = []
    
    if not test_dir.exists():
        return results
    
    for lua_file in sorted(test_dir.glob("*.lua")):
        result = run_lua_test(lua_file)
        results.append(result)
    
    return results


__all__ = [
    "AsepriteAPI",
    "run_lua_test",
    "run_all_tests",
    "App",
    "Sprite",
    "Image",
    "Layer",
    "Color",
    "ColorMode",
    "BlendMode",
    "PixelColor",
    "Selection",
    "Frame",
    "Palette",
    "Tag",
    "Slice",
    "Tileset",
    "Rectangle",
    "Size",
    "Point",
    "Uuid",
    "Version",
    "Brush",
    "BrushType",
    "Site",
    "FileSystem",
    "CommandAPI",
    "LuaListWrapper",
]
