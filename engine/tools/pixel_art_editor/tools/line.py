# /**************************************************************************/
# /*  line.py                                                               */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Line drawing tool."""

from engine.tools.pixel_art_editor.tools.tool_base import ToolBase


class LineTool(ToolBase):
    """Draw straight lines."""

    def __init__(self):
        super().__init__("Line", icon="line")
        self._preview_layer = None

    def on_mouse_move(self, x: int, y: int) -> None:
        if self._is_drawing and self._start_pos:
            # Could draw preview line here
            pass
        super().on_mouse_move(x, y)

    def _finish_stroke(self, x: int, y: int, button: int) -> None:
        """Draw final line."""
        if self._start_pos and self._active_layer:
            x0, y0 = self._start_pos
            color = self.get_color(button)
            self.draw_line(x0, y0, x, y, color)
