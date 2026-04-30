# /**************************************************************************/
# /*  move.py                                                               */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Move/translate tool."""

from typing import Tuple, Optional
from engine.tools.pixel_art_editor.tools.tool_base import ToolBase


class MoveTool(ToolBase):
    """Move selection or layer."""

    def __init__(self):
        super().__init__("Move", icon="move")
        self._moving: bool = False
        self._offset: Tuple[int, int] = (0, 0)

    def on_mouse_press(self, x: int, y: int, button: int = 1) -> None:
        """Start move."""
        super().on_mouse_press(x, y, button)
        if self._canvas and self._canvas.selection:
            sx, sy, sw, sh = self._canvas.selection
            if sx <= x <= sx + sw and sy <= y <= sy + sh:
                self._moving = True
                self._offset = (x - sx, y - sy)

    def on_mouse_move(self, x: int, y: int) -> None:
        """Update selection position."""
        if self._moving and self._canvas and self._canvas.selection:
            new_x = x - self._offset[0]
            new_y = y - self._offset[1]
            _, _, w, h = self._canvas.selection
            self._canvas.selection = (new_x, new_y, w, h)

        super().on_mouse_move(x, y)

    def _finish_stroke(self, x: int, y: int, button: int) -> None:
        """End move."""
        self._moving = False
