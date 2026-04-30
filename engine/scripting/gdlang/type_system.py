# /**************************************************************************/
# /*  type_system.py                                                        */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""GDScript-compatible type system for GDLang.

This module implements all built-in GDScript types and their operations,
designed for direct compatibility with GDScript code.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable


# ============================================================================
# 2D Types
# ============================================================================

@dataclass
class Vector2:
    """2D vector with float components."""
    x: float = 0.0
    y: float = 0.0
    
    def __add__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x + other.x, self.y + other.y)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x - other.x, self.y - other.y)
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Vector2(self.x * other, self.y * other)
        if isinstance(other, Vector2):
            return Vector2(self.x * other.x, self.y * other.y)
        return NotImplemented
    
    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return Vector2(self.x / other, self.y / other)
        if isinstance(other, Vector2):
            return Vector2(self.x / other.x, self.y / other.y)
        return NotImplemented
    
    def __neg__(self):
        return Vector2(-self.x, -self.y)
    
    def __eq__(self, other):
        if isinstance(other, Vector2):
            return math.isclose(self.x, other.x) and math.isclose(self.y, other.y)
        return False
    
    def __repr__(self):
        return f"({self.x}, {self.y})"

    def length(self) -> float:
        return math.hypot(self.x, self.y)
    
    def length_squared(self) -> float:
        return self.x * self.x + self.y * self.y
        
    def normalized(self):
        l = self.length()
        if l == 0:
            return Vector2(0, 0)
        return Vector2(self.x / l, self.y / l)
    
    def dot(self, other: Vector2) -> float:
        return self.x * other.x + self.y * other.y
    
    def cross(self, other: Vector2) -> float:
        return self.x * other.y - self.y * other.x
    
    def distance_to(self, other: Vector2) -> float:
        return (self - other).length()
    
    def distance_squared_to(self, other: Vector2) -> float:
        return (self - other).length_squared()
    
    def angle(self) -> float:
        return math.atan2(self.y, self.x)
    
    def angle_to(self, other: Vector2) -> float:
        return math.atan2(self.cross(other), self.dot(other))
    
    def rotated(self, angle: float):
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return Vector2(
            self.x * cos_a - self.y * sin_a,
            self.x * sin_a + self.y * cos_a
        )
    
    def lerp(self, to: Vector2, weight: float):
        return Vector2(
            self.x + (to.x - self.x) * weight,
            self.y + (to.y - self.y) * weight
        )
    
    def floor(self):
        return Vector2i(int(math.floor(self.x)), int(math.floor(self.y)))
    
    def ceil(self):
        return Vector2i(int(math.ceil(self.x)), int(math.ceil(self.y)))
    
    def round(self):
        return Vector2i(round(self.x), round(self.y))


@dataclass
class Vector2i:
    """2D vector with integer components."""
    x: int = 0
    y: int = 0
    
    def __add__(self, other):
        if isinstance(other, Vector2i):
            return Vector2i(self.x + other.x, self.y + other.y)
        if isinstance(other, Vector2):
            return Vector2(self.x + other.x, self.y + other.y)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Vector2i):
            return Vector2i(self.x - other.x, self.y - other.y)
        if isinstance(other, Vector2):
            return Vector2(self.x - other.x, self.y - other.y)
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, int):
            return Vector2i(self.x * other, self.y * other)
        if isinstance(other, Vector2i):
            return Vector2i(self.x * other.x, self.y * other.y)
        return NotImplemented
    
    def __truediv__(self, other):
        if isinstance(other, int):
            return Vector2(self.x / other, self.y / other)
        return NotImplemented
    
    def __eq__(self, other):
        if isinstance(other, Vector2i):
            return self.x == other.x and self.y == other.y
        return False
    
    def __repr__(self):
        return f"({self.x}, {self.y})"
    
    def length(self) -> float:
        return math.hypot(self.x, self.y)
    
    def length_squared(self) -> int:
        return self.x * self.x + self.y * self.y

# ============================================================================
# Rectangle Types
# ============================================================================

