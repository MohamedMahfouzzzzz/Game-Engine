# /**************************************************************************/
# /*  parallax_layer2d.py                                                    */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""ParallaxLayer2D - Parallax scrolling layer for backgrounds."""

from __future__ import annotations

from typing import Optional

from .types import Vector2
from .sprite2d import Sprite2D

import logging


logger = logging.getLogger(__name__)


class ParallaxLayer2D(Sprite2D):
    """A sprite layer that scrolls at different speed for parallax effect.
    
    Properties:
        scroll_scale: Movement multiplier relative to camera (Vector2)
        auto_scroll: Automatic scrolling speed (Vector2)
        mirroring: Repeat texture for infinite scrolling (Vector2)
        limit_begin: Minimum scroll limit (Vector2)
        limit_end: Maximum scroll limit (Vector2)
        
    Signals:
        scrolled: Emitted when layer scrolls
    """
    
    __slots__ = [
        "scroll_scale",
        "auto_scroll",
        "mirroring",
        "limit_begin", "limit_end",
        "_scroll_position",
        "_camera_position"
    ]
    
    _SIGNALS = ["scrolled"]
    
    def __init__(self, name: str = "ParallaxLayer2D"):
        super().__init__(name)
        self.node_type = "ParallaxLayer2D"
        
        # Parallax settings
        self.scroll_scale: Vector2 = Vector2(0.5, 0.5)  # 0.5 = moves at half camera speed
        self.auto_scroll: Vector2 = Vector2(0, 0)  # pixels per second
        self.mirroring: Vector2 = Vector2(0, 0)  # 0 = no repeat
        
        # Scroll limits
        self.limit_begin: Vector2 = Vector2(-1000000, -1000000)
        self.limit_end: Vector2 = Vector2(1000000, 1000000)
        
        # Internal state
        self._scroll_position: Vector2 = Vector2(0, 0)
        self._camera_position: Vector2 = Vector2(0, 0)
    
    def set_scroll_scale(self, x: float, y: float) -> None:
        """Set parallax scroll scale.
        
        1.0 = moves with camera (no parallax)
        0.5 = moves at half camera speed (far layer)
        2.0 = moves faster than camera (close layer)
        """
        self.scroll_scale = Vector2(x, y)
    
    def set_auto_scroll(self, x: float, y: float) -> None:
        """Set automatic scrolling speed in pixels per second."""
        self.auto_scroll = Vector2(x, y)
    
    def set_mirroring(self, x: int, y: int) -> None:
        """Set mirroring distance for infinite scrolling.
        
        Set to texture size to create seamless infinite background.
        """
        self.mirroring = Vector2(x, y)
    
    def set_limits(self, begin_x: float, begin_y: float, 
                   end_x: float, end_y: float) -> None:
        """Set scroll limits."""
        self.limit_begin = Vector2(begin_x, begin_y)
        self.limit_end = Vector2(end_x, end_y)
    
    def update_camera_position(self, camera_pos: Vector2) -> None:
        """Update with current camera position."""
        self._camera_position = camera_pos
        
        # Calculate parallax position
        parallax_x = camera_pos.x * (1.0 - self.scroll_scale.x)
        parallax_y = camera_pos.y * (1.0 - self.scroll_scale.y)
        
        # Add auto-scroll offset
        # (would need delta time for real auto-scroll)
        
        # Apply limits
        parallax_x = max(self.limit_begin.x, min(self.limit_end.x, parallax_x))
        parallax_y = max(self.limit_begin.y, min(self.limit_end.y, parallax_y))
        
        # Update offset
        self._scroll_position = Vector2(parallax_x, parallax_y)
        self.offset = self._scroll_position
        
        self.signals.emit("scrolled", self._scroll_position)
    
    def get_screen_position(self, camera_pos: Vector2) -> Vector2:
        """Get the position on screen given camera position."""
        # Base position
        base_pos = self.get_global_position()
        
        # Apply parallax
        screen_x = base_pos.x - (camera_pos.x * self.scroll_scale.x)
        screen_y = base_pos.y - (camera_pos.y * self.scroll_scale.y)
        
        # Apply mirroring for infinite scroll
        if self.mirroring.x > 0:
            screen_x = screen_x % self.mirroring.x
        if self.mirroring.y > 0:
            screen_y = screen_y % self.mirroring.y
        
        return Vector2(screen_x, screen_y)
    
    def _draw(self, renderer) -> None:
        """Draw the parallax layer with wrapping."""
        if not self.visible or not self.texture or not self.texture.is_loaded():
            return
        
        if self.mirroring.x <= 0 and self.mirroring.y <= 0:
            # No mirroring, draw as normal sprite
            super()._draw(renderer)
            return
        
        # Draw with tiling for parallax
        if hasattr(renderer, 'draw_parallax'):
            renderer.draw_parallax(
                texture=self.texture,
                position=self.get_global_position() + self.offset,
                scroll_position=self._scroll_position,
                scroll_scale=self.scroll_scale,
                mirroring=self.mirroring,
                flip_h=self.flip_h,
                flip_v=self.flip_v,
                modulate=self.modulate
            )
        else:
            # Fallback: draw as normal sprite
            super()._draw(renderer)
