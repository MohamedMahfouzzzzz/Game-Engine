# /**************************************************************************/
# /*  collision_shape_2d.py                                                 */
# /**************************************************************************/

"""Godot CollisionShape2D port - 2D collision shape."""

from typing import Optional, List
from engine.core.nodes2d import Node2D
from engine.godot_scene2d.types import Point2, Rect2, Size2


class Shape2D:
    """Base 2D shape."""
    
    def get_rect(self) -> Rect2:
        return Rect2()
    
    def collide(self, with_shape: 'Shape2D', with_transform: any, with_motion: Point2) -> bool:
        return False


class RectangleShape2D(Shape2D):
    """Rectangle collision shape."""
    
    def __init__(self, width: float = 20.0, height: float = 20.0):
        self._size = Size2(width, height)
    
    def set_size(self, size: Size2) -> None:
        self._size = size
    
    def get_size(self) -> Size2:
        return self._size
    
    def get_rect(self) -> Rect2:
        half = Size2(self._size.width / 2, self._size.height / 2)
        return Rect2(Point2(-half.width, -half.height), self._size)


class CircleShape2D(Shape2D):
    """Circle collision shape."""
    
    def __init__(self, radius: float = 10.0):
        self._radius = radius
    
    def set_radius(self, radius: float) -> None:
        self._radius = max(0.0, radius)
    
    def get_radius(self) -> float:
        return self._radius
    
    def get_rect(self) -> Rect2:
        r = self._radius
        return Rect2(Point2(-r, -r), Size2(r * 2, r * 2))


class CapsuleShape2D(Shape2D):
    """Capsule collision shape."""
    
    def __init__(self, radius: float = 10.0, height: float = 20.0):
        self._radius = radius
        self._height = height
    
    def set_radius(self, radius: float) -> None:
        self._radius = max(0.0, radius)
    
    def get_radius(self) -> float:
        return self._radius
    
    def set_height(self, height: float) -> None:
        self._height = max(0.0, height)
    
    def get_height(self) -> float:
        return self._height
    
    def get_rect(self) -> Rect2:
        r = self._radius
        h = self._height
        return Rect2(Point2(-r, -(h/2 + r)), Size2(r * 2, h + r * 2))


class SeparationRayShape2D(Shape2D):
    """Ray collision shape for character controller."""
    
    def __init__(self, length: float = 20.0):
        self._length = length
    
    def set_length(self, length: float) -> None:
        self._length = max(0.0, length)
    
    def get_length(self) -> float:
        return self._length


class WorldBoundaryShape2D(Shape2D):
    """Infinite world boundary."""
    
    def __init__(self, normal: Point2 = None, distance: float = 0.0):
        self._normal = normal if normal else Point2(0, -1)
        self._distance = distance
    
    def set_normal(self, normal: Point2) -> None:
        self._normal = normal.normalized()
    
    def get_normal(self) -> Point2:
        return self._normal
    
    def set_distance(self, distance: float) -> None:
        self._distance = distance
    
    def get_distance(self) -> float:
        return self._distance


class CollisionShape2D(Node2D):
    """Node that provides a collision shape."""
    
    def __init__(self, name: str = "CollisionShape2D"):
        super().__init__(name)
        self._shape: Optional[Shape2D] = None
        self._disabled: bool = False
        self._one_way_collision: bool = False
        self._one_way_collision_margin: float = 1.0
    
    def set_shape(self, shape: Optional[Shape2D]) -> None:
        self._shape = shape
    
    def get_shape(self) -> Optional[Shape2D]:
        return self._shape
    
    def set_disabled(self, disabled: bool) -> None:
        self._disabled = disabled
    
    def is_disabled(self) -> bool:
        return self._disabled
    
    def set_one_way_collision(self, enabled: bool) -> None:
        self._one_way_collision = enabled
    
    def is_one_way_collision_enabled(self) -> bool:
        return self._one_way_collision
    
    def set_one_way_collision_margin(self, margin: float) -> None:
        self._one_way_collision_margin = max(0.0, margin)
    
    def get_one_way_collision_margin(self) -> float:
        return self._one_way_collision_margin
    
    def __repr__(self) -> str:
        return f"CollisionShape2D('{self.name}', shape={type(self._shape).__name__ if self._shape else None}, disabled={self._disabled})"
