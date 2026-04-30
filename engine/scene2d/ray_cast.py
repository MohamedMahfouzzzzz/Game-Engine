# /**************************************************************************/
# /*  ray_cast.py                                                           */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""2D ray casting node for collision detection."""

from typing import Optional
from engine.core.nodes2d import Node2D, Vector2


class RayCast2D(Node2D):
    """Casts a ray to detect collisions along a line.
    
    Detects collisions with physics bodies and reports the closest collision.
    """
    
    def __init__(self, name: str = "RayCast2D"):
        super().__init__(name)
        self._enabled: bool = True
        self._target_position: Vector2 = Vector2(0, 50)
        self._collide_with_areas: bool = False
        self._collide_with_bodies: bool = True
        self._collision_mask: int = 1
        self._hit_from_inside: bool = False
        
        # Collision results
        self._is_colliding: bool = False
        self._collision_point: Vector2 = Vector2()
        self._collision_normal: Vector2 = Vector2()
        self._collider: Optional['Node2D'] = None
        self._collider_id: int = 0
        self._collision_rid: int = 0
        self._collision_shape: int = 0
        self._collision_local_shape: int = 0
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable/disable ray casting."""
        self._enabled = enabled
    
    def is_enabled(self) -> bool:
        return self._enabled
    
    def set_target_position(self, position: Vector2) -> None:
        """Set ray target in local coordinates."""
        self._target_position = position
    
    def get_target_position(self) -> Vector2:
        return self._target_position
    
    def set_collision_mask(self, mask: int) -> None:
        """Set which collision layers to check."""
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
        """Detect Area2D collisions."""
        self._collide_with_areas = enabled
    
    def is_collide_with_areas_enabled(self) -> bool:
        return self._collide_with_areas
    
    def set_collide_with_bodies(self, enabled: bool) -> None:
        """Detect physics body collisions."""
        self._collide_with_bodies = enabled
    
    def is_collide_with_bodies_enabled(self) -> bool:
        return self._collide_with_bodies
    
    def is_colliding(self) -> bool:
        """Returns true if ray is hitting something."""
        return self._is_colliding
    
    def get_collider(self) -> Optional['Node2D']:
        """Get the collided object."""
        return self._collider
    
    def get_collider_id(self) -> int:
        """Get collider's instance ID."""
        return self._collider_id
    
    def get_collision_point(self) -> Vector2:
        """Get collision point in global coordinates."""
        return self._collision_point
    
    def get_collision_normal(self) -> Vector2:
        """Get collision surface normal."""
        return self._collision_normal
    
    def force_raycast_update(self) -> None:
        """Immediately update collision check."""
        # This would integrate with physics backend
        pass
    
    def __repr__(self) -> str:
        return f"RayCast2D('{self.name}', target=({self._target_position.x}, {self._target_position.y}))"
