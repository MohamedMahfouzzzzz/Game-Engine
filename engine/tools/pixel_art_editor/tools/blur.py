# /**************************************************************************/
# /*  blur.py                                                               */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Blur/soften tool."""

from typing import Tuple
from engine.tools.pixel_art_editor.tools.tool_base import ToolBase


class BlurTool(ToolBase):
    """Gaussian blur effect."""

    def __init__(self):
        super().__init__("Blur", icon="blur")
        self._radius: int = 2

    def on_mouse_press(self, x: int, y: int, button: int = 1) -> None:
        """Apply blur."""
        super().on_mouse_press(x, y, button)
        self._apply_blur(x, y)

    def _apply_blur(self, x: int, y: int) -> None:
        """Apply simple box blur at position."""
        if not self._active_layer:
            return

        r = self._radius

        for py in range(y - r, y + r + 1):
            for px in range(x - r, x + r + 1):
                if px < 0 or px >= self._active_layer.width:
                    continue
                if py < 0 or py >= self._active_layer.height:
                    continue

                # Simple box blur
                total = [0, 0, 0, 0]
                count = 0

                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        nx, ny = px + dx, py + dy
                        if 0 <= nx < self._active_layer.width and 0 <= ny < self._active_layer.height:
                            c = self._active_layer.get_pixel(nx, ny)
                            for i in range(4):
                                total[i] += c[i]
                            count += 1

                if count > 0:
                    blurred = tuple(t // count for t in total)
                    self._active_layer.set_pixel(px, py, blurred)

    def _finish_stroke(self, x: int, y: int, button: int) -> None:
        """Blur is applied immediately."""
        pass
