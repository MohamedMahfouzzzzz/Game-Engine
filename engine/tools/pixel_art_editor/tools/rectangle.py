# /**************************************************************************/
# /*  rectangle.py                                                          */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Rectangle drawing tool."""

from typing import Tuple
from engine.tools.pixel_art_editor.tools.tool_base import ToolBase


class RectangleTool(ToolBase):
    """Draw rectangles."""

    def __init__(self):
        super().__init__("Rectangle", icon="rectangle")
        self._filled: bool = False

    def _finish_stroke(self, x: int, y: int, button: int) -> None:
        """Draw rectangle."""
        if not self._start_pos or not self._active_layer:
            return

        x0, y0 = self._start_pos
        color = self.get_color(button)

        # Normalize corners
        left = min(x0, x)
        right = max(x0, x)
        top = min(y0, y)
        bottom = max(y0, y)

        if self._filled:
            # Fill rectangle
            for py in range(top, bottom + 1):
                for px in range(left, right + 1):
                    self._draw_pixel(px, py, color, self._active_layer)
        else:
            # Draw outline
            for px in range(left, right + 1):
                self._draw_pixel(px, top, color, self._active_layer)
                self._draw_pixel(px, bottom, color, self._active_layer)
            for py in range(top, bottom + 1):
                self._draw_pixel(left, py, color, self._active_layer)
                self._draw_pixel(right, py, color, self._active_layer)

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
