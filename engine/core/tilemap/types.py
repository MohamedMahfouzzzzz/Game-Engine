# /**************************************************************************/
# /*  tilemap/types.py                                                      */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Core types for TileMap system."""

from __future__ import annotations

from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional, List, Tuple

class Direction(Enum):
    """Eight neighboring directions for auto-tiling."""
    TOP_LEFT = auto()
    TOP = auto()
    TOP_RIGHT = auto()
    LEFT = auto()
    RIGHT = auto()
    BOTTOM_LEFT = auto()
    BOTTOM = auto()
    BOTTOM_RIGHT = auto()
    
    @classmethod
    def all_directions(cls) -> list:
        return list(cls)
    
    @property
    def opposite(self) -> Direction:
        opposites = {
            self.TOP_LEFT: self.BOTTOM_RIGHT,
            self.TOP: self.BOTTOM,
            self.TOP_RIGHT: self.BOTTOM_LEFT,
            self.LEFT: self.RIGHT,
            self.RIGHT: self.LEFT,
            self.BOTTOM_LEFT: self.TOP_RIGHT,
            self.BOTTOM: self.TOP,
            self.BOTTOM_RIGHT: self.TOP_LEFT,
        }
        return opposites[self]


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
    
    def __mul__(self, scalar: int) -> Vector2i:
        return Vector2i(self.x * scalar, self.y * scalar)
    
    def __floordiv__(self, scalar: int) -> Vector2i:
        return Vector2i(self.x // scalar, self.y // scalar)
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Vector2i):
            return False
        return self.x == other.x and self.y == other.y
    
    def __hash__(self) -> int:
        return hash((self.x, self.y))
    
    def __repr__(self) -> str:
        return f"Vector2i({self.x}, {self.y})"
    
    @property
    def width(self) -> int:
        return self.x
    
    @property
    def height(self) -> int:
        return self.y


@dataclass
class Rect2i:
    """Integer rectangle for grid regions."""
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0
    
    def contains(self, point: Vector2i) -> bool:
        return (self.x <= point.x < self.x + self.width and
                self.y <= point.y < self.y + self.height)
    
    def intersects(self, other: Rect2i) -> bool:
        return not (self.x + self.width <= other.x or
                   other.x + other.width <= self.x or
                   self.y + self.height <= other.y or
                   other.y + other.height <= self.y)


class Shape2D:
    """Base class for collision shapes."""
    
    def get_bounds(self) -> Tuple[float, float, float, float]:
        """Get AABB (x, y, w, h)."""
        raise NotImplementedError
    
    def test_point(self, point: Tuple[float, float]) -> bool:
        """Test if point is inside."""
        raise NotImplementedError


class RectangleShape2D(Shape2D):
    """Rectangle collision shape."""
    
    def __init__(self, width: float = 0, height: float = 0):
        self.width = width
        self.height = height
    
    def get_bounds(self) -> Tuple[float, float, float, float]:
        return (-self.width/2, -self.height/2, self.width, self.height)
    
    def test_point(self, point: Tuple[float, float]) -> bool:
        x, y = point
        hw, hh = self.width/2, self.height/2
        return abs(x) <= hw and abs(y) <= hh


__all__ = [
    "Direction",
    "Vector2i",
    "Rect2i",
    "Shape2D",
    "RectangleShape2D",
]
