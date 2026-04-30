# /**************************************************************************/
# /*  nodes2d/node2d.py                                                     */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Node2D - Base class for all 2D game objects."""

from __future__ import annotations

import math
from typing import Optional

from engine.core.node_base import Node
from engine.core.types import NodeType
from engine.core.transform import Transform2D
from .types import Vector2, Color

import logging


logger = logging.getLogger(__name__)



class Node2D(Node):
    """Base class for all 2D game objects with transform support.
    
    Properties:
        position: Local position relative to parent (Vector2)
        rotation: Rotation in degrees (float)
        scale: Scale factors (Vector2)
        z_index: Draw order, higher = on top (int)
        visible: If False, skip rendering (bool)
        modulate: Color tint (Color)
    
    Signals:
        transform_changed: Emitted when position/rotation/scale changes
        visibility_changed: Emitted when visibility toggles
    """
    
    __slots__ = [
        "_position", "_rotation", "_scale",
        "z_index", "z_relative",
        "visible",
        "modulate", "self_modulate",
        "_transform", "_global_transform", "_transform_dirty"
    ]
    
    _SIGNALS = ["transform_changed", "visibility_changed", "z_index_changed"]
    
    def __init__(self, name: str = "Node2D"):
        super().__init__(name, NodeType.NODE2D)
        
        # Transform
        self._position = Vector2(0, 0)
        self._rotation = 0.0
        self._scale = Vector2(1, 1)
        
        # Rendering
        self.z_index = 0
        self.z_relative = False
        self.visible = True
        self.modulate = Color.white()
        self.self_modulate = Color.white()
        
        # Cached transforms
        self._transform = Transform2D()
        self._global_transform: Optional[Transform2D] = None
        self._transform_dirty = True
        
        self._update_transform_matrix()
    
    @property
    def position(self) -> Vector2:
        return self._position.copy()
    
    @position.setter
    def position(self, value: Vector2) -> None:
        self._position = value.copy() if hasattr(value, 'copy') else Vector2(value[0], value[1])
        self._mark_transform_dirty()
    
    @property
    def rotation(self) -> float:
        return self._rotation
    
    @rotation.setter
    def rotation(self, value: float) -> None:
        self._rotation = value
        self._mark_transform_dirty()
    
    @property
    def scale(self) -> Vector2:
        return self._scale.copy()
    
    @scale.setter
    def scale(self, value: Vector2) -> None:
        self._scale = value.copy() if hasattr(value, 'copy') else Vector2(value[0], value[1])
        self._mark_transform_dirty()
    
    def _mark_transform_dirty(self) -> None:
        """Mark transform as needing recalculation."""
        self._transform_dirty = True
        self._global_transform = None
        self.signals.emit("transform_changed")
        
        # Propagate to children
        for child in self.children:
            if isinstance(child, Node2D):
                child._transform_dirty = True
                child._global_transform = None
    
    def _update_transform_matrix(self) -> None:
        """Rebuild local transform matrix."""
        self._transform = Transform2D.from_components(
            translation=(self._position.x, self._position.y),
            rotation=math.radians(self._rotation),
            scale=(self._scale.x, self._scale.y)
        )
        self._transform_dirty = False
    
    def get_transform(self) -> Transform2D:
        """Get local transform matrix."""
        if self._transform_dirty:
            self._update_transform_matrix()
        return self._transform
    
    def get_global_transform(self) -> Transform2D:
        """Get transform in world space."""
        if not self._transform_dirty and self._global_transform is not None:
            return self._global_transform
        
        local = self.get_transform()
        
        if self.parent and isinstance(self.parent, Node2D):
            parent_global = self.parent.get_global_transform()
            self._global_transform = parent_global * local
        else:
            self._global_transform = local
        
        return self._global_transform
    
    def get_global_position(self) -> Vector2:
        """Get position in world coordinates."""
        global_xform = self.get_global_transform()
        origin = global_xform.origin
        return Vector2(origin[0], origin[1])
    
    def set_global_position(self, pos: Vector2) -> None:
        """Set position in world coordinates."""
        if self.parent and isinstance(self.parent, Node2D):
            parent_global = self.parent.get_global_transform()
            parent_inv = parent_global.affine_inverse()
            local_pos = parent_inv * (pos.x, pos.y)
            self.position = Vector2(local_pos[0], local_pos[1])
        else:
            self.position = pos
    
    def to_local(self, global_point: Vector2) -> Vector2:
        """Convert world point to local coordinates."""
        global_xform = self.get_global_transform()
        inv = global_xform.affine_inverse()
        result = inv * (global_point.x, global_point.y)
        return Vector2(result[0], result[1])
    
    def to_global(self, local_point: Vector2) -> Vector2:
        """Convert local point to world coordinates."""
        global_xform = self.get_global_transform()
        result = global_xform * (local_point.x, local_point.y)
        return Vector2(result[0], result[1])
    
    def translate(self, offset: Vector2) -> None:
        """Move by offset in local space."""
        self.position = self._position + offset
    
    def rotate(self, degrees: float) -> None:
        """Rotate by degrees."""
        self.rotation = self._rotation + degrees
    
    def look_at(self, target: Vector2) -> None:
        """Rotate to face target position."""
        direction = target - self.get_global_position()
        self.rotation = math.degrees(direction.angle())
    
    def show(self) -> None:
        """Make visible."""
        if not self.visible:
            self.visible = True
            self.signals.emit("visibility_changed", True)
    
    def hide(self) -> None:
        """Make invisible."""
        if self.visible:
            self.visible = False
            self.signals.emit("visibility_changed", False)
    
    def _draw(self, renderer) -> None:
        """Override to render this node."""
        pass
