# /**************************************************************************/
# /*  character_body.py                                                     */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Kinematic character body for platformers and top-down games."""

from enum import IntEnum
from typing import List, Tuple, Optional
from engine.scene2d.physics.physics_body import PhysicsBody2D
from engine.core.nodes2d import Vector2


class PlatformFloorLayers(IntEnum):
    """Default collision layer for floor detection."""
    ALL_LAYERS = 0xFFFFFFFF


class CharacterBody2D(PhysicsBody2D):
    """Kinematic body for characters with platformer logic.
    
    Features:
    - Velocity-based movement with collisions
    - Floor/sliding/snap detection
    - Platformer-specific methods (move_and_slide, is_on_floor, etc.)
    - Up direction configuration
    """
    
    def __init__(self, name: str = "CharacterBody2D"):
        super().__init__(name)
        self._velocity: Vector2 = Vector2()
        self._up_direction: Vector2 = Vector2(0, -1)
        self._floor_stop_on_slope: bool = True
        self._floor_constant_speed: bool = False
        self._floor_block_on_wall: bool = True
        self._floor_max_angle: float = 45.0
        self._floor_snap_length: float = 1.0
        self._platform_on_leave: int = 0
        self._platform_floor_layers: int = PlatformFloorLayers.ALL_LAYERS
        self._platform_wall_layers: int = 1
        self._slide_on_ceiling: bool = True
        self._wall_min_slide_angle: float = 15.0
        self._safe_margin: float = 0.001
        
        # State
        self._on_floor: bool = False
        self._on_ceiling: bool = False
        self._on_wall: bool = False
        self._floor_normal: Vector2 = Vector2()
        self._wall_normal: Vector2 = Vector2()
        self._last_motion: Vector2 = Vector2()
        self._real_velocity: Vector2 = Vector2()
    
    # Velocity
    def set_velocity(self, velocity: Vector2) -> None:
        """Set the body's velocity."""
        self._velocity = velocity
    
    def get_velocity(self) -> Vector2:
        """Get the current velocity."""
        return self._velocity
    
    # Floor detection
    def is_on_floor(self) -> bool:
        """Returns true if the body is on the floor."""
        return self._on_floor
    
    def is_on_ceiling(self) -> bool:
        """Returns true if the body hit the ceiling."""
        return self._on_ceiling
    
    def is_on_wall(self) -> bool:
        """Returns true if the body is touching a wall."""
        return self._on_wall
    
    def is_on_floor_only(self) -> bool:
        """Returns true if only on floor."""
        return self._on_floor and not self._on_ceiling and not self._on_wall
    
    def is_on_wall_only(self) -> bool:
        """Returns true if only on wall."""
        return self._on_wall and not self._on_floor and not self._on_ceiling
    
    def get_floor_normal(self) -> Vector2:
        """Get the normal of the last floor collision."""
        return self._floor_normal
    
    def get_wall_normal(self) -> Vector2:
        """Get the normal of the last wall collision."""
        return self._wall_normal
    
    def get_last_motion(self) -> Vector2:
        """Get the last frame's movement."""
        return self._last_motion
    
    def get_real_velocity(self) -> Vector2:
        """Get the actual movement velocity (may differ from target)."""
        return self._real_velocity
    
    def get_position_delta(self) -> Vector2:
        """Get the position change from last move."""
        return self._last_motion
    
    # Configuration
    def set_up_direction(self, direction: Vector2) -> None:
        """Set which direction is considered 'up' for floor detection."""
        self._up_direction = direction.normalized()
    
    def get_up_direction(self) -> Vector2:
        return self._up_direction
    
    def set_floor_stop_on_slope(self, enabled: bool) -> None:
        """Stop horizontal movement when going downhill."""
        self._floor_stop_on_slope = enabled
    
    def is_floor_stop_on_slope_enabled(self) -> bool:
        return self._floor_stop_on_slope
    
    def set_floor_constant_speed(self, enabled: bool) -> None:
        """Maintain constant speed when going up/down slopes."""
        self._floor_constant_speed = enabled
    
    def is_floor_constant_speed_enabled(self) -> bool:
        return self._floor_constant_speed
    
    def set_floor_block_on_wall(self, enabled: bool) -> None:
        """Enable/disable sliding against walls."""
        self._floor_block_on_wall = enabled
    
    def is_floor_block_on_wall_enabled(self) -> bool:
        return self._floor_block_on_wall
    
    def set_floor_max_angle(self, angle: float) -> None:
        """Maximum angle (in degrees) considered walkable."""
        self._floor_max_angle = max(0, min(180, angle))
    
    def get_floor_max_angle(self) -> float:
        return self._floor_max_angle
    
    def set_floor_snap_length(self, length: float) -> None:
        """Distance to snap down for floor detection."""
        self._floor_snap_length = max(0, length)
    
    def get_floor_snap_length(self) -> float:
        return self._floor_snap_length
    
    def set_slide_on_ceiling(self, enabled: bool) -> None:
        """Enable sliding against ceiling."""
        self._slide_on_ceiling = enabled
    
    def is_slide_on_ceiling_enabled(self) -> bool:
        return self._slide_on_ceiling
    
    def set_wall_min_slide_angle(self, angle: float) -> None:
        """Minimum wall angle for sliding."""
        self._wall_min_slide_angle = angle
    
    def get_wall_min_slide_angle(self) -> float:
        return self._wall_min_slide_angle
    
    def set_safe_margin(self, margin: float) -> None:
        """Safety margin for collision detection."""
        self._safe_margin = max(0, margin)
    
    def get_safe_margin(self) -> float:
        return self._safe_margin
    
    # Movement functions (would be implemented with physics backend)
    def move_and_slide(self) -> int:
        """Move with collision detection and sliding.
        
        Returns: number of collisions.
        """
        # Reset state
        self._on_floor = False
        self._on_ceiling = False
        self._on_wall = False
        
        # Calculate motion
        motion = self._velocity
        self._last_motion = motion
        
        # Check collisions and slide
        # This would integrate with physics backend
        collision_count = 0
        
        # Update position
        if motion.length() > 0:
            self.position = Vector2(
                self.position[0] + motion.x,
                self.position[1] + motion.y
            )
        
        self._real_velocity = motion
        return collision_count
    
    def move_and_collide(self, motion: Vector2, recovery: bool = True) -> Optional[dict]:
        """Move and collide without sliding.
        
        Returns collision info or None.
        """
        # This would integrate with physics backend
        self.position = Vector2(
            self.position[0] + motion.x,
            self.position[1] + motion.y
        )
        self._last_motion = motion
        return None
    
    def apply_floor_snap(self) -> bool:
        """Apply floor snapping for platformer feel."""
        if self._floor_snap_length <= 0:
            return False
        
        # This would integrate with physics backend
        return self._on_floor
    
    def get_platform_velocity(self) -> Vector2:
        """Get velocity of moving platform the body is standing on."""
        return Vector2()
    
    def __repr__(self) -> str:
        return f"CharacterBody2D('{self.name}', velocity={self._velocity})"
