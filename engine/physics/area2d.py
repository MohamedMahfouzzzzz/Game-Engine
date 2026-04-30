# /**************************************************************************/
# /*  area2d.py                                                             */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Area2D for collision detection without physics response."""

from typing import Callable, List, Optional, Set, Tuple, Dict
from engine.core.node_base import Node2D
from engine.core.types import NodeType

import logging


logger = logging.getLogger(__name__)



class Area2D(Node2D):
    """An area that detects overlapping bodies without physics response."""

    def __init__(self, name: str = "Area2D"):
        super().__init__(name)
        self.node_type = NodeType.AREA2D

        self.shapes: List["CollisionShape2D"] = []
        self._world: Optional["PhysicsWorld"] = None

        # Overlap tracking
        self._overlapping_bodies: Set["RigidBody2D"] = set()
        self._previous_overlaps: Set["RigidBody2D"] = set()

        # Callbacks
        self._on_body_entered: Optional[Callable[["RigidBody2D"], None]] = None
        self._on_body_exited: Optional[Callable[["RigidBody2D"], None]] = None
        self._on_body_shape_entered: Optional[Callable[["RigidBody2D", int, int], None]] = None
        self._on_body_shape_exited: Optional[Callable[["RigidBody2D", int, int], None]] = None

        # Monitoring settings
        self.monitorable: bool = True  # Can be detected by other areas
        self.monitoring: bool = True  # Detects other bodies
        self.priority: int = 0  # For overlapping area priority

        # Layer/mask system for collision filtering
        self.collision_layer: int = 1  # What layer this area is on
        self.collision_mask: int = 1  # What layers this area detects

    def add_shape(self, shape: "CollisionShape2D") -> None:
        """Add a collision shape."""
        self.shapes.append(shape)
        shape.body = self

    def remove_shape(self, shape: "CollisionShape2D") -> None:
        """Remove a collision shape."""
        if shape in self.shapes:
            self.shapes.remove(shape)
            shape.body = None

    def overlaps_body(self, body: "RigidBody2D") -> bool:
        """Check if area overlaps a physics body."""
        if not self.monitoring:
            return False

        # Check collision mask
        if not (self.collision_mask & body.collision_layer):
            return False

        # Check shape overlaps
        for area_shape in self.shapes:
            if area_shape.disabled:
                continue
            for body_shape in body.shapes:
                if body_shape.disabled:
                    continue
                if area_shape.intersects(body_shape):
                    return True
        return False

    def overlaps_area(self, other: "Area2D") -> bool:
        """Check if area overlaps another area."""
        if not self.monitoring or not other.monitorable:
            return False

        for shape1 in self.shapes:
            if shape1.disabled:
                continue
            for shape2 in other.shapes:
                if shape2.disabled:
                    continue
                if shape1.intersects(shape2):
                    return True
        return False

    def _update_overlaps(self, overlapping: Set["RigidBody2D"]) -> None:
        """Update overlapping bodies and emit signals (internal use)."""
        self._previous_overlaps = self._overlapping_bodies.copy()
        self._overlapping_bodies = overlapping

        # Detect enter/exit
        entered = self._overlapping_bodies - self._previous_overlaps
        exited = self._previous_overlaps - self._overlapping_bodies

        for body in entered:
            if self._on_body_entered:
                self._on_body_entered(body)

        for body in exited:
            if self._on_body_exited:
                self._on_body_exited(body)

    def get_overlapping_bodies(self) -> List["RigidBody2D"]:
        """Get list of bodies currently overlapping."""
        return list(self._overlapping_bodies)

    def has_overlapping_bodies(self) -> bool:
        """Check if any body is overlapping."""
        return len(self._overlapping_bodies) > 0

    def get_overlapping_areas(self) -> List["Area2D"]:
        """Get list of overlapping areas."""
        if not self._world:
            return []

        overlapping = []
        for area in self._world.areas:
            if area is not self and self.overlaps_area(area):
                overlapping.append(area)
        return overlapping

    # Connection methods for signals
    def connect_body_entered(self, callback: Callable[["RigidBody2D"], None]) -> None:
        """Connect callback for body entered signal."""
        self._on_body_entered = callback

    def connect_body_exited(self, callback: Callable[["RigidBody2D"], None]) -> None:
        """Connect callback for body exited signal."""
        self._on_body_exited = callback

    def connect_body_shape_entered(
        self,
        callback: Callable[["RigidBody2D", int, int], None]
    ) -> None:
        """Connect callback for body shape entered signal."""
        self._on_body_shape_entered = callback

    def connect_body_shape_exited(
        self,
        callback: Callable[["RigidBody2D", int, int], None]
    ) -> None:
        """Connect callback for body shape exited signal."""
        self._on_body_shape_exited = callback

    def set_collision_layer_bit(self, bit: int, value: bool) -> None:
        """Set a specific collision layer bit."""
        if value:
            self.collision_layer |= (1 << bit)
        else:
            self.collision_layer &= ~(1 << bit)

    def get_collision_layer_bit(self, bit: int) -> bool:
        """Get a specific collision layer bit."""
        return bool(self.collision_layer & (1 << bit))

    def set_collision_mask_bit(self, bit: int, value: bool) -> None:
        """Set a specific collision mask bit."""
        if value:
            self.collision_mask |= (1 << bit)
        else:
            self.collision_mask &= ~(1 << bit)

    def get_collision_mask_bit(self, bit: int) -> bool:
        """Get a specific collision mask bit."""
        return bool(self.collision_mask & (1 << bit))

    def query_overlaps(self) -> Dict[str, any]:
        """Query detailed overlap information."""
        return {
            "overlapping_bodies": len(self._overlapping_bodies),
            "bodies": [b.name for b in self._overlapping_bodies],
            "has_overlaps": self.has_overlapping_bodies(),
            "monitoring": self.monitoring,
            "monitorable": self.monitorable,
        }
