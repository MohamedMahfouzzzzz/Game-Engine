# /**************************************************************************/
# /*  shape_cast.py                                                         */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""2D shape casting for sweep collision detection."""

from typing import List, Optional
from engine.core.nodes2d import Node2D, Vector2


class ShapeCast2D(Node2D):
    """Casts a shape along a path to detect collisions.
    
    Useful for sweep testing - e.g., checking if a moving object
    would hit anything along its path.
    """
    
    def __init__(self, name: str = "ShapeCast2D"):
        super().__init__(name)
        self._enabled: bool = True
        self._shape = None
        self._target_position: Vector2 = Vector2(0, 50)
        self._margin: float = 0.0
        self._max_results: int = 32
        self._collision_mask: int = 1
        self._collide_with_areas: bool = False
        self._collide_with_bodies: bool = True
        self._motion: Vector2 = Vector2()
        
        # Results
        self._is_colliding: bool = False
        self._collision_result: List[dict] = []
        self._closest_collision_safe_fraction: float = 1.0
        self._closest_collision_unsafe_fraction: float = 1.0
    
    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled
    
    def is_enabled(self) -> bool:
        return self._enabled
    
    def set_shape(self, shape) -> None:
        """Set the collision shape to cast."""
        self._shape = shape
    
    def get_shape(self):
        return self._shape
    
    def set_target_position(self, position: Vector2) -> None:
        self._target_position = position
    
    def get_target_position(self) -> Vector2:
        return self._target_position
    
    def set_motion(self, motion: Vector2) -> None:
        """Set motion vector for sweep."""
        self._motion = motion
    
    def get_motion(self) -> Vector2:
        return self._motion
    
    def set_margin(self, margin: float) -> None:
        """Set collision margin."""
        self._margin = max(0.0, margin)
    
    def get_margin(self) -> float:
        return self._margin
    
    def set_max_results(self, max_results: int) -> None:
        """Maximum collision results to return."""
        self._max_results = max(1, max_results)
    
    def get_max_results(self) -> int:
        return self._max_results
    
    def set_collision_mask(self, mask: int) -> None:
        self._collision_mask = mask
    
    def get_collision_mask(self) -> int:
        return self._collision_mask
    
    def set_collide_with_areas(self, enabled: bool) -> None:
        self._collide_with_areas = enabled
    
    def is_collide_with_areas_enabled(self) -> bool:
        return self._collide_with_areas
    
    def set_collide_with_bodies(self, enabled: bool) -> None:
        self._collide_with_bodies = enabled
    
    def is_collide_with_bodies_enabled(self) -> bool:
        return self._collide_with_bodies
    
    def is_colliding(self) -> bool:
        return self._is_colliding
    
    def get_closest_collision_safe_fraction(self) -> float:
        """Get fraction of motion before collision."""
        return self._closest_collision_safe_fraction
    
    def get_closest_collision_unsafe_fraction(self) -> float:
        return self._closest_collision_unsafe_fraction
    
    def get_collision_count(self) -> int:
        return len(self._collision_result)
    
    def get_collider(self, index: int = 0) -> Optional['Node2D']:
        if 0 <= index < len(self._collision_result):
            return self._collision_result[index].get('collider')
        return None
    
    def get_collider_id(self, index: int = 0) -> int:
        if 0 <= index < len(self._collision_result):
            return self._collision_result[index].get('collider_id', 0)
        return 0
    
    def get_collision_point(self, index: int = 0) -> Vector2:
        if 0 <= index < len(self._collision_result):
            return self._collision_result[index].get('point', Vector2())
        return Vector2()
    
    def get_collision_normal(self, index: int = 0) -> Vector2:
        if 0 <= index < len(self._collision_result):
            return self._collision_result[index].get('normal', Vector2())
        return Vector2()
    
    def __repr__(self) -> str:
        return f"ShapeCast2D('{self.name}', results={len(self._collision_result)})"
