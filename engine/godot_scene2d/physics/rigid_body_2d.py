# /**************************************************************************/
# /*  rigid_body_2d.py                                                      */
# /**************************************************************************/

"""Godot RigidBody2D port - Physics-simulated body."""

from enum import IntEnum
from typing import List, Optional
from engine.godot_scene2d.physics.physics_body_2d import PhysicsBody2D
from engine.godot_scene2d.types import Point2


class RigidBody2DMode(IntEnum):
    MODE_RIGID = 0
    MODE_STATIC = 1
    MODE_CHARACTER = 2
    MODE_KINEMATIC = 3


class RigidBody2D(PhysicsBody2D):
    """Physics body controlled by simulation."""
    
    def __init__(self, name: str = "RigidBody2D"):
        super().__init__(name)
        self._mass: float = 1.0
        self._inertia: float = 1.0
        self._center_of_mass: Point2 = Point2()
        self._center_of_mass_mode: int = 0
        self._angular_velocity: float = 0.0
        self._linear_velocity: Point2 = Point2()
        self._linear_damp: float = 0.0
        self._angular_damp: float = 0.0
        self._linear_damp_mode: int = 0
        self._angular_damp_mode: int = 0
        self._gravity_scale: float = 1.0
        self._mode: RigidBody2DMode = RigidBody2DMode.MODE_RIGID
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
        self._mass = max(0.001, mass)
    
    def get_mass(self) -> float:
        return self._mass
    
    def set_inertia(self, inertia: float) -> None:
        self._inertia = max(0.0, inertia)
    
    def get_inertia(self) -> float:
        return self._inertia
    
    def set_linear_velocity(self, velocity: Point2) -> None:
        self._linear_velocity = velocity
    
    def get_linear_velocity(self) -> Point2:
        return self._linear_velocity
    
    def set_angular_velocity(self, velocity: float) -> None:
        self._angular_velocity = velocity
    
    def get_angular_velocity(self) -> float:
        return self._angular_velocity
    
    def set_gravity_scale(self, scale: float) -> None:
        self._gravity_scale = scale
    
    def get_gravity_scale(self) -> float:
        return self._gravity_scale
    
    def set_linear_damp(self, damp: float) -> None:
        self._linear_damp = max(0.0, damp)
    
    def get_linear_damp(self) -> float:
        return self._linear_damp
    
    def set_angular_damp(self, damp: float) -> None:
        self._angular_damp = max(0.0, damp)
    
    def get_angular_damp(self) -> float:
        return self._angular_damp
    
    def set_mode(self, mode: RigidBody2DMode) -> None:
        self._mode = mode
    
    def get_mode(self) -> RigidBody2DMode:
        return self._mode
    
    def set_sleeping(self, sleeping: bool) -> None:
        self._sleeping = sleeping
    
    def is_sleeping(self) -> bool:
        return self._sleeping
    
    def apply_central_impulse(self, impulse: Point2) -> None:
        self._linear_velocity.x += impulse.x / self._mass
        self._linear_velocity.y += impulse.y / self._mass
    
    def apply_impulse(self, impulse: Point2, position: Point2 = None) -> None:
        self.apply_central_impulse(impulse)
    
    def apply_torque_impulse(self, impulse: float) -> None:
        self._angular_velocity += impulse / self._inertia
    
    def apply_central_force(self, force: Point2) -> None:
        pass
    
    def apply_force(self, force: Point2, position: Point2 = None) -> None:
        pass
    
    def apply_torque(self, torque: float) -> None:
        pass
    
    def __repr__(self) -> str:
        return f"RigidBody2D('{self.name}', mass={self._mass}, velocity={self._linear_velocity}, sleeping={self._sleeping})"
