# /**************************************************************************/
# /*  character_body_2d.py                                                  */
# /**************************************************************************/

"""Godot CharacterBody2D port - Kinematic character controller."""

from typing import List, Optional
from engine.godot_scene2d.physics.physics_body_2d import PhysicsBody2D
from engine.godot_scene2d.types import Point2


class CharacterBody2D(PhysicsBody2D):
    """Kinematic character controller."""
    
    def __init__(self, name: str = "CharacterBody2D"):
        super().__init__(name)
        self._velocity: Point2 = Point2()
        self._slide_on_ceiling: bool = True
        self._floor_max_angle: float = 0.785398  # 45 degrees
        self._floor_snap_length: float = 1.0
        self._floor_stop_on_slope: bool = True
        self._floor_constant_velocity: bool = True
        self._floor_block_on_wall: bool = True
        self._platform_on_leave: int = 0
        self._platform_floor_layers: int = 0xFFFFFFFF
        self._platform_wall_layers: int = 0
        self._motion_mode: int = 0
        self._up_direction: Point2 = Point2(0, -1)
        
        # State
        self._on_floor: bool = False
        self._on_ceiling: bool = False
        self._on_wall: bool = False
        self._floor_normal: Point2 = Point2(0, -1)
        self._platform_velocity: Point2 = Point2()
        self._real_velocity: Point2 = Point2()
    
    def set_velocity(self, velocity: Point2) -> None:
        self._velocity = velocity
    
    def get_velocity(self) -> Point2:
        return self._velocity
    
    def is_on_floor(self) -> bool:
        return self._on_floor
    
    def is_on_ceiling(self) -> bool:
        return self._on_ceiling
    
    def is_on_wall(self) -> bool:
        return self._on_wall
    
    def get_floor_normal(self) -> Point2:
        return self._floor_normal
    
    def get_platform_velocity(self) -> Point2:
        return self._platform_velocity
    
    def get_real_velocity(self) -> Point2:
        return self._real_velocity
    
    def set_floor_max_angle(self, angle: float) -> None:
        self._floor_max_angle = max(0.0, min(1.570796, angle))
    
    def get_floor_max_angle(self) -> float:
        return self._floor_max_angle
    
    def set_up_direction(self, direction: Point2) -> None:
        self._up_direction = direction.normalized() if direction.length() > 0 else Point2(0, -1)
    
    def get_up_direction(self) -> Point2:
        return self._up_direction
    
    def set_floor_stop_on_slope_enabled(self, enabled: bool) -> None:
        self._floor_stop_on_slope = enabled
    
    def is_floor_stop_on_slope_enabled(self) -> bool:
        return self._floor_stop_on_slope
    
    def set_floor_constant_velocity_enabled(self, enabled: bool) -> None:
        self._floor_constant_velocity = enabled
    
    def is_floor_constant_velocity_enabled(self) -> bool:
        return self._floor_constant_velocity
    
    def set_slide_on_ceiling_enabled(self, enabled: bool) -> None:
        self._slide_on_ceiling = enabled
    
    def is_slide_on_ceiling_enabled(self) -> bool:
        return self._slide_on_ceiling
    
    def set_floor_snap_length(self, length: float) -> None:
        self._floor_snap_length = max(0.0, length)
    
    def get_floor_snap_length(self) -> float:
        return self._floor_snap_length
    
    def move_and_slide(self) -> bool:
        """Move body with collision sliding."""
        # Would perform actual collision detection
        old_pos = self.get_position()
        new_pos = Point2(old_pos.x + self._velocity.x, old_pos.y + self._velocity.y)
        self.set_position(new_pos)
        self._real_velocity = Point2(new_pos.x - old_pos.x, new_pos.y - old_pos.y)
        return self._on_floor
    
    def move_and_collide(self, motion: Point2, test_only: bool = False, safe_margin: float = 0.08, recovery_as_collision: bool = False) -> any:
        """Move and detect collision."""
        if not test_only:
            pos = self.get_position()
            self.set_position(Point2(pos.x + motion.x, pos.y + motion.y))
        return None
    
    def get_slide_collision_count(self) -> int:
        return 0
    
    def get_slide_collision(self, index: int) -> any:
        return None
    
    def __repr__(self) -> str:
        return f"CharacterBody2D('{self.name}', on_floor={self._on_floor}, vel={self._velocity})"
