# /**************************************************************************/
# /*  text.py                                                               */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Text tool for adding text to canvas."""

from typing import Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
from engine.tools.pixel_art_editor.tools.tool_base import ToolBase


class TextTool(ToolBase):
    """Text drawing tool."""

    def __init__(self):
        super().__init__("Text", icon="text")
        self._text: str = "Text"
        self._font_size: int = 10
        self._antialias: bool = False

    def _finish_stroke(self, x: int, y: int, button: int) -> None:
        """Draw text at position."""
        if not self._active_layer:
            return

        color = self.get_color(button)

        # Create temporary image for text
        img = Image.new("RGBA", (self._active_layer.width, self._active_layer.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("arial.ttf", self._font_size)
        except:
            font = ImageFont.load_default()

        # Draw text
        draw.text((x, y), self._text, fill=color, font=font)

        # Paste onto layer
        layer_img = self._active_layer._image
        layer_img = Image.alpha_composite(layer_img, img)
        self._active_layer._image = layer_img

    def set_text(self, text: str) -> None:
        """Set text to draw."""
        self._text = text

    def set_font_size(self, size: int) -> None:
        """Set font size."""
        self._font_size = max(6, min(72, size))

    def get_options(self) -> dict:
        """Get tool options."""
        opts = super().get_options()
        opts["text"] = self._text
        opts["font_size"] = self._font_size
        opts["antialias"] = self._antialias
        return opts

    def set_options(self, options: dict) -> None:
        """Set tool options."""
        super().set_options(options)
        if "text" in options:
            self._text = options["text"]
        if "font_size" in options:
            self._font_size = options["font_size"]
        if "antialias" in options:
            self._antialias = options["antialias"]
