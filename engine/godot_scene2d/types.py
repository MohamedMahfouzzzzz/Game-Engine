# /**************************************************************************/
# /*  types.py                                                              */
# /**************************************************************************/

"""Godot-compatible 2D types."""

from enum import IntEnum
from dataclasses import dataclass
from typing import Tuple


class Side(IntEnum):
    SIDE_LEFT = 0
    SIDE_TOP = 1
    SIDE_RIGHT = 2
    SIDE_BOTTOM = 3


class HorizontalAlignment(IntEnum):
    HORIZONTAL_ALIGNMENT_LEFT = 0
    HORIZONTAL_ALIGNMENT_CENTER = 1
    HORIZONTAL_ALIGNMENT_RIGHT = 2


class VerticalAlignment(IntEnum):
    VERTICAL_ALIGNMENT_TOP = 0
    VERTICAL_ALIGNMENT_CENTER = 1
    VERTICAL_ALIGNMENT_BOTTOM = 2


@dataclass
class Point2:
    x: float = 0.0
    y: float = 0.0
    
    def __init__(self, x: float = 0.0, y: float = 0.0):
        self.x = float(x)
        self.y = float(y)
    
    def __add__(self, other: 'Point2') -> 'Point2':
        return Point2(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: 'Point2') -> 'Point2':
        return Point2(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar: float) -> 'Point2':
        return Point2(self.x * scalar, self.y * scalar)
    
    def length(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** 0.5
    
    def length_squared(self) -> float:
        return self.x ** 2 + self.y ** 2
    
    def normalized(self) -> 'Point2':
        length = self.length()
        if length > 0:
            return Point2(self.x / length, self.y / length)
        return Point2()


@dataclass
class Size2:
    width: float = 0.0
    height: float = 0.0
    
    def __init__(self, width: float = 0.0, height: float = 0.0):
        self.width = float(width)
        self.height = float(height)


@dataclass
class Rect2:
    position: Point2 = None
    size: Size2 = None
    
    def __init__(self, position: Point2 = None, size: Size2 = None):
        self.position = position if position else Point2()
        self.size = size if size else Size2()
    
    def get_center(self) -> Point2:
        return Point2(
            self.position.x + self.size.width / 2,
            self.position.y + self.size.height / 2
        )


@dataclass
class Vector2i:
    x: int = 0
    y: int = 0


@dataclass
class Color:
    r: float = 1.0
    g: float = 1.0
    b: float = 1.0
    a: float = 1.0
    
    def __init__(self, r: float = 1.0, g: float = 1.0, b: float = 1.0, a: float = 1.0):
        self.r = float(r)
        self.g = float(g)
        self.b = float(b)
        self.a = float(a)
    
    @staticmethod
    def from_rgba8(r: int, g: int, b: int, a: int = 255) -> 'Color':
        return Color(r / 255.0, g / 255.0, b / 255.0, a / 255.0)
    
    def to_tuple(self) -> Tuple[float, float, float, float]:
        return (self.r, self.g, self.b, self.a)
