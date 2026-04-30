# /**************************************************************************/
# /*  gradient.py                                                           */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Gradient drawing tool."""

from typing import Tuple
from engine.tools.pixel_art_editor.tools.tool_base import ToolBase


class GradientTool(ToolBase):
    """Linear and radial gradients."""

    def __init__(self):
        super().__init__("Gradient", icon="gradient")
        self._gradient_type: str = "linear"  # linear, radial

    def _finish_stroke(self, x: int, y: int, button: int) -> None:
        """Apply gradient."""
        if not self._start_pos or not self._active_layer:
            return

        x0, y0 = self._start_pos
        color1 = self._current_color
        color2 = self._secondary_color

        if self._gradient_type == "linear":
            self._apply_linear_gradient(x0, y0, x, y, color1, color2)
        else:
            self._apply_radial_gradient(x0, y0, x, y, color1, color2)

    def _apply_linear_gradient(
        self,
        x0: int,
        y0: int,
        x1: int,
        y1: int,
        color1: Tuple[int, int, int, int],
        color2: Tuple[int, int, int, int]
    ) -> None:
        """Apply linear gradient."""
        dx = x1 - x0
        dy = y1 - y0
        length_sq = dx*dx + dy*dy

        for py in range(self._active_layer.height):
            for px in range(self._active_layer.width):
                # Project point onto gradient line
                if length_sq > 0:
                    t = ((px - x0) * dx + (py - y0) * dy) / length_sq
                    t = max(0.0, min(1.0, t))
                else:
                    t = 0.0

                color = self._interpolate_color(color1, color2, t)
                self._active_layer.set_pixel(px, py, color)

    def _apply_radial_gradient(
        self,
        cx: int,
        cy: int,
        ex: int,
        ey: int,
        color1: Tuple[int, int, int, int],
        color2: Tuple[int, int, int, int]
    ) -> None:
        """Apply radial gradient."""
        max_radius = ((ex - cx) ** 2 + (ey - cy) ** 2) ** 0.5

        for py in range(self._active_layer.height):
            for px in range(self._active_layer.width):
                dist = ((px - cx) ** 2 + (py - cy) ** 2) ** 0.5
                t = min(1.0, dist / max_radius) if max_radius > 0 else 0.0

                color = self._interpolate_color(color1, color2, t)
                self._active_layer.set_pixel(px, py, color)

    def _interpolate_color(
        self,
        c1: Tuple[int, int, int, int],
        c2: Tuple[int, int, int, int],
        t: float
    ) -> Tuple[int, int, int, int]:
        """Interpolate between two colors."""
        return (
            int(c1[0] + (c2[0] - c1[0]) * t),
            int(c1[1] + (c2[1] - c1[1]) * t),
            int(c1[2] + (c2[2] - c1[2]) * t),
            int(c1[3] + (c2[3] - c1[3]) * t),
        )
