# /**************************************************************************/
# /*  joint.py                                                              */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""2D physics joints for constraining bodies."""

from typing import Optional
from engine.core.nodes2d import Node2D, Vector2


class Joint2D(Node2D):
    """Base class for 2D physics joints.
    
    Connects two physics bodies with various constraints.
    """
    
    def __init__(self, name: str = "Joint2D"):
        super().__init__(name)
        self._node_a: str = ""
        self._node_b: str = ""
        self._collide_connected: bool = false
        self._bias: float = 0.0
        self._disable_collision: bool = True
    
    def set_node_a(self, path: str) -> None:
        """Set path to first body."""
        self._node_a = path
    
    def get_node_a(self) -> str:
        return self._node_a
    
    def set_node_b(self, path: str) -> None:
        """Set path to second body."""
        self._node_b = path
    
    def get_node_b(self) -> str:
        return self._node_b
    
    def set_collide_connected(self, collide: bool) -> None:
        """Enable collision between connected bodies."""
        self._collide_connected = collide
    
    def get_collide_connected(self) -> bool:
        return self._collide_connected
    
    def get_rid(self) -> int:
        return id(self)
    
    def __repr__(self) -> str:
        return f"Joint2D('{self.name}', a='{self._node_a}', b='{self._node_b}')"


class PinJoint2D(Joint2D):
    """Pin joint - constrains bodies to a point.
    
    Like a hinge or pivot point.
    """
    
    def __init__(self, name: str = "PinJoint2D"):
        super().__init__(name)
        self._softness: float = 0.0
        self._bias: float = 0.0
        self._motor_enabled: bool = False
        self._motor_target_velocity: float = 0.0
    
    def set_softness(self, softness: float) -> None:
        """Joint softness (0 = rigid)."""
        self._softness = max(0.0, min(1.0, softness))
    
    def get_softness(self) -> float:
        return self._softness
    
    def set_motor_enabled(self, enabled: bool) -> None:
        """Enable motor rotation."""
        self._motor_enabled = enabled
    
    def is_motor_enabled(self) -> bool:
        return self._motor_enabled
    
    def set_motor_target_velocity(self, velocity: float) -> None:
        """Motor rotation speed."""
        self._motor_target_velocity = velocity
    
    def get_motor_target_velocity(self) -> float:
        return self._motor_target_velocity


class DampedSpringJoint2D(Joint2D):
    """Damped spring joint - springy connection.
    
    Like a spring with damping.
    """
    
    def __init__(self, name: str = "DampedSpringJoint2D"):
        super().__init__(name)
        self._length: float = 10.0
        self._rest_length: float = 5.0
        self._stiffness: float = 20.0
        self._damping: float = 1.5
    
    def set_length(self, length: float) -> None:
        """Spring length when at rest."""
        self._length = max(0.0, length)
    
    def get_length(self) -> float:
        return self._length
    
    def set_rest_length(self, length: float) -> None:
        """Target rest length."""
        self._rest_length = max(0.0, length)
    
    def get_rest_length(self) -> float:
        return self._rest_length
    
    def set_stiffness(self, stiffness: float) -> None:
        """Spring stiffness."""
        self._stiffness = max(0.0, stiffness)
    
    def get_stiffness(self) -> float:
        return self._stiffness
    
    def set_damping(self, damping: float) -> None:
        """Damping coefficient."""
        self._damping = max(0.0, damping)
    
    def get_damping(self) -> float:
        return self._damping


class GrooveJoint2D(Joint2D):
    """Groove joint - body slides along a groove.
    
    Constrains body to slide along a line.
    """
    
    def __init__(self, name: str = "GrooveJoint2D"):
        super().__init__(name)
        self._length: float = 10.0
        self._initial_offset: float = 5.0
    
    def set_length(self, length: float) -> None:
        self._length = max(0.0, length)
    
    def get_length(self) -> float:
        return self._length
    
    def set_initial_offset(self, offset: float) -> None:
        self._initial_offset = offset
    
    def get_initial_offset(self) -> float:
        return self._initial_offset


class MotorJoint2D(Joint2D):
    """Motor joint - controls relative motion.
    
    Applies force to reach target relative transform.
    """
    
    def __init__(self, name: str = "MotorJoint2D"):
        super().__init__(name)
        self._linear_offset: Vector2 = Vector2()
        self._angular_offset: float = 0.0
        self._max_force: float = 1000.0
        self._max_torque: float = 1000.0
        self._correction_factor: float = 1.0
    
    def set_linear_offset(self, offset: Vector2) -> None:
        """Target relative position."""
        self._linear_offset = offset
    
    def get_linear_offset(self) -> Vector2:
        return self._linear_offset
    
    def set_angular_offset(self, offset: float) -> None:
        """Target relative rotation."""
        self._angular_offset = offset
    
    def get_angular_offset(self) -> float:
        return self._angular_offset
    
    def set_max_force(self, max_force: float) -> None:
        """Maximum force to apply."""
        self._max_force = max(0.0, max_force)
    
    def get_max_force(self) -> float:
        return self._max_force
    
    def set_max_torque(self, max_torque: float) -> None:
        """Maximum torque to apply."""
        self._max_torque = max(0.0, max_torque)
    
    def get_max_torque(self) -> float:
        return self._max_torque
    
    def set_correction_factor(self, factor: float) -> None:
        """Position correction factor."""
        self._correction_factor = max(0.0, min(1.0, factor))
    
    def get_correction_factor(self) -> float:
        return self._correction_factor
