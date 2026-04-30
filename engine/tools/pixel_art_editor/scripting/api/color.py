# /**************************************************************************/
# /*  api/color.py                                                          */
# /**************************************************************************/

"""Color-related classes for Aseprite API."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import List, Optional

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
        self.r = max(0, min(255, int(self.r)))
        self.g = max(0, min(255, int(self.g)))
        self.b = max(0, min(255, int(self.b)))
        self.a = max(0, min(255, int(self.a)))
        if self.red == 0 and self.r != 0:
            self.red = self.r
        if self.green == 0 and self.g != 0:
            self.green = self.g
        if self.blue == 0 and self.b != 0:
            self.blue = self.b
        if self.alpha == 255 and self.a != 255:
            self.alpha = self.a
        self.red = max(0, min(255, int(self.red)))
        self.green = max(0, min(255, int(self.green)))
        self.blue = max(0, min(255, int(self.blue)))
        self.alpha = max(0, min(255, int(self.alpha)))
    
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
    
    @classmethod
    def rgba(cls, r: int, g: int, b: int, a: int = 255) -> "Color":
        """Create RGBA color."""
        return cls(r, g, b, a)
    
    @classmethod
    def rgb(cls, r: int, g: int, b: int) -> "Color":
        """Create RGB color."""
        return cls(r, g, b, 255)
    
    @classmethod
    def gray(cls, g: int, a: int = 255) -> "Color":
        """Create grayscale color."""
        return cls(g, g, g, a)
    
    @classmethod
    def graya(cls, g: int, a: int) -> "Color":
        """Create grayscale with alpha."""
        return cls(g, g, g, a)
    
    @classmethod
    def indexed(cls, i: int, a: int = 255) -> "Color":
        """Create indexed color."""
        return cls(i, i, i, a)
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Color):
            return False
        return (self.r == other.r and self.g == other.g and 
                self.b == other.b and self.a == other.a)


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
    
    def getColor(self, index: int) -> Color:
        """Get color at index."""
        return self.__getitem__(index)
    
    def setColor(self, index: int, color: Color) -> None:
        """Set color at index."""
        self.__setitem__(index, color)