@dataclass
class Rect2:
    """2D axis-aligned bounding box using position and size."""
    position: Vector2 = field(default_factory=Vector2)
    size: Vector2 = field(default_factory=Vector2)
    
    @property
    def end(self) -> Vector2:
        return Vector2(self.position.x + self.size.x, self.position.y + self.size.y)
    
    @property
    def center(self) -> Vector2:
        return Vector2(
            self.position.x + self.size.x / 2,
            self.position.y + self.size.y / 2
        )
    
    def has_point(self, point: Vector2) -> bool:
        return (self.position.x <= point.x < self.end.x and
                self.position.y <= point.y < self.end.y)
    
    def intersects(self, other: Rect2) -> bool:
        return (self.position.x < other.end.x and self.end.x > other.position.x and
                self.position.y < other.end.y and self.end.y > other.position.y)
    
    def merge(self, other: Rect2):
        x = min(self.position.x, other.position.x)
        y = min(self.position.y, other.position.y)
        end_x = max(self.end.x, other.end.x)
        end_y = max(self.end.y, other.end.y)
        return Rect2(Vector2(x, y), Vector2(end_x - x, end_y - y))


@dataclass
class Rect2i:
    """Integer version of Rect2."""
    position: Vector2i = field(default_factory=Vector2i)
    size: Vector2i = field(default_factory=Vector2i)


# ============================================================================
# Color Type
# ============================================================================

@dataclass
class Color:
    """Color with RGBA components (0.0 to 1.0)."""
    r: float = 1.0
    g: float = 1.0
    b: float = 1.0
    a: float = 1.0
    
    @staticmethod
    def from_rgb(r: int, g: int, b: int) -> Color:
        return Color(r / 255.0, g / 255.0, b / 255.0, 1.0)
    
    @staticmethod
    def from_rgba(r: int, g: int, b: int, a: int) -> Color:
        return Color(r / 255.0, g / 255.0, b / 255.0, a / 255.0)
    
    @staticmethod
    def from_hex(hex_code: str) -> Color:
        hex_code = hex_code.lstrip('#')
        if len(hex_code) == 6:
            r = int(hex_code[0:2], 16) / 255.0
            g = int(hex_code[2:4], 16) / 255.0
            b = int(hex_code[4:6], 16) / 255.0
            return Color(r, g, b, 1.0)
        elif len(hex_code) == 8:
            r = int(hex_code[0:2], 16) / 255.0
            g = int(hex_code[2:4], 16) / 255.0
            b = int(hex_code[4:6], 16) / 255.0
            a = int(hex_code[6:8], 16) / 255.0
            return Color(r, g, b, a)
        return Color(1, 1, 1, 1)
    
    def to_rgba32(self) -> int:
        return ((int(self.r * 255) << 24) | 
                (int(self.g * 255) << 16) | 
                (int(self.b * 255) << 8) | 
                int(self.a * 255))
    
    def lerp(self, to: Color, weight: float):
        return Color(
            self.r + (to.r - self.r) * weight,
            self.g + (to.g - self.g) * weight,
            self.b + (to.b - self.b) * weight,
            self.a + (to.a - self.a) * weight
        )
    
    def __mul__(self, other):
        if isinstance(other, Color):
            return Color(self.r * other.r, self.g * other.g, 
                        self.b * other.b, self.a * other.a)
        if isinstance(other, (int, float)):
            return Color(self.r * other, self.g * other, 
                        self.b * other, self.a * other)
        return NotImplemented


# ============================================================================
# Transform Types
# ============================================================================

@dataclass
class Transform2D:
    """2D transformation matrix."""
    x: Vector2 = field(default_factory=lambda: Vector2(1, 0))
    y: Vector2 = field(default_factory=lambda: Vector2(0, 1))
    origin: Vector2 = field(default_factory=Vector2)
    
    def basis_xform(self, v: Vector2) -> Vector2:
        return Vector2(self.x.x * v.x + self.y.x * v.y,
                      self.x.y * v.x + self.y.y * v.y)
    
    def origin_xform(self, v: Vector2) -> Vector2:
        return self.basis_xform(v) + self.origin


# ============================================================================
# Array Types (GDScript typed arrays)
# ============================================================================

