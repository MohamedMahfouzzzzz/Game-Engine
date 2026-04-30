# /**************************************************************************/
# /*  circle.py                                                             */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Circle/Ellipse drawing tool."""

from typing import Tuple
import math
from engine.tools.pixel_art_editor.tools.tool_base import ToolBase


class CircleTool(ToolBase):
    """Draw circles and ellipses."""

    def __init__(self):
        super().__init__("Circle", icon="circle")
        self._filled: bool = False

    def _finish_stroke(self, x: int, y: int, button: int) -> None:
        """Draw circle."""
        if not self._start_pos or not self._active_layer:
            return

        x0, y0 = self._start_pos
        color = self.get_color(button)

        # Calculate radius
        radius = int(math.hypot(x - x0, y - y0))

        self._draw_circle(x0, y0, radius, color, self._filled)

    def _draw_circle(
        self,
        cx: int,
        cy: int,
        radius: int,
        color: Tuple[int, int, int, int],
        filled: bool
    ) -> None:
        """Draw circle using midpoint algorithm."""
        x = 0
        y = radius
        d = 3 - 2 * radius

        def draw_pixels(xc: int, yc: int, x: int, y: int) -> None:
            """Draw symmetric pixels."""
            points = [
                (xc + x, yc + y), (xc - x, yc + y),
                (xc + x, yc - y), (xc - x, yc - y),
                (xc + y, yc + x), (xc - y, yc + x),
                (xc + y, yc - x), (xc - y, yc - x),
            ]
            for px, py in points:
                self._draw_pixel(px, py, color, self._active_layer)

        if filled:
            # Fill circle
            for r in range(radius + 1):
                self._draw_circle_outline(cx, cy, r, color)
        else:
            while y >= x:
                draw_pixels(cx, cy, x, y)
                x += 1
                if d > 0:
                    y -= 1
                    d = d + 4 * (x - y) + 10
                else:
                    d = d + 4 * x + 6

    def _draw_circle_outline(
        self,
        cx: int,
        cy: int,
        radius: int,
        color: Tuple[int, int, int, int]
    ) -> None:
        """Draw just the circle outline."""
        # Use simple iteration for filled circles
        for angle in range(360):
            rad = math.radians(angle)
            x = int(cx + radius * math.cos(rad))
            y = int(cy + radius * math.sin(rad))
            self._draw_pixel(x, y, color, self._active_layer)

    def get_options(self) -> dict:
        """Get tool options."""
        opts = super().get_options()
        opts["filled"] = self._filled
        return opts

    def set_options(self, options: dict) -> None:
        """Set tool options."""
        super().set_options(options)
        if "filled" in options:
            self._filled = options["filled"]
