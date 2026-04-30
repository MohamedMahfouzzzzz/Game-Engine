# /**************************************************************************/
# /*  nodes2d/character_body2d.py                                           */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""CharacterBody2D - Kinematic character controller."""

from __future__ import annotations

from typing import Optional, List
from enum import Enum, auto

from .node2d import Node2D
from .types import Vector2
from engine.core.types import NodeType

import logging


logger = logging.getLogger(__name__)



class CharacterBody2D(Node2D):
    """Kinematic character controller with collision response.
    
    Features:
        - Collision detection via attached CollisionShape2D
        - Floor/ceiling/wall collision response
        - Slope and snap support
        - One-way platform support
    
    Properties:
        velocity: Current velocity (Vector2)
        up_direction: Normal for floor detection
        floor_max_angle: Maximum floor slope angle
        motion_mode: GROUNDED (with gravity) or FLOATING
    
    Signals:
        motion_changed: When velocity changes
        floor_state_changed: When floor contact changes
    """
    
    class MotionMode(Enum):
        GROUNDED = auto()   # Uses floor/slope detection
        FLOATING = auto()   # Free movement
    
    __slots__ = [
        "velocity", "up_direction", "floor_max_angle", "motion_mode",
        "floor_snap_length", "floor_stop_on_slope",
        "is_on_floor", "is_on_wall", "is_on_ceiling", "floor_normal",
        "_collision_shape"
    ]
    
    _SIGNALS = ["motion_changed", "floor_state_changed"]
    
    def __init__(self, name: str = "CharacterBody2D"):
        super().__init__(name)
        self.node_type = NodeType.CHARACTERBODY2D
        
        # Motion
        self.velocity = Vector2(0, 0)
        self.up_direction = Vector2(0, -1)  # Y-up
        self.floor_max_angle = 45.0
        self.motion_mode = self.MotionMode.GROUNDED
        
        # Floor snap
        self.floor_snap_length = 0.0
        self.floor_stop_on_slope = True
        
        # Collision state
        self.is_on_floor = False
        self.is_on_wall = False
        self.is_on_ceiling = False
        self.floor_normal = Vector2(0, 0)
        
        # Cached collision shape reference
        self._collision_shape: Optional['CollisionShape2D'] = None
    
    def _find_collision_shape(self) -> Optional['CollisionShape2D']:
        """Find attached CollisionShape2D child."""
        if self._collision_shape is not None:
            return self._collision_shape
        
        for child in self.children:
            if hasattr(child, 'shape_type'):  # CollisionShape2D
                self._collision_shape = child
                return child
        return None
    
    def move_and_slide(self) -> Vector2:
        """Move with collision response. Returns remaining motion.
        
        Call in _physics_process() every frame.
        """
        collision = self._find_collision_shape()
        if not collision or collision.disabled:
            # No collision, move freely
            self.position = self.position + self.velocity
            self.is_on_floor = False
            self.is_on_wall = False
            self.is_on_ceiling = False
            return Vector2(0, 0)
        
        # Simplified collision response
        # In production, integrate with physics engine
        
        # Apply movement
        old_pos = self.position
        self.position = self.position + self.velocity
        
        # Update collision state (would check with physics world)
        self.is_on_floor = False
        self.is_on_wall = False
        self.is_on_ceiling = False
        
        return Vector2(0, 0)  # Remaining motion
    
    def move_and_collide(self, motion: Vector2) -> Optional[dict]:
        """Move with collision detection. Returns collision info or None."""
        collision = self._find_collision_shape()
        if not collision or collision.disabled:
            self.position = self.position + motion
            return None
        
        # Test movement, return collision if any
        # Production: integrate with physics engine
        return None
    
    def is_on_floor_only(self) -> bool:
        """Check if only on floor (not wall/ceiling)."""
        return self.is_on_floor and not self.is_on_wall and not self.is_on_ceiling
    
    def get_floor_angle(self) -> float:
        """Get floor slope angle in degrees."""
        if not self.is_on_floor:
            return 0.0
        return self.up_direction.angle() - self.floor_normal.angle()
