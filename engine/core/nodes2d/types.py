# /**************************************************************************/
# /*  nodes2d/types.py                                                      */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Core 2D types - Vector2, Color, Texture2D"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Tuple, Optional
from pathlib import Path

from PySide6.QtGui import QImage

import logging


logger = logging.getLogger(__name__)



class Vector2:
    """2D vector with math operations."""
    
    __slots__ = ["x", "y"]
    
    def __init__(self, x: float = 0, y: float = 0):
        self.x = float(x)
        self.y = float(y)
    
    def __add__(self, other: Vector2) -> Vector2:
        return Vector2(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: Vector2) -> Vector2:
        return Vector2(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar: float) -> Vector2:
        return Vector2(self.x * scalar, self.y * scalar)
    
    def __truediv__(self, scalar: float) -> Vector2:
        return Vector2(self.x / scalar, self.y / scalar)
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Vector2):
            return False
        return self.x == other.x and self.y == other.y
    
    def __repr__(self) -> str:
        return f"Vector2({self.x:.2f}, {self.y:.2f})"
    
    def dot(self, other: Vector2) -> float:
        return self.x * other.x + self.y * other.y
    
    def length(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y)
    
    def normalized(self) -> Vector2:
        length = self.length()
        if length == 0:
            return Vector2(0, 0)
        return Vector2(self.x / length, self.y / length)
    
    def angle(self) -> float:
        return math.atan2(self.y, self.x)
    
    def slide(self, normal: Vector2) -> Vector2:
        """Slide vector along a normal."""
        return self - normal * self.dot(normal)
    
    def lerp(self, target: Vector2, t: float) -> Vector2:
        """Linear interpolate toward target."""
        return Vector2(
            self.x + (target.x - self.x) * t,
            self.y + (target.y - self.y) * t
        )
    
    def copy(self) -> Vector2:
        return Vector2(self.x, self.y)


class Vector2i:
    """Integer 2D vector for grid coordinates."""
    
    __slots__ = ["x", "y"]
    
    def __init__(self, x: int = 0, y: int = 0):
        self.x = int(x)
        self.y = int(y)
    
    def __add__(self, other: Vector2i) -> Vector2i:
        return Vector2i(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: Vector2i) -> Vector2i:
        return Vector2i(self.x - other.x, self.y - other.y)
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Vector2i):
            return False
        return self.x == other.x and self.y == other.y
    
    def __hash__(self) -> int:
        return hash((self.x, self.y))
    
    def __repr__(self) -> str:
        return f"Vector2i({self.x}, {self.y})"


class Color:
    """RGBA color."""
    
    __slots__ = ["r", "g", "b", "a"]
    
    def __init__(self, r: float = 1.0, g: float = 1.0, b: float = 1.0, a: float = 1.0):
        self.r = max(0.0, min(1.0, r))
        self.g = max(0.0, min(1.0, g))
        self.b = max(0.0, min(1.0, b))
        self.a = max(0.0, min(1.0, a))
    
    def to_ints(self) -> tuple:
        """Convert to 0-255 integers."""
        return (
            int(self.r * 255),
            int(self.g * 255),
            int(self.b * 255),
            int(self.a * 255)
        )
    
    @classmethod
    def from_ints(cls, r: int, g: int, b: int, a: int = 255) -> Color:
        return cls(r / 255, g / 255, b / 255, a / 255)
    
    @classmethod
    def white(cls) -> Color:
        return cls(1, 1, 1, 1)
    
    @classmethod
    def black(cls) -> Color:
        return cls(0, 0, 0, 1)
    
    @classmethod
    def red(cls) -> Color:
        return cls(1, 0, 0, 1)
    
    @classmethod
    def green(cls) -> Color:
        return cls(0, 1, 0, 1)
    
    @classmethod
    def blue(cls) -> Color:
        return cls(0, 0, 1, 1)
    
    @classmethod
    def transparent(cls) -> Color:
        return cls(0, 0, 0, 0)


class Texture2D:
    """2D texture with loaded image data."""
    
    __slots__ = ["path", "width", "height", "_loaded", "_image"]
    
    def __init__(self, path: str = "", width: int = 0, height: int = 0):
        self.path = path
        self.width = width
        self.height = height
        self._loaded = False
        self._image: Optional[QImage] = None
    
    def load(self) -> bool:
        """Load texture from disk."""
        if not self.path or not Path(self.path).exists():
            logger.warning("Texture path not found: %s", self.path)
            return False
        try:
            self._image = QImage(str(self.path))
            if self._image.isNull():
                logger.error("Failed to load image: %s", self.path)
                return False
            self.width = self._image.width()
            self.height = self._image.height()
            self._loaded = True
            logger.info("Loaded texture: %s (%dx%d)", self.path, self.width, self.height)
            return True
        except Exception as e:
            logger.error("Error loading texture %s: %s", self.path, e)
            return False
    
    def is_loaded(self) -> bool:
        return self._loaded and self._image is not None and not self._image.isNull()
    
    def get_image(self) -> Optional[QImage]:
        """Get the loaded QImage data."""
        return self._image
    
    def get_sub_image(self, x: int, y: int, w: int, h: int) -> Optional[QImage]:
        """Get a sub-region of the texture as QImage."""
        if not self.is_loaded():
            return None
        return self._image.copy(x, y, w, h)


__all__ = ["Vector2", "Vector2i", "Color", "Texture2D"]
