# /**************************************************************************/
# /*  tool_base.py                                                          */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Base class for all drawing tools."""

from abc import ABC, abstractmethod
from typing import Optional, Tuple

import logging


logger = logging.getLogger(__name__)



class ToolBase(ABC):
    """Abstract base class for drawing tools."""

    def __init__(self, name: str, icon: str = ""):
        self.name = name
        self.icon = icon
        self._canvas: Optional["Canvas"] = None
        self._active_layer: Optional["Layer"] = None
        self._current_color: Tuple[int, int, int, int] = (0, 0, 0, 255)
        self._secondary_color: Tuple[int, int, int, int] = (255, 255, 255, 255)
        self._brush_size: int = 1
        self._opacity: float = 1.0

        # Tool state
        self._is_drawing: bool = False
        self._start_pos: Optional[Tuple[int, int]] = None
        self._current_pos: Optional[Tuple[int, int]] = None

    def set_canvas(self, canvas: "Canvas") -> None:
        """Set the canvas to work on."""
        self._canvas = canvas
        self._active_layer = canvas.get_active_layer()

    def set_color(self, color: Tuple[int, int, int, int]) -> None:
        """Set primary drawing color."""
        self._current_color = color

    def set_secondary_color(self, color: Tuple[int, int, int, int]) -> None:
        """Set secondary color (right-click)."""
        self._secondary_color = color

    def set_brush_size(self, size: int) -> None:
        """Set brush size in pixels."""
        self._brush_size = max(1, size)

    def set_opacity(self, opacity: float) -> None:
        """Set tool opacity."""
        self._opacity = max(0.0, min(1.0, opacity))

    def on_mouse_press(self, x: int, y: int, button: int = 1) -> None:
        """Called when mouse button is pressed."""
        self._is_drawing = True
        self._start_pos = (x, y)
        self._current_pos = (x, y)

    def on_mouse_move(self, x: int, y: int) -> None:
        """Called when mouse moves while button is held."""
        self._current_pos = (x, y)

    def on_mouse_release(self, x: int, y: int, button: int = 1) -> None:
        """Called when mouse button is released."""
        self._is_drawing = False
        self._finish_stroke(x, y, button)
        self._start_pos = None
        self._current_pos = None

    @abstractmethod
    def _finish_stroke(self, x: int, y: int, button: int) -> None:
        """Finish the drawing stroke. Override in subclass."""
        pass

    def get_color(self, button: int = 1) -> Tuple[int, int, int, int]:
        """Get color based on mouse button."""
        if button == 2:  # Right click
            return self._secondary_color
        return self._current_color

    def blend_color(
        self,
        base: Tuple[int, int, int, int],
        overlay: Tuple[int, int, int, int]
    ) -> Tuple[int, int, int, int]:
        """Blend two colors with alpha."""
        if overlay[3] == 255:
            return overlay

        alpha = overlay[3] / 255.0
        inv_alpha = 1.0 - alpha

        r = int(overlay[0] * alpha + base[0] * inv_alpha)
        g = int(overlay[1] * alpha + base[1] * inv_alpha)
        b = int(overlay[2] * alpha + base[2] * inv_alpha)
        a = int(255 * (alpha + base[3] / 255.0 * inv_alpha))

        return (r, g, b, a)

    def draw_line(
        self,
        x0: int,
        y0: int,
        x1: int,
        y1: int,
        color: Tuple[int, int, int, int],
        layer: Optional["Layer"] = None
    ) -> None:
        """Draw line using Bresenham's algorithm."""
        layer = layer or self._active_layer
        if not layer:
            return

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while True:
            self._draw_pixel(x0, y0, color, layer)

            if x0 == x1 and y0 == y1:
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def _draw_pixel(
        self,
        x: int,
        y: int,
        color: Tuple[int, int, int, int],
        layer: "Layer"
    ) -> None:
        """Draw a single pixel with brush size."""
        half_size = self._brush_size // 2

        for dy in range(-half_size, half_size + 1):
            for dx in range(-half_size, half_size + 2):
                if self._brush_size > 1:
                    # Circular brush
                    dist = (dx**2 + dy**2) ** 0.5
                    if dist > half_size:
                        continue

                px, py = x + dx, y + dy

                # Apply opacity
                if self._opacity < 1.0:
                    current = layer.get_pixel(px, py)
                    alpha = int(color[3] * self._opacity)
                    blended = self.blend_color(current, (color[0], color[1], color[2], alpha))
                    layer.set_pixel(px, py, blended)
                else:
                    layer.set_pixel(px, py, color)

    def get_cursor(self) -> str:
        """Get cursor type for this tool."""
        return "cross"

    def get_options(self) -> dict:
        """Get tool options for UI."""
        return {
            "brush_size": self._brush_size,
            "opacity": self._opacity,
        }

    def set_options(self, options: dict) -> None:
        """Set tool options from UI."""
        if "brush_size" in options:
            self.set_brush_size(options["brush_size"])
        if "opacity" in options:
            self.set_opacity(options["opacity"])
