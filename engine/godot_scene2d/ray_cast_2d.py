# /**************************************************************************/
# /*  ray_cast_2d.py                                                        */
# /**************************************************************************/

"""Godot RayCast2D port - 2D ray casting."""

from typing import Optional, List, Callable
from engine.core.nodes2d import Node2D
from engine.godot_scene2d.types import Point2


class RayCast2D(Node2D):
    """2D ray casting for collision detection."""
    
    def __init__(self, name: str = "RayCast2D"):
        super().__init__(name)
        self._enabled: bool = true
        self._target_position: Point2 = Point2(0, 50)
        self._collision_mask: int = 1
        self._hit_from_inside: bool = False
        self._collide_with_areas: bool = False
        self._collide_with_bodies: bool = True
        self._hit: bool = False
        self._collision_point: Point2 = Point2()
        self._collision_normal: Point2 = Point2(0, -1)
        self._collider: Optional[Node2D] = None
        self._collision_rid: any = None
        self._collision_object_id: int = 0
        self._collision_shape: int = 0
    
    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled
    
    def is_enabled(self) -> bool:
        return self._enabled
    
    def set_target_position(self, target_position: Point2) -> None:
        self._target_position = target_position
    
    def get_target_position(self) -> Point2:
        return self._target_position
    
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
    
    def set_hit_from_inside(self, enabled: bool) -> None:
        self._hit_from_inside = enabled
    
    def is_hit_from_inside_enabled(self) -> bool:
        return self._hit_from_inside
    
    def set_collide_with_areas(self, enabled: bool) -> None:
        self._collide_with_areas = enabled
    
    def is_collide_with_areas_enabled(self) -> bool:
        return self._collide_with_areas
    
    def set_collide_with_bodies(self, enabled: bool) -> None:
        self._collide_with_bodies = enabled
    
    def is_collide_with_bodies_enabled(self) -> bool:
        return self._collide_with_bodies
    
    def is_colliding(self) -> bool:
        return self._hit
    
    def get_collider(self) -> Optional[Node2D]:
        return self._collider
    
    def get_collider_rid(self) -> any:
        return self._collision_rid
    
    def get_collision_point(self) -> Point2:
        return self._collision_point
    
    def get_collision_normal(self) -> Point2:
        return self._collision_normal
    
    def get_collision_shape(self) -> int:
        return self._collision_shape
    
    def force_update_shapecast(self) -> None:
        pass
    
    def __repr__(self) -> str:
        return f"RayCast2D('{self.name}', target={self._target_position}, colliding={self._hit})"
