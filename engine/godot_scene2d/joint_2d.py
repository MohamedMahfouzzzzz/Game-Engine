# /**************************************************************************/
# /*  joint_2d.py                                                           */
# /**************************************************************************/

"""Godot Joint2D port - 2D physics joints."""

from typing import Optional
from engine.core.nodes2d import Node2D
from engine.godot_scene2d.physics.physics_body_2d import PhysicsBody2D
from engine.godot_scene2d.types import Point2


class Joint2D(Node2D):
    """Base class for 2D physics joints."""
    
    def __init__(self, name: str = "Joint2D"):
        super().__init__(name)
        self._node_a: Optional[PhysicsBody2D] = None
        self._node_b: Optional[PhysicsBody2D] = None
        self._node_a_path: str = ""
        self._node_b_path: str = ""
        self._bias: float = 0.0
        self._disable_collision: bool = True
        self._solver_priority: int = 1
        self._softness: float = 0.0
    
    def set_node_a(self, node: Optional[PhysicsBody2D]) -> None:
        self._node_a = node
    
    def get_node_a(self) -> Optional[PhysicsBody2D]:
        return self._node_a
    
    def set_node_b(self, node: Optional[PhysicsBody2D]) -> None:
        self._node_b = node
    
    def get_node_b(self) -> Optional[PhysicsBody2D]:
        return self._node_b
    
    def set_node_a_path(self, path: str) -> None:
        self._node_a_path = path
    
    def get_node_a_path(self) -> str:
        return self._node_a_path
    
    def set_node_b_path(self, path: str) -> None:
        self._node_b_path = path
    
    def get_node_b_path(self) -> str:
        return self._node_b_path
    
    def set_bias(self, bias: float) -> None:
        self._bias = max(0.0, min(1.0, bias))
    
    def get_bias(self) -> float:
        return self._bias
    
    def set_disable_collision(self, disable: bool) -> None:
        self._disable_collision = disable
    
    def get_disable_collision(self) -> bool:
        return self._disable_collision
    
    def set_solver_priority(self, priority: int) -> None:
        self._solver_priority = max(1, priority)
    
    def get_solver_priority(self) -> int:
        return self._solver_priority
    
    def get_rid(self) -> any:
        return None
    
    def rebuild(self) -> None:
        pass
    
    def __repr__(self) -> str:
        return f"Joint2D('{self.name}')"


class PinJoint2D(Joint2D):
    """Pin joint - constrains two bodies to a common point."""
    
    def __init__(self, name: str = "PinJoint2D"):
        super().__init__(name)
        self._softness: float = 0.0
        self._motor_target_velocity: float = 0.0
        self._motor_enabled: bool = False
        self._motor_max_impulse: float = 0.7
    
    def set_softness(self, softness: float) -> None:
        self._softness = max(0.0, softness)
    
    def get_softness(self) -> float:
        return self._softness
    
    def set_motor_enabled(self, enabled: bool) -> None:
        self._motor_enabled = enabled
    
    def is_motor_enabled(self) -> bool:
        return self._motor_enabled
    
    def set_motor_target_velocity(self, velocity: float) -> None:
        self._motor_target_velocity = velocity
    
    def get_motor_target_velocity(self) -> float:
        return self._motor_target_velocity
    
    def __repr__(self) -> str:
        return f"PinJoint2D('{self.name}')"


class DampedSpringJoint2D(Joint2D):
    """Damped spring joint."""
    
    def __init__(self, name: str = "DampedSpringJoint2D"):
        super().__init__(name)
        self._length: float = 20.0
        self._rest_length: float = 10.0
        self._stiffness: float = 20.0
        self._damping: float = 1.5
    
    def set_length(self, length: float) -> None:
        self._length = max(0.0, length)
    
    def get_length(self) -> float:
        return self._length
    
    def set_rest_length(self, rest_length: float) -> None:
        self._rest_length = max(0.0, rest_length)
    
    def get_rest_length(self) -> float:
        return self._rest_length
    
    def set_stiffness(self, stiffness: float) -> None:
        self._stiffness = max(0.0, stiffness)
    
    def get_stiffness(self) -> float:
        return self._stiffness
    
    def set_damping(self, damping: float) -> None:
        self._damping = max(0.0, damping)
    
    def get_damping(self) -> float:
        return self._damping
    
    def __repr__(self) -> str:
        return f"DampedSpringJoint2D('{self.name}', length={self._length}, stiffness={self._stiffness})"


class GrooveJoint2D(Joint2D):
    """Groove joint - slides along a groove."""
    
    def __init__(self, name: str = "GrooveJoint2D"):
        super().__init__(name)
        self._length: float = 50.0
        self._initial_offset: float = 25.0
    
    def set_length(self, length: float) -> None:
        self._length = max(0.0, length)
    
    def get_length(self) -> float:
        return self._length
    
    def set_initial_offset(self, offset: float) -> None:
        self._initial_offset = offset
    
    def get_initial_offset(self) -> float:
        return self._initial_offset
    
    def __repr__(self) -> str:
        return f"GrooveJoint2D('{self.name}', length={self._length})"


class MotorJoint2D(Joint2D):
    """Motor joint - tries to maintain relative transform."""
    
    def __init__(self, name: str = "MotorJoint2D"):
        super().__init__(name)
        self._motor_target_transform: any = None
        self._linear_offset: Point2 = Point2()
        self._angular_offset: float = 0.0
        self._max_force: float = 1000.0
        self._max_torque: float = 1000.0
        self._correction_factor: float = 0.3
    
    def set_linear_offset(self, linear_offset: Point2) -> None:
        self._linear_offset = linear_offset
    
    def get_linear_offset(self) -> Point2:
        return self._linear_offset
    
    def set_angular_offset(self, angular_offset: float) -> None:
        self._angular_offset = angular_offset
    
    def get_angular_offset(self) -> float:
        return self._angular_offset
    
    def set_max_force(self, max_force: float) -> None:
        self._max_force = max(0.0, max_force)
    
    def get_max_force(self) -> float:
        return self._max_force
    
    def set_max_torque(self, max_torque: float) -> None:
        self._max_torque = max(0.0, max_torque)
    
    def get_max_torque(self) -> float:
        return self._max_torque
    
    def set_correction_factor(self, correction_factor: float) -> None:
        self._correction_factor = max(0.0, min(1.0, correction_factor))
    
    def get_correction_factor(self) -> float:
        return self._correction_factor
    
    def __repr__(self) -> str:
        return f"MotorJoint2D('{self.name}', force={self._max_force}, torque={self._max_torque})"
