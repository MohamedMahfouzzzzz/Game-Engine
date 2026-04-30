# /**************************************************************************/
# /*  static_body_2d.py                                                     */
# /**************************************************************************/

"""Godot StaticBody2D port - Static physics body."""

from engine.godot_scene2d.physics.physics_body_2d import PhysicsBody2D
from engine.godot_scene2d.types import Point2


class StaticBody2D(PhysicsBody2D):
    """Static body that doesn't move.
    
    Used for walls, floors, and obstacles.
    """
    
    def __init__(self, name: str = "StaticBody2D"):
        super().__init__(name)
        self._constant_linear_velocity: Point2 = Point2()
        self._constant_angular_velocity: float = 0.0
        self._physics_material_override: any = None
    
    def set_constant_linear_velocity(self, velocity: Point2) -> None:
        self._constant_linear_velocity = velocity
    
    def get_constant_linear_velocity(self) -> Point2:
        return self._constant_linear_velocity
    
    def set_constant_angular_velocity(self, velocity: float) -> None:
        self._constant_angular_velocity = velocity
    
    def get_constant_angular_velocity(self) -> float:
        return self._constant_angular_velocity
    
    def __repr__(self) -> str:
        return f"StaticBody2D('{self.name}')"


class AnimatableBody2D(StaticBody2D):
    """Static body that can be animated.
    
    Can be moved by animation but behaves as static otherwise.
    """
    
    def __init__(self, name: str = "AnimatableBody2D"):
        super().__init__(name)
        self._sync_to_physics: bool = true
    
    def set_sync_to_physics(self, sync: bool) -> None:
        self._sync_to_physics = sync
    
    def is_sync_to_physics_enabled(self) -> bool:
        return self._sync_to_physics
    
    def __repr__(self) -> str:
        return f"AnimatableBody2D('{self.name}')"
