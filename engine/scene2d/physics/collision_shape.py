# /**************************************************************************/
# /*  collision_shape.py                                                    */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Collision shape node for physics bodies."""

from typing import Optional
from engine.core.nodes2d import Node2D, Vector2


class Shape2D:
    """Base class for 2D collision shapes."""
    
    def __init__(self):
        self._custom_solver_bias: float = 0.0
    
    def set_custom_solver_bias(self, bias: float) -> None:
        self._custom_solver_bias = max(0.0, min(1.0, bias))
    
    def get_custom_solver_bias(self) -> float:
        return self._custom_solver_bias


class WorldBoundaryShape2D(Shape2D):
    """Infinite line collision shape."""
    
    def __init__(self, normal: Vector2 = None, distance: float = 0.0):
        super().__init__()
        self._normal: Vector2 = normal if normal else Vector2(0, -1)
        self._distance: float = distance


class SeparationRayShape2D(Shape2D):
    """Ray for separation detection."""
    
    def __init__(self, length: float = 20.0, slide_on_slope: bool = False):
        super().__init__()
        self._length: float = length
        self._slide_on_slope: bool = slide_on_slope


class SegmentShape2D(Shape2D):
    """Line segment collision shape."""
    
    def __init__(self, a: Vector2 = None, b: Vector2 = None):
        super().__init__()
        self._a: Vector2 = a if a else Vector2()
        self._b: Vector2 = b if b else Vector2(0, 10)


class CircleShape2D(Shape2D):
    """Circle collision shape."""
    
    def __init__(self, radius: float = 10.0):
        super().__init__()
        self._radius: float = radius
    
    def set_radius(self, radius: float) -> None:
        self._radius = max(0.0, radius)
    
    def get_radius(self) -> float:
        return self._radius


class RectangleShape2D(Shape2D):
    """Rectangle collision shape."""
    
    def __init__(self, size: Vector2 = None):
        super().__init__()
        self._size: Vector2 = size if size else Vector2(20, 20)
    
    def set_size(self, size: Vector2) -> None:
        self._size = Vector2(max(0.001, size.x), max(0.001, size.y))
    
    def get_size(self) -> Vector2:
        return self._size


class CapsuleShape2D(Shape2D):
    """Capsule collision shape."""
    
    def __init__(self, radius: float = 10.0, height: float = 20.0):
        super().__init__()
        self._radius: float = radius
        self._height: float = height
    
    def set_radius(self, radius: float) -> None:
        self._radius = max(0.0, radius)
    
    def get_radius(self) -> float:
        return self._radius
    
    def set_height(self, height: float) -> None:
        self._height = max(0.0, height)
    
    def get_height(self) -> float:
        return self._height


class CollisionShape2D(Node2D):
    """Node that holds a collision shape for physics bodies.
    
    Used by StaticBody2D, RigidBody2D, CharacterBody2D, and Area2D.
    """
    
    def __init__(self, name: str = "CollisionShape2D"):
        super().__init__(name)
        self._shape: Optional[Shape2D] = None
        self._disabled: bool = False
        self._one_way_collision: bool = False
        self._one_way_collision_margin: float = 1.0
        self._debug_color = None
    
    def set_shape(self, shape: Optional[Shape2D]) -> None:
        """Set the collision shape resource."""
        self._shape = shape
    
    def get_shape(self) -> Optional[Shape2D]:
        """Get the collision shape resource."""
        return self._shape
    
    def set_disabled(self, disabled: bool) -> None:
        """Enable/disable collision detection."""
        self._disabled = disabled
    
    def is_disabled(self) -> bool:
        return self._disabled
    
    def set_one_way_collision(self, enabled: bool) -> None:
        """Enable one-way collision (objects can pass through from one side)."""
        self._one_way_collision = enabled
    
    def is_one_way_collision_enabled(self) -> bool:
        return self._one_way_collision
    
    def set_one_way_collision_margin(self, margin: float) -> None:
        """Set margin for one-way collision."""
        self._one_way_collision_margin = max(0.0, margin)
    
    def get_one_way_collision_margin(self) -> float:
        return self._one_way_collision_margin
    
    def __repr__(self) -> str:
        return f"CollisionShape2D('{self.name}', shape={self._shape.__class__.__name__ if self._shape else None})"
