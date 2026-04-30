# /**************************************************************************/
# /*  shape_cast_2d.py                                                      */
# /**************************************************************************/

"""Godot ShapeCast2D port - 2D shape casting."""

from typing import List, Optional, Dict
from engine.core.nodes2d import Node2D
from engine.godot_scene2d.types import Point2
from engine.godot_scene2d.physics.collision_shape_2d import Shape2D


class ShapeCast2D(Node2D):
    """Cast a shape along a ray for collision detection."""
    
    def __init__(self, name: str = "ShapeCast2D"):
        super().__init__(name)
        self._enabled: bool = True
        self._shape: Optional[Shape2D] = None
        self._target_position: Point2 = Point2(0, 50)
        self._margin: float = 0.0
        self._collision_mask: int = 1
        self._collide_with_areas: bool = False
        self._collide_with_bodies: bool = True
        self._max_results: int = 32
        
        self._result: List[Dict] = []
        self._motion: Point2 = Point2()
        self._exclude: List[any] = []
    
    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled
    
    def is_enabled(self) -> bool:
        return self._enabled
    
    def set_shape(self, shape: Optional[Shape2D]) -> None:
        self._shape = shape
    
    def get_shape(self) -> Optional[Shape2D]:
        return self._shape
    
    def set_target_position(self, target_position: Point2) -> None:
        self._target_position = target_position
    
    def get_target_position(self) -> Point2:
        return self._target_position
    
    def set_margin(self, margin: float) -> None:
        self._margin = max(0.0, margin)
    
    def get_margin(self) -> float:
        return self._margin
    
    def set_max_results(self, max_results: int) -> None:
        self._max_results = max(1, max_results)
    
    def get_max_results(self) -> int:
        return self._max_results
    
    def set_collision_mask(self, mask: int) -> None:
        self._collision_mask = mask
    
    def get_collision_mask(self) -> int:
        return self._collision_mask
    
    def set_collision_mask_bit(self, bit: int, value: bool) -> None:
        if value:
            self._collision_mask |= (1 << bit)
        else:
            self._collision_mask &= ~(1 << bit)
    
    def get_collision_mask_bit(self, bit: int) -> bool:
        return (self._collision_mask & (1 << bit)) != 0
    
    def set_collide_with_areas(self, enabled: bool) -> None:
        self._collide_with_areas = enabled
    
    def is_collide_with_areas_enabled(self) -> bool:
        return self._collide_with_areas
    
    def set_collide_with_bodies(self, enabled: bool) -> None:
        self._collide_with_bodies = enabled
    
    def is_collide_with_bodies_enabled(self) -> bool:
        return self._collide_with_bodies
    
    def is_colliding(self) -> bool:
        return len(self._result) > 0
    
    def get_collision_count(self) -> int:
        return len(self._result)
    
    def get_collider(self, index: int = 0) -> Optional[Node2D]:
        if 0 <= index < len(self._result):
            return self._result[index].get("collider")
        return None
    
    def get_collider_rid(self, index: int = 0) -> any:
        if 0 <= index < len(self._result):
            return self._result[index].get("rid")
        return None
    
    def get_collider_shape(self, index: int = 0) -> int:
        if 0 <= index < len(self._result):
            return self._result[index].get("shape", 0)
        return 0
    
    def get_collision_point(self, index: int = 0) -> Point2:
        if 0 <= index < len(self._result):
            return self._result[index].get("point", Point2())
        return Point2()
    
    def get_collision_normal(self, index: int = 0) -> Point2:
        if 0 <= index < len(self._result):
            return self._result[index].get("normal", Point2(0, -1))
        return Point2(0, -1)
    
    def get_closest_collision_safe_fraction(self) -> float:
        if self._result:
            return min(r.get("safe_fraction", 1.0) for r in self._result)
        return 1.0
    
    def get_closest_collision_unsafe_fraction(self) -> float:
        if self._result:
            return min(r.get("unsafe_fraction", 1.0) for r in self._result)
        return 1.0
    
    def add_exception(self, obj: any) -> None:
        self._exclude.append(obj)
    
    def remove_exception(self, obj: any) -> None:
        if obj in self._exclude:
            self._exclude.remove(obj)
    
    def __repr__(self) -> str:
        return f"ShapeCast2D('{self.name}', shape={type(self._shape).__name__ if self._shape else None}, hits={len(self._result)})"
