# /**************************************************************************/
# /*  fill.py                                                               */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Bucket fill tool."""

from typing import List, Tuple, Set
from engine.tools.pixel_art_editor.tools.tool_base import ToolBase


class FillTool(ToolBase):
    """Flood fill / bucket fill tool."""

    def __init__(self):
        super().__init__("Fill", icon="fill")
        self._tolerance: int = 0
        self._contiguous: bool = True

    def _finish_stroke(self, x: int, y: int, button: int) -> None:
        """Perform flood fill."""
        if not self._active_layer:
            return

        target_color = self._active_layer.get_pixel(x, y)
        fill_color = self.get_color(button)

        if target_color == fill_color:
            return

        if self._contiguous:
            self._flood_fill(x, y, target_color, fill_color)
        else:
            self._fill_all(target_color, fill_color)

    def _flood_fill(
        self,
        start_x: int,
        start_y: int,
        target_color: Tuple[int, int, int, int],
        fill_color: Tuple[int, int, int, int]
    ) -> None:
        """Flood fill using stack-based algorithm."""
        stack: List[Tuple[int, int]] = [(start_x, start_y)]
        filled: Set[Tuple[int, int]] = set()
        width, height = self._active_layer.width, self._active_layer.height

        while stack:
            x, y = stack.pop()

            if (x, y) in filled or x < 0 or x >= width or y < 0 or y >= height:
                continue

            current = self._active_layer.get_pixel(x, y)
            if not self._colors_match(current, target_color):
                continue

            self._active_layer.set_pixel(x, y, fill_color)
            filled.add((x, y))

            # Add neighbors
            stack.append((x + 1, y))
            stack.append((x - 1, y))
            stack.append((x, y + 1))
            stack.append((x, y - 1))

    def _fill_all(
        self,
        target_color: Tuple[int, int, int, int],
        fill_color: Tuple[int, int, int, int]
    ) -> None:
        """Replace all matching colors globally."""
        for y in range(self._active_layer.height):
            for x in range(self._active_layer.width):
                current = self._active_layer.get_pixel(x, y)
                if self._colors_match(current, target_color):
                    self._active_layer.set_pixel(x, y, fill_color)

    def _colors_match(
        self,
        c1: Tuple[int, int, int, int],
        c2: Tuple[int, int, int, int]
    ) -> bool:
        """Check if colors match within tolerance."""
        if self._tolerance == 0:
            return c1 == c2

        return all(abs(a - b) <= self._tolerance for a, b in zip(c1, c2))

    def get_options(self) -> dict:
        """Get tool options."""
        opts = super().get_options()
        opts["tolerance"] = self._tolerance
        opts["contiguous"] = self._contiguous
        return opts

    def set_options(self, options: dict) -> None:
        """Set tool options."""
        super().set_options(options)
        if "tolerance" in options:
            self._tolerance = max(0, min(255, options["tolerance"]))
        if "contiguous" in options:
            self._contiguous = options["contiguous"]
