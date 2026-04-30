# /**************************************************************************/
# /*  static_body.py                                                        */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Static physics body that doesn't move."""

from engine.scene2d.physics.physics_body import PhysicsBody2D
from engine.core.nodes2d import Vector2


class StaticBody2D(PhysicsBody2D):
    """Static body for walls, floors, and obstacles.
    
    Can be moved programmatically or by animation but behaves
    as immovable object in physics simulation.
    """
    
    def __init__(self, name: str = "StaticBody2D"):
        super().__init__(name)
        self._constant_linear_velocity: Vector2 = Vector2()
        self._constant_angular_velocity: float = 0.0
        self._physics_material_override: any = None
    
    def set_constant_linear_velocity(self, velocity: Vector2) -> None:
        """Set constant linear velocity applied to contacting bodies."""
        self._constant_linear_velocity = velocity
    
    def get_constant_linear_velocity(self) -> Vector2:
        return self._constant_linear_velocity
    
    def set_constant_angular_velocity(self, velocity: float) -> None:
        """Set constant angular velocity applied to contacting bodies."""
        self._constant_angular_velocity = velocity
    
    def get_constant_angular_velocity(self) -> float:
        return self._constant_angular_velocity
    
    def __repr__(self) -> str:
        return f"StaticBody2D('{self.name}')"


class AnimatableBody2D(StaticBody2D):
    """Static body that can be animated.
    
    Behaves as static body in physics simulation but can be moved
    by animation or code. Used for moving platforms.
    """
    
    def __init__(self, name: str = "AnimatableBody2D"):
        super().__init__(name)
        self._sync_to_physics: bool = True
    
    def set_sync_to_physics(self, sync: bool) -> None:
        """Enable synchronization with physics thread."""
        self._sync_to_physics = sync
    
    def is_sync_to_physics_enabled(self) -> bool:
        return self._sync_to_physics
    
    def __repr__(self) -> str:
        return f"AnimatableBody2D('{self.name}')"
