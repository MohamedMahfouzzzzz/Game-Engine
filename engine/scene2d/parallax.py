# /**************************************************************************/
# /*  parallax.py                                                           */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""2D parallax background nodes."""

from typing import List, Optional
from engine.core.nodes2d import Node2D, Vector2


class ParallaxLayer(Node2D):
    """Single layer in a parallax background.
    
    Moves at different speed than camera for depth effect.
    """
    
    def __init__(self, name: str = "ParallaxLayer"):
        super().__init__(name)
        self._motion_scale: Vector2 = Vector2(1, 1)
        self._motion_offset: Vector2 = Vector2()
        self._motion_mirroring: Vector2 = Vector2()
        self._visibility_rect = None
    
    def set_motion_scale(self, scale: Vector2) -> None:
        """Set parallax motion scale.
        
        (1, 1) = moves with camera (no parallax)
        (0.5, 0.5) = moves half speed (background)
        (2, 2) = moves twice as fast (foreground)
        """
        self._motion_scale = scale
    
    def get_motion_scale(self) -> Vector2:
        return self._motion_scale
    
    def set_motion_offset(self, offset: Vector2) -> None:
        """Additional offset applied to layer."""
        self._motion_offset = offset
    
    def get_motion_offset(self) -> Vector2:
        return self._motion_offset
    
    def set_motion_mirroring(self, mirroring: Vector2) -> None:
        """Repeat/mirror layer at these intervals (0 = no mirror)."""
        self._motion_mirroring = Vector2(
            max(0, mirroring.x),
            max(0, mirroring.y)
        )
    
    def get_motion_mirroring(self) -> Vector2:
        return self._motion_mirroring
    
    def __repr__(self) -> str:
        return f"ParallaxLayer('{self.name}', scale=({self._motion_scale.x}, {self._motion_scale.y}))"


class ParallaxBackground(Node2D):
    """Container for parallax layers.
    
    Automatically scrolls child ParallaxLayer nodes based on
    camera position.
    """
    
    def __init__(self, name: str = "ParallaxBackground"):
        super().__init__(name)
        self._scroll_offset: Vector2 = Vector2()
        self._scroll_scale: Vector2 = Vector2(1, 1)
        self._scroll_base_offset: Vector2 = Vector2()
        self._scroll_base_scale: Vector2 = Vector2(1, 1)
        self._scroll_ignore_camera_zoom: bool = False
        self._scroll_limit_begin: Vector2 = Vector2(-10000000, -10000000)
        self._scroll_limit_end: Vector2 = Vector2(10000000, 10000000)
        self._layers: List[ParallaxLayer] = []
    
    def set_scroll_offset(self, offset: Vector2) -> None:
        """Manual scroll offset."""
        self._scroll_offset = offset
        self._update_layers()
    
    def get_scroll_offset(self) -> Vector2:
        return self._scroll_offset
    
    def set_scroll_scale(self, scale: Vector2) -> None:
        """Scale applied to scroll input."""
        self._scroll_scale = scale
    
    def get_scroll_scale(self) -> Vector2:
        return self._scroll_scale
    
    def set_scroll_base_offset(self, offset: Vector2) -> None:
        """Base scroll offset."""
        self._scroll_base_offset = offset
    
    def get_scroll_base_offset(self) -> Vector2:
        return self._scroll_base_offset
    
    def set_scroll_limit_begin(self, limit: Vector2) -> None:
        """Minimum scroll position."""
        self._scroll_limit_begin = limit
    
    def get_scroll_limit_begin(self) -> Vector2:
        return self._scroll_limit_begin
    
    def set_scroll_limit_end(self, limit: Vector2) -> None:
        """Maximum scroll position."""
        self._scroll_limit_end = limit
    
    def get_scroll_limit_end(self) -> Vector2:
        return self._scroll_limit_end
    
    def _update_layers(self) -> None:
        """Update all child parallax layers."""
        for layer in self._layers:
            # Calculate parallax offset
            parallax_x = self._scroll_offset.x * (1 - layer.get_motion_scale().x)
            parallax_y = self._scroll_offset.y * (1 - layer.get_motion_scale().y)
            layer.position = Vector2(parallax_x, parallax_y) + layer.get_motion_offset()
    
    def add_layer(self, layer: ParallaxLayer) -> None:
        """Add a parallax layer."""
        self._layers.append(layer)
    
    def remove_layer(self, layer: ParallaxLayer) -> None:
        if layer in self._layers:
            self._layers.remove(layer)
    
    def __repr__(self) -> str:
        return f"ParallaxBackground('{self.name}', layers={len(self._layers)})"


class Parallax2D(Node2D):
    """Newer parallax node with simpler configuration.
    
    Replaces ParallaxBackground/ParallaxLayer for simpler use cases.
    """
    
    def __init__(self, name: str = "Parallax2D"):
        super().__init__(name)
        self._scroll_scale: Vector2 = Vector2(1, 1)
        self._scroll_offset: Vector2 = Vector2()
        self._repeat_size: Vector2 = Vector2()
        self._repeat_times: int = 1
        self._autoscroll: Vector2 = Vector2()
        self._limit_begin: Vector2 = Vector2(-10000000, -10000000)
        self._limit_end: Vector2 = Vector2(10000000, 10000000)
        self._ignore_camera_zoom: bool = False
    
    def set_scroll_scale(self, scale: Vector2) -> None:
        """Scroll scale - lower = slower = appears farther."""
        self._scroll_scale = scale
    
    def get_scroll_scale(self) -> Vector2:
        return self._scroll_scale
    
    def set_scroll_offset(self, offset: Vector2) -> None:
        self._scroll_offset = offset
    
    def get_scroll_offset(self) -> Vector2:
        return self._scroll_offset
    
    def set_repeat_size(self, size: Vector2) -> None:
        """Size to repeat/tile the content."""
        self._repeat_size = Vector2(max(0, size.x), max(0, size.y))
    
    def get_repeat_size(self) -> Vector2:
        return self._repeat_size
    
    def set_repeat_times(self, times: int) -> None:
        """Number of times to repeat (-1 = infinite)."""
        self._repeat_times = times
    
    def get_repeat_times(self) -> int:
        return self._repeat_times
    
    def set_autoscroll(self, speed: Vector2) -> None:
        """Automatic scrolling speed."""
        self._autoscroll = speed
    
    def get_autoscroll(self) -> Vector2:
        return self._autoscroll
    
    def set_limit_begin(self, limit: Vector2) -> None:
        self._limit_begin = limit
    
    def get_limit_begin(self) -> Vector2:
        return self._limit_begin
    
    def set_limit_end(self, limit: Vector2) -> None:
        self._limit_end = limit
    
    def get_limit_end(self) -> Vector2:
        return self._limit_end
    
    def __repr__(self) -> str:
        return f"Parallax2D('{self.name}', scale=({self._scroll_scale.x}, {self._scroll_scale.y}))"
