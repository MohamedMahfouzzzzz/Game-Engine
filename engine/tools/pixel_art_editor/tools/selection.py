# /**************************************************************************/
# /*  selection.py                                                          */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Selection/Marquee tool."""

from typing import Tuple
from engine.tools.pixel_art_editor.tools.tool_base import ToolBase


class SelectionTool(ToolBase):
    """Rectangular selection tool."""

    def __init__(self):
        super().__init__("Selection", icon="selection")
        self._selecting: bool = False

    def on_mouse_press(self, x: int, y: int, button: int = 1) -> None:
        """Start selection."""
        super().on_mouse_press(x, y, button)
        self._selecting = True
        if self._canvas:
            self._canvas.selection = (x, y, 0, 0)

    def on_mouse_move(self, x: int, y: int) -> None:
        """Update selection rect."""
        if self._selecting and self._start_pos and self._canvas:
            x0, y0 = self._start_pos
            left = min(x0, x)
            top = min(y0, y)
            right = max(x0, x)
            bottom = max(y0, y)
            self._canvas.selection = (left, top, right - left, bottom - y0)

        super().on_mouse_move(x, y)

    def _finish_stroke(self, x: int, y: int, button: int) -> None:
        """Finalize selection."""
        self._selecting = False
        if self._canvas and self._canvas.selection:
            x, y, w, h = self._canvas.selection
            if w == 0 or h == 0:
                self._canvas.selection = None
