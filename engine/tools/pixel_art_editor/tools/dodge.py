# /**************************************************************************/
# /*  dodge.py                                                              */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Dodge (lighten) tool."""

from typing import Tuple
from engine.tools.pixel_art_editor.tools.tool_base import ToolBase


class DodgeTool(ToolBase):
    """Lighten/dodge tool for highlights."""

    def __init__(self):
        super().__init__("Dodge", icon="dodge")
        self._exposure: float = 0.5

    def on_mouse_move(self, x: int, y: int) -> None:
        """Lighten pixels."""
        if self._is_drawing and self._active_layer:
            for dy in range(-self._brush_size, self._brush_size + 1):
                for dx in range(-self._brush_size, self._brush_size + 1):
                    px, py = x + dx, y + dy
                    if dx*dx + dy*dy > self._brush_size*self._brush_size:
                        continue

                    current = self._active_layer.get_pixel(px, py)
                    if current[3] == 0:
                        continue

                    # Lighten
                    factor = 1.0 + self._exposure * self._opacity
                    new_color = (
                        min(255, int(current[0] * factor)),
                        min(255, int(current[1] * factor)),
                        min(255, int(current[2] * factor)),
                        current[3]
                    )
                    self._active_layer.set_pixel(px, py, new_color)

        super().on_mouse_move(x, y)

    def _finish_stroke(self, x: int, y: int, button: int) -> None:
        """Dodge applies immediately."""
        pass
