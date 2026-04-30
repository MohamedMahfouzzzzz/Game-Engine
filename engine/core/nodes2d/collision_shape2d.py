# /**************************************************************************/
# /*  nodes2d/collision_shape2d.py                                          */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""CollisionShape2D - Physics collision component."""

from __future__ import annotations

from typing import Optional, Any
from enum import Enum, auto

from .node2d import Node2D
from engine.core.types import NodeType

class ShapeType(Enum):
    """Types of collision shapes."""
    RECTANGLE = auto()
    CIRCLE = auto()
    CAPSULE = auto()


class CollisionShape2D(Node2D):
    """Collision shape component. Uses composition pattern.
    
    Add as child to physics bodies instead of inheriting.
    
    Properties:
        shape_type: Type of collision shape
        size: Shape dimensions (width, height)
        radius: For circle/capsule shapes
        disabled: If True, collisions disabled
        one_way: Allow one-way collision platform
    """
    
    __slots__ = [
        "shape_type", "size", "radius", "height",
        "disabled", "one_way", "one_way_margin"
    ]
    
    _SIGNALS = ["shape_changed"]
    
    def __init__(self, name: str = "CollisionShape2D"):
        super().__init__(name)
        self.node_type = NodeType.COLLISIONSHAPE2D
        
        self.shape_type = ShapeType.RECTANGLE
        self.size = (32, 32)  # width, height
        self.radius = 16.0
        self.height = 32.0
        
        self.disabled = False
        self.one_way = False
        self.one_way_margin = 1.0
    
    def set_shape_rectangle(self, width: float, height: float) -> None:
        """Configure as rectangle."""
        self.shape_type = ShapeType.RECTANGLE
        self.size = (width, height)
        self.signals.emit("shape_changed")
    
    def set_shape_circle(self, radius: float) -> None:
        """Configure as circle."""
        self.shape_type = ShapeType.CIRCLE
        self.radius = radius
        self.signals.emit("shape_changed")
    
    def set_shape_capsule(self, radius: float, height: float) -> None:
        """Configure as capsule."""
        self.shape_type = ShapeType.CAPSULE
        self.radius = radius
        self.height = height
        self.signals.emit("shape_changed")
    
    def get_bounds(self) -> tuple:
        """Get AABB bounds (x, y, width, height)."""
        if self.shape_type == ShapeType.RECTANGLE:
            return (-self.size[0]/2, -self.size[1]/2, self.size[0], self.size[1])
        elif self.shape_type == ShapeType.CIRCLE:
            r = self.radius
            return (-r, -r, r*2, r*2)
        elif self.shape_type == ShapeType.CAPSULE:
            r = self.radius
            return (-r, -self.height/2, r*2, self.height)
        return (0, 0, 0, 0)
    
    def test_point(self, point: Any) -> bool:
        """Test if point is inside shape."""
        from .types import Vector2
        if not isinstance(point, Vector2):
            return False
        
        # Simple circle approximation for now
        if self.shape_type == ShapeType.CIRCLE:
            return point.length() <= self.radius
        elif self.shape_type == ShapeType.RECTANGLE:
            hw, hh = self.size[0]/2, self.size[1]/2
            return abs(point.x) <= hw and abs(point.y) <= hh
        return False
