# /**************************************************************************/
# /*  shape.py                                                              */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Generic shape drawing tool."""

from typing import Tuple
from engine.tools.pixel_art_editor.tools.tool_base import ToolBase


class ShapeTool(ToolBase):
    """Draw predefined shapes."""

    def __init__(self):
        super().__init__("Shape", icon="shape")
        self._shape_type: str = "star"  # star, heart, arrow, etc.

    def _finish_stroke(self, x: int, y: int, button: int) -> None:
        """Draw shape."""
        if not self._start_pos or not self._active_layer:
            return

        x0, y0 = self._start_pos
        color = self.get_color(button)

        if self._shape_type == "star":
            self._draw_star(x0, y0, x, y, color)
        elif self._shape_type == "heart":
            self._draw_heart(x0, y0, x, y, color)

    def _draw_star(self, cx: int, cy: int, ex: int, ey: int, color: Tuple[int, int, int, int]) -> None:
        """Draw star shape."""
        import math
        radius = int(((ex - cx) ** 2 + (ey - cy) ** 2) ** 0.5)

        for i in range(10):
            angle = math.radians(i * 36 - 90)
            r = radius if i % 2 == 0 else radius // 2
            x = cx + int(r * math.cos(angle))
            y = cy + int(r * math.sin(angle))
            self._draw_pixel(x, y, color, self._active_layer)

    def _draw_heart(self, x0: int, y0: int, x1: int, y1: int, color: Tuple[int, int, int, int]) -> None:
        """Draw heart shape."""
        cx = (x0 + x1) // 2
        cy = (y0 + y1) // 2
        w = abs(x1 - x0) // 2
        h = abs(y1 - y0) // 2

        for y in range(-h, h):
            for x in range(-w, w):
                nx, ny = x / w, y / h
                if (nx**2 + ny**2 - 1)**3 - nx**2 * ny**3 <= 0:
                    self._draw_pixel(cx + x, cy + y, color, self._active_layer)
