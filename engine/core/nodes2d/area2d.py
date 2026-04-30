# /**************************************************************************/
# /*  nodes2d/area2d.py                                                     */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Area2D - Detection zone with entry/exit signals."""

from __future__ import annotations

from typing import Optional, Set, List
from enum import IntEnum

from .node2d import Node2D
from .types import Vector2
from engine.core.types import NodeType

import logging


logger = logging.getLogger(__name__)



class Area2D(Node2D):
    """Area for detecting overlapping bodies and areas.
    
    Use cases:
        - Hitboxes and hurtboxes
        - Trigger zones (switches, doors)
        - Detection zones (enemy aggro)
        - Environmental effects (gravity, damage zones)
    
    Properties:
        monitoring: Detect areas/bodies entering (bool)
        monitorable: Be detected by other areas (bool)
        priority: Evaluation order
    
    Signals:
        body_entered, body_exited
        area_entered, area_exited
    """
    
    class SpaceOverride(IntEnum):
        DISABLED = 0
        COMBINE = 1
        REPLACE = 2
    
    __slots__ = [
        "monitoring", "monitorable", "priority",
        "gravity_space_override", "gravity_direction", "gravity_strength",
        "_overlapping_bodies", "_overlapping_areas",
        "_collision_shape"
    ]
    
    _SIGNALS = [
        "body_entered", "body_exited",
        "area_entered", "area_exited"
    ]
    
    def __init__(self, name: str = "Area2D"):
        super().__init__(name)
        self.node_type = NodeType.AREA2D
        
        self.monitoring = True
        self.monitorable = True
        self.priority = 0
        
        # Gravity override
        self.gravity_space_override = self.SpaceOverride.DISABLED
        self.gravity_direction = Vector2(0, -1)
        self.gravity_strength = 980.0
        
        # Overlapping objects
        self._overlapping_bodies: Set[int] = set()
        self._overlapping_areas: Set[int] = set()
        
        self._collision_shape: Optional['CollisionShape2D'] = None
    
    def _find_collision_shape(self) -> Optional['CollisionShape2D']:
        """Find attached collision shape."""
        if self._collision_shape is not None:
            return self._collision_shape
        
        for child in self.children:
            if hasattr(child, 'shape_type'):
                self._collision_shape = child
                return child
        return None
    
    def get_overlapping_bodies(self) -> List[Node2D]:
        """Get list of overlapping physics bodies."""
        # Production: query physics engine
        return []
    
    def get_overlapping_areas(self) -> List['Area2D']:
        """Get list of overlapping areas."""
        # Production: query physics engine
        return []
    
    def has_overlapping_bodies(self) -> bool:
        """Check if any body overlaps."""
        return len(self._overlapping_bodies) > 0
    
    def overlaps_body(self, body: Node2D) -> bool:
        """Check if specific body overlaps."""
        return id(body) in self._overlapping_bodies
    
    def _on_body_entered(self, body: Node2D) -> None:
        """Called when body enters."""
        self._overlapping_bodies.add(id(body))
        self.signals.emit("body_entered", body)
    
    def _on_body_exited(self, body: Node2D) -> None:
        """Called when body exits."""
        self._overlapping_bodies.discard(id(body))
        self.signals.emit("body_exited", body)
    
    def _on_area_entered(self, area: 'Area2D') -> None:
        """Called when area enters."""
        self._overlapping_areas.add(id(area))
        self.signals.emit("area_entered", area)
    
    def _on_area_exited(self, area: 'Area2D') -> None:
        """Called when area exits."""
        self._overlapping_areas.discard(id(area))
        self.signals.emit("area_exited", area)
