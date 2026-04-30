# /**************************************************************************/
# /*  rigid_body.py                                                         */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Rigid body controlled by physics simulation."""

from enum import IntEnum
from typing import List, Optional
from engine.scene2d.physics.physics_body import PhysicsBody2D
from engine.core.nodes2d import Vector2


class RigidBody2DMode(IntEnum):
    """Physics simulation modes for rigid body."""
    RIGID = 0
    STATIC = 1
    CHARACTER = 2
    KINEMATIC = 3


class RigidBody2D(PhysicsBody2D):
    """Physics body controlled by physics simulation.
    
    Supports multiple modes: rigid, static, character, kinematic.
    Features mass, inertia, damping, forces, and collision reporting.
    """
    
    def __init__(self, name: str = "RigidBody2D"):
        super().__init__(name)
        self._mass: float = 1.0
        self._inertia: float = 1.0
        self._center_of_mass: Vector2 = Vector2()
        self._center_of_mass_mode: int = 0
        self._angular_velocity: float = 0.0
        self._linear_velocity: Vector2 = Vector2()
        self._linear_damp: float = 0.0
        self._angular_damp: float = 0.0
        self._linear_damp_mode: int = 0
        self._angular_damp_mode: int = 0
        self._gravity_scale: float = 1.0
        self._mode: RigidBody2DMode = RigidBody2DMode.RIGID
        self._sleeping: bool = False
        self._can_sleep: bool = True
        self._lock_rotation: bool = False
        self._freeze: bool = False
        self._freeze_mode: int = 0
        self._continuous_cd: int = 0
        self._max_contacts_reported: int = 0
        self._contact_monitor: bool = False
        self._contact_count: int = 0
        self._contacts: List[dict] = []
    
    def set_mass(self, mass: float) -> None:
        """Set body mass (minimum 0.001)."""
        self._mass = max(0.001, mass)
    
    def get_mass(self) -> float:
        return self._mass
    
    def set_inertia(self, inertia: float) -> None:
        """Set moment of inertia."""
        self._inertia = max(0.0, inertia)
    
    def get_inertia(self) -> float:
        return self._inertia
    
    def set_linear_velocity(self, velocity: Vector2) -> None:
        """Set linear velocity."""
        self._linear_velocity = velocity
    
    def get_linear_velocity(self) -> Vector2:
        return self._linear_velocity
    
    def set_angular_velocity(self, velocity: float) -> None:
        """Set angular velocity in degrees/sec."""
        self._angular_velocity = velocity
    
    def get_angular_velocity(self) -> float:
        return self._angular_velocity
    
    def set_gravity_scale(self, scale: float) -> None:
        """Set gravity multiplier."""
        self._gravity_scale = scale
    
    def get_gravity_scale(self) -> float:
        return self._gravity_scale
    
    def set_linear_damp(self, damp: float) -> None:
        """Set linear damping."""
        self._linear_damp = max(0.0, damp)
    
    def get_linear_damp(self) -> float:
        return self._linear_damp
    
    def set_angular_damp(self, damp: float) -> None:
        """Set angular damping."""
        self._angular_damp = max(0.0, damp)
    
    def get_angular_damp(self) -> float:
        return self._angular_damp
    
    def set_mode(self, mode: RigidBody2DMode) -> None:
        """Set physics simulation mode."""
        self._mode = mode
    
    def get_mode(self) -> RigidBody2DMode:
        return self._mode
    
    def set_sleeping(self, sleeping: bool) -> None:
        """Put body to sleep or wake up."""
        self._sleeping = sleeping
    
    def is_sleeping(self) -> bool:
        return self._sleeping
    
    def set_can_sleep(self, can_sleep: bool) -> None:
        """Allow body to enter sleep state."""
        self._can_sleep = can_sleep
    
    def is_able_to_sleep(self) -> bool:
        return self._can_sleep
    
    def set_lock_rotation(self, lock: bool) -> None:
        """Prevent rotation."""
        self._lock_rotation = lock
    
    def is_rotation_locked(self) -> bool:
        return self._lock_rotation
    
    def set_freeze(self, freeze: bool) -> None:
        """Freeze body in place."""
        self._freeze = freeze
    
    def is_frozen(self) -> bool:
        return self._freeze
    
    def apply_central_impulse(self, impulse: Vector2) -> None:
        """Apply impulse to center of mass."""
        if self._mass > 0:
            self._linear_velocity += impulse / self._mass
    
    def apply_torque_impulse(self, torque: float) -> None:
        """Apply rotational impulse."""
        if self._inertia > 0:
            self._angular_velocity += torque / self._inertia
    
    def apply_impulse(self, impulse: Vector2, position: Vector2) -> None:
        """Apply impulse at specific position."""
        self.apply_central_impulse(impulse)
        # Torque = r x F
        offset = position - self.position
        torque = offset.x * impulse.y - offset.y * impulse.x
        self.apply_torque_impulse(torque)
    
    def apply_force(self, force: Vector2) -> None:
        """Apply continuous force."""
        # Acceleration = F / m
        if self._mass > 0:
            self._linear_velocity += force / self._mass
    
    def apply_torque(self, torque: float) -> None:
        """Apply continuous torque."""
        if self._inertia > 0:
            self._angular_velocity += torque / self._inertia
    
    def get_colliding_bodies(self) -> List['RigidBody2D']:
        """Get list of colliding bodies."""
        return []
    
    def __repr__(self) -> str:
        return f"RigidBody2D('{self.name}', mass={self._mass})"
