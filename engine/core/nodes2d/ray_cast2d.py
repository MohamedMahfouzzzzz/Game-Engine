# /**************************************************************************/
# /*  ray_cast2d.py                                                         */
# /**************************************************************************/

"""RayCast2D - 2D ray casting for collision detection."""

from __future__ import annotations
from typing import Optional, Any
from .node2d import Node2D
from .types import Vector2
from engine.core.types import NodeType

import logging


logger = logging.getLogger(__name__)



class RayCast2D(Node2D):
    """2D ray casting for collision detection.
    
    Properties:
        enabled: bool - Enable raycasting
        exclude_parent: bool - Exclude parent body
        target_position: Vector2 - Ray target relative to origin
        collision_mask: int - Collision mask
        hit_from_inside: bool - Detect hits from inside colliders
        collide_with_areas: bool - Detect area collisions
        collide_with_bodies: bool - Detect body collisions
    """
    
    __slots__ = [
        "enabled",
        "exclude_parent",
        "target_position",
        "collision_mask",
        "hit_from_inside",
        "collide_with_areas",
        "collide_with_bodies",
        "_collision_result"
    ]
    
    def __init__(self, name: str = "RayCast2D"):
        super().__init__(name)
        self.node_type = NodeType.RAYCAST2D
        
        self.enabled: bool = True
        self.exclude_parent: bool = True
        self.target_position: Vector2 = Vector2(0, 50)
        self.collision_mask: int = 1
        self.hit_from_inside: bool = False
        self.collide_with_areas: bool = False
        self.collide_with_bodies: bool = True
        
        self._collision_result: Optional[dict] = None
    
    def is_colliding(self) -> bool:
        return self._collision_result is not None
    
    def get_collider(self) -> Optional[Any]:
        return self._collision_result.get("collider") if self._collision_result else None
    
    def get_collision_point(self) -> Vector2:
        if self._collision_result:
            pt = self._collision_result.get("point", (0, 0))
            return Vector2(pt[0], pt[1])
        return self.to_global(self.target_position)
    
    def force_raycast_update(self) -> None:
        """Force immediate raycast check."""
        pass


__all__ = ["RayCast2D"]
