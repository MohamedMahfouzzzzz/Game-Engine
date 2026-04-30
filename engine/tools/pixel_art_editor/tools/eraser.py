# /**************************************************************************/
# /*  eraser.py                                                             */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Eraser tool."""

from engine.tools.pixel_art_editor.tools.tool_base import ToolBase


class EraserTool(ToolBase):
    """Eraser that removes pixels."""

    def __init__(self):
        super().__init__("Eraser", icon="eraser")

    def on_mouse_move(self, x: int, y: int) -> None:
        if self._is_drawing and self._active_layer:
            color = (0, 0, 0, 0)  # Transparent
            self._draw_pixel(x, y, color, self._active_layer)

        super().on_mouse_move(x, y)

    def _finish_stroke(self, x: int, y: int, button: int) -> None:
        """Eraser doesn't need special finish."""
        pass
