# /**************************************************************************/
# /*  nodes2d/camera2d.py                                                   */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Camera2D - 2D camera for viewport control."""

from __future__ import annotations

from typing import Optional
from enum import Enum, auto

from .node2d import Node2D
from .types import Vector2
from engine.core.types import NodeType

import logging


logger = logging.getLogger(__name__)



class Camera2D(Node2D):
    """2D camera controlling the viewport.
    
    Features:
        - Zoom control
        - Smooth following
        - Camera limits (world boundaries)
        - Multiple anchor modes
        - Drag margins for smooth following
    
    Properties:
        zoom: Scale factor (Vector2)
        offset: Viewport offset
        limit_*: World boundaries
        smoothing_enabled: Smooth camera movement
        smoothing_speed: Interpolation speed
        anchor_mode: Anchor point behavior
    
    Signals:
        camera_moved: When position changes
    """
    
    class AnchorMode(Enum):
        """How camera anchor point works."""
        CENTER = auto()  # Anchor at center
        TOP_LEFT = auto()  # Anchor at top-left
    
    __slots__ = [
        "zoom", "offset",
        "limit_left", "limit_right", "limit_top", "limit_bottom",
        "limit_smoothed",
        "smoothing_enabled", "smoothing_speed",
        "anchor_mode",
        "follow_target", "follow_smoothing",
        "_camera_position"
    ]
    
    _SIGNALS = ["camera_moved"]
    
    def __init__(self, name: str = "Camera2D"):
        super().__init__(name)
        self.node_type = NodeType.CAMERA2D
        
        self.zoom = Vector2(1, 1)
        self.offset = Vector2(0, 0)
        
        # Limits
        self.limit_left = -10000000
        self.limit_right = 10000000
        self.limit_top = -10000000
        self.limit_bottom = 10000000
        self.limit_smoothed = False
        
        # Smoothing
        self.smoothing_enabled = False
        self.smoothing_speed = 5.0
        
        self.anchor_mode = self.AnchorMode.CENTER
        
        # Following
        self.follow_target: Optional[Node2D] = None
        self.follow_smoothing = 0.0
        
        self._camera_position = Vector2(0, 0)
    
    def get_screen_center(self) -> Vector2:
        """Get the world position at screen center."""
        # Get viewport size (would come from renderer)
        viewport_size = Vector2(800, 600)  # Default
        
        # Calculate center based on anchor mode
        if self.anchor_mode == self.AnchorMode.CENTER:
            return self.get_global_position()
        else:
            pos = self.get_global_position()
            return Vector2(
                pos.x + viewport_size.x / (2 * self.zoom.x),
                pos.y + viewport_size.y / (2 * self.zoom.y)
            )
    
    def set_screen_center(self, pos: Vector2) -> None:
        """Move camera so pos is at screen center."""
        self.set_global_position(pos)
    
    def get_viewport_rect(self) -> tuple:
        """Get visible world rectangle (x, y, width, height)."""
        center = self.get_screen_center()
        # Get viewport size from renderer
        vw, vh = 800 / self.zoom.x, 600 / self.zoom.y
        return (center.x - vw/2, center.y - vh/2, vw, vh)
    
    def is_position_visible(self, pos: Vector2) -> bool:
        """Check if world position is in view."""
        rect = self.get_viewport_rect()
        return (rect[0] <= pos.x <= rect[0] + rect[2] and
                rect[1] <= pos.y <= rect[1] + rect[3])
    
    def align(self) -> None:
        """Align camera to follow target immediately."""
        if self.follow_target:
            self.set_global_position(self.follow_target.get_global_position())
    
    def reset_smoothing(self) -> None:
        """Reset smoothing to jump to target."""
        self.align()
    
    def _update(self, delta: float) -> None:
        """Update camera position."""
        if self.follow_target:
            target_pos = self.follow_target.get_global_position()
            
            if self.smoothing_enabled:
                # Smooth interpolation
                current = self.get_global_position()
                t = min(1.0, self.smoothing_speed * delta)
                new_pos = current.lerp(target_pos, t)
                self.set_global_position(new_pos)
            else:
                self.set_global_position(target_pos)
            
            self.signals.emit("camera_moved", self.get_global_position())
