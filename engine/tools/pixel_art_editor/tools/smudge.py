# /**************************************************************************/
# /*  smudge.py                                                             */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Smudge/blend tool."""

from typing import Tuple, List
from engine.tools.pixel_art_editor.tools.tool_base import ToolBase


class SmudgeTool(ToolBase):
    """Smudge/push pixels around."""

    def __init__(self):
        super().__init__("Smudge", icon="smudge")
        self._strength: float = 0.5
        self._last_pos: Optional[Tuple[int, int]] = None

    def on_mouse_move(self, x: int, y: int) -> None:
        """Smudge in direction of movement."""
        if self._is_drawing and self._active_layer and self._last_pos:
            lx, ly = self._last_pos

            # Push color in direction
            color = self._active_layer.get_pixel(lx, ly)
            self._draw_pixel(x, y, color, self._active_layer)

            # Fade original
            if self._strength < 1.0:
                alpha = int(color[3] * (1.0 - self._strength))
                faded = (color[0], color[1], color[2], alpha)
                self._active_layer.set_pixel(lx, ly, faded)

            self._last_pos = (x, y)

        super().on_mouse_move(x, y)

    def on_mouse_press(self, x: int, y: int, button: int = 1) -> None:
        super().on_mouse_press(x, y, button)
        self._last_pos = (x, y)

    def _finish_stroke(self, x: int, y: int, button: int) -> None:
        """End smudge."""
        self._last_pos = None