class Array(list):
    """GDScript-compatible Array with type hints."""
    
    def __init__(self, items=None, typed_type=None):
        super().__init__(items or [])
        self.typed_type = typed_type
    
    def append(self, item) -> None:
        if self.typed_type and not isinstance(item, self.typed_type):
            raise TypeError(f"Expected {self.typed_type}, got {type(item)}")
        super().append(item)
    
    def size(self) -> int:
        return len(self)
    
    def is_empty(self) -> bool:
        return len(self) == 0
    
    def front(self):
        return self[0] if self else None
    
    def back(self):
        return self[-1] if self else None
    
    def has(self, item) -> bool:
        return item in self


class Dict(dict):
    """GDScript-compatible Dictionary."""
    
    def has(self, key) -> bool:
        return key in self
    
    def size(self) -> int:
        return len(self)
    
    def is_empty(self) -> bool:
        return len(self) == 0
    
    def keys_array(self) -> list:
        return list(self.keys())
    
    def values_array(self) -> list:
        return list(self.values())


# ============================================================================
# String Types
# ============================================================================

class StringName(str):
    """GDScript StringName - immutable, interned string for fast comparison."""
    _interned: Dict[str, StringName] = {}
    
    def __new__(cls, value: str):
        if value in cls._interned:
            return cls._interned[value]
        instance = super().__new__(cls, value)
        cls._interned[value] = instance
        return instance


class NodePath(str):
    """GDScript NodePath - pre-parsed node path string."""
    
    def get_name(self, idx: int) -> str:
        parts = self.split('/')
        return parts[idx] if 0 <= idx < len(parts) else ""
    
    def get_name_count(self) -> int:
        return len(self.split('/')) if self else 0
    
    def is_absolute(self) -> bool:
        return self.startswith('/') if self else False


# ============================================================================
# Callable Type
# ============================================================================

@dataclass
class Callable:
    """GDScript Callable - stores a function reference."""
    target: Any
    method: str
    
    def call(self, *args):
        method = getattr(self.target, self.method)
        return method(*args)
    
    def is_valid(self) -> bool:
        return hasattr(self.target, self.method)


# ============================================================================
# Signal Type
# ============================================================================

class Signal:
    """GDScript Signal - for event dispatching."""
    
    def __init__(self, name: str = ""):
        self.name = name
        self.connections: List[tuple] = []  # (target, method, binds)
    
    def connect(self, callable: Callable, binds: List = None):
        self.connections.append((callable, binds or []))
    
    def disconnect(self, callable: Callable):
        self.connections = [(c, b) for c, b in self.connections if c != callable]
    
    def emit(self, *args):
        for callable, binds in self.connections:
            callable.call(*(args + tuple(binds)))
    
    def is_connected(self, callable: Callable) -> bool:
        return any(c == callable for c, _ in self.connections)


# ============================================================================
# Packed Arrays (GDScript typed packed arrays)
# ============================================================================

class PackedByteArray(bytearray):
    """Packed array of bytes."""
    
    def size(self) -> int:
        return len(self)


class PackedInt32Array(list):
    """Packed array of 32-bit integers."""
    
    def __init__(self, items=None):
        super().__init__(items or [])
    
    def size(self) -> int:
        return len(self)


class PackedFloat32Array(list):
    """Packed array of 32-bit floats."""
    
    def __init__(self, items=None):
        super().__init__(items or [])
    
    def size(self) -> int:
        return len(self)


class PackedStringArray(list):
    """Packed array of strings."""
    
    def __init__(self, items=None):
        super().__init__(items or [])
    
    def size(self) -> int:
        return len(self)


class PackedVector2Array(list):
    """Packed array of Vector2."""
    
    def __init__(self, items=None):
        super().__init__(items or [])
    
    def size(self) -> int:
        return len(self)


class PackedColorArray(list):
    """Packed array of Color."""
    
    def __init__(self, items=None):
        super().__init__(items or [])
    
    def size(self) -> int:
        return len(self)


# ============================================================================
# RID (Resource ID)
# ============================================================================

@dataclass
class RID:
    """Resource ID for referencing server-side objects."""
    _id: int
    
    def get_id(self) -> int:
        return self._id
    
    def is_valid(self) -> bool:
        return self._id > 0
