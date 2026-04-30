# /**************************************************************************/
# /*  static_body2d.py                                                      */
# /**************************************************************************/

"""StaticBody2D - Immovable physics body."""

from __future__ import annotations
from typing import Optional
from .node2d import Node2D
from .types import Vector2
from engine.core.types import NodeType

import logging


logger = logging.getLogger(__name__)



class StaticBody2D(Node2D):
    """Immovable physics body.
    
    Properties:
        physics_material_override: PhysicsMaterial
        constant_linear_velocity: Vector2 - Constant velocity for kinematic movement
        constant_angular_velocity: float - Constant angular velocity
    """
    
    __slots__ = [
        "physics_material_override",
        "constant_linear_velocity",
        "constant_angular_velocity"
    ]
    
    def __init__(self, name: str = "StaticBody2D"):
        super().__init__(name)
        self.node_type = NodeType.STATICBODY2D
        
        self.physics_material_override: Optional['PhysicsMaterial'] = None
        self.constant_linear_velocity: Vector2 = Vector2(0, 0)
        self.constant_angular_velocity: float = 0.0


__all__ = ["StaticBody2D"]
