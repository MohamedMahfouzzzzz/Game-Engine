# /**************************************************************************/
# /*  pick.py                                                               */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Color picker/eyedropper tool."""

from typing import Tuple
from engine.tools.pixel_art_editor.tools.tool_base import ToolBase


class PickTool(ToolBase):
    """Color picker from canvas."""

    def __init__(self):
        super().__init__("Pick", icon="picker")
        self._pick_all_layers: bool = True

    def on_mouse_press(self, x: int, y: int, button: int = 1) -> None:
        """Pick color at position."""
        if not self._canvas:
            return

        color = self._canvas.get_pixel(x, y, self._pick_all_layers)

        if button == 1:
            self.set_color(color)
        else:
            self.set_secondary_color(color)

        super().on_mouse_press(x, y, button)

    def _finish_stroke(self, x: int, y: int, button: int) -> None:
        """No stroke to finish for picker."""
        pass

    def get_options(self) -> dict:
        """Get tool options."""
        opts = super().get_options()
        opts["pick_all_layers"] = self._pick_all_layers
        return opts

    def set_options(self, options: dict) -> None:
        """Set tool options."""
        super().set_options(options)
        if "pick_all_layers" in options:
            self._pick_all_layers = options["pick_all_layers"]

    def get_cursor(self) -> str:
        return "crosshair"
