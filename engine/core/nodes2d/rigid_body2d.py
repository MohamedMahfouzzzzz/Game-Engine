# /**************************************************************************/
# /*  rigid_body2d.py                                                       */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""RigidBody2D - Dynamic physics body with mass and forces."""

from __future__ import annotations

from typing import Optional
from enum import IntEnum

from .node2d import Node2D
from .types import Vector2
from engine.core.types import NodeType

import logging


logger = logging.getLogger(__name__)



class PhysicsMaterial:
    """Physics material with friction and bounce."""
    
    def __init__(self):
        self.friction: float = 1.0
        self.rough: bool = False
        self.bounce: float = 0.0
        self.absorbent: bool = False


class RigidBody2D(Node2D):
    """Dynamic physics body with mass and forces.
    
    Properties:
        mass: Body mass in kg (float)
        physics_material_override: PhysicsMaterial override
        gravity_scale: Gravity multiplier (float)
        center_of_mass_mode: 0=CENTER_OF_MASS_MODE_AUTO, 1=CENTER_OF_MASS_MODE_CUSTOM
        center_of_mass: Custom center of mass offset (Vector2)
        linear_velocity: Current linear velocity (Vector2)
        angular_velocity: Current angular velocity in rad/s (float)
        linear_damp_mode: 0=DAMP_MODE_COMBINE, 1=DAMP_MODE_REPLACE
        linear_damp: Linear damping (float)
        angular_damp_mode: 0=DAMP_MODE_COMBINE, 1=DAMP_MODE_REPLACE
        angular_damp: Angular damping (float)
        constant_force: Constant force applied (Vector2)
        constant_torque: Constant torque applied (float)
        body_mode: 0=MODE_RIGID, 1=MODE_STATIC, 2=MODE_CHARACTER, 3=MODE_KINEMATIC
        lock_rotation: Prevent rotation (bool)
        freeze: Freeze body in place (bool)
        freeze_mode: 0=FREEZE_MODE_STATIC, 1=FREEZE_MODE_KINEMATIC
        continuous_cd: 0=CCD_DISABLED, 1=CCD_MODE_CAST_RAY, 2=CCD_MODE_CAST_SHAPE
        contact_monitor: Enable contact reporting (bool)
        max_contacts_reported: Max contacts to report (int)
    
    Signals:
        body_entered(body: Node)
        body_exited(body: Node)
        body_shape_entered(body_rid: RID, body: Node, body_shape_index: int, local_shape_index: int)
        body_shape_exited(body_rid: RID, body: Node, body_shape_index: int, local_shape_index: int)
        sleeping_state_changed
    """
    
    class Mode(IntEnum):
        RIGID = 0
        STATIC = 1
        CHARACTER = 2
        KINEMATIC = 3
    
    class FreezeMode(IntEnum):
        STATIC = 0
        KINEMATIC = 1
    
    class DampMode(IntEnum):
        COMBINE = 0
        REPLACE = 1
    
    class CenterOfMassMode(IntEnum):
        AUTO = 0
        CUSTOM = 1
    
    class CCDMode(IntEnum):
        DISABLED = 0
        CAST_RAY = 1
        CAST_SHAPE = 2
    
    __slots__ = [
        "mass",
        "physics_material_override",
        "gravity_scale",
        "center_of_mass_mode",
        "center_of_mass",
        "linear_velocity",
        "angular_velocity",
        "linear_damp_mode",
        "linear_damp",
        "angular_damp_mode",
        "angular_damp",
        "constant_force",
        "constant_torque",
        "body_mode",
        "lock_rotation",
        "freeze",
        "freeze_mode",
        "continuous_cd",
        "contact_monitor",
        "max_contacts_reported",
        "_sleeping",
        "_contacts"
    ]
    
    _SIGNALS = [
        "body_entered",
        "body_exited",
        "body_shape_entered",
        "body_shape_exited",
        "sleeping_state_changed"
    ]
    
    def __init__(self, name: str = "RigidBody2D"):
        super().__init__(name)
        self.node_type = NodeType.RIGIDBODY2D
        
        # Mass properties
        self.mass: float = 1.0
        self.physics_material_override: Optional[PhysicsMaterial] = None
        self.gravity_scale: float = 1.0
        
        # Center of mass
        self.center_of_mass_mode: int = self.CenterOfMassMode.AUTO
        self.center_of_mass: Vector2 = Vector2(0, 0)
        
        # Velocity
        self.linear_velocity: Vector2 = Vector2(0, 0)
        self.angular_velocity: float = 0.0
        
        # Damping
        self.linear_damp_mode: int = self.DampMode.COMBINE
        self.linear_damp: float = 0.0
        self.angular_damp_mode: int = self.DampMode.COMBINE
        self.angular_damp: float = 0.0
        
        # Forces
        self.constant_force: Vector2 = Vector2(0, 0)
        self.constant_torque: float = 0.0
        
        # Behavior
        self.body_mode: int = self.Mode.RIGID
        self.lock_rotation: bool = False
        self.freeze: bool = False
        self.freeze_mode: int = self.FreezeMode.STATIC
        
        # Collision detection
        self.continuous_cd: int = self.CCDMode.DISABLED
        self.contact_monitor: bool = False
        self.max_contacts_reported: int = 0
        
        # State
        self._sleeping: bool = False
        self._contacts: list = []
    
    def apply_central_force(self, force: Vector2) -> None:
        """Apply force at center of mass."""
        # Would integrate with physics engine
        pass
    
    def apply_force(self, force: Vector2, position: Vector2) -> None:
        """Apply force at position."""
        pass
    
    def apply_torque(self, torque: float) -> None:
        """Apply torque."""
        pass
    
    def apply_central_impulse(self, impulse: Vector2) -> None:
        """Apply impulse at center."""
        self.linear_velocity = self.linear_velocity + impulse / self.mass
    
    def apply_impulse(self, impulse: Vector2, position: Vector2) -> None:
        """Apply impulse at position."""
        pass
    
    def apply_torque_impulse(self, torque: float) -> None:
        """Apply torque impulse."""
        pass
    
    def set_sleeping(self, sleeping: bool) -> None:
        """Set sleeping state."""
        if sleeping != self._sleeping:
            self._sleeping = sleeping
            self.signals.emit("sleeping_state_changed")
    
    def is_sleeping(self) -> bool:
        """Check if body is sleeping."""
        return self._sleeping


__all__ = ["RigidBody2D", "PhysicsMaterial"]
