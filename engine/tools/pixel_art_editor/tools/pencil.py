# /**************************************************************************/
# /*  pencil.py                                                             */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Pencil/Brush tool for drawing."""

from typing import List, Tuple
from engine.tools.pixel_art_editor.tools.tool_base import ToolBase

import logging


logger = logging.getLogger(__name__)



class PencilTool(ToolBase):
    """Freehand drawing tool."""

    def __init__(self):
        super().__init__("Pencil", icon="pencil")
        self._stroke_points: List[Tuple[int, int]] = []

    def on_mouse_press(self, x: int, y: int, button: int = 1) -> None:
        super().on_mouse_press(x, y, button)
        self._stroke_points = [(x, y)]

    def on_mouse_move(self, x: int, y: int) -> None:
        if self._is_drawing and self._canvas:
            # Interpolate between last point and current
            if self._stroke_points:
                last_x, last_y = self._stroke_points[-1]
                color = self.get_color(1)

                # Draw line between points
                self.draw_line(last_x, last_y, x, y, color)

            self._stroke_points.append((x, y))

        super().on_mouse_move(x, y)

    def _finish_stroke(self, x: int, y: int, button: int) -> None:
        """Finish the stroke."""
        self._stroke_points.clear()
