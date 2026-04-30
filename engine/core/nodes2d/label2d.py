# /**************************************************************************/
# /*  label2d.py                                                             */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Label2D - Text rendering node."""

from __future__ import annotations

from typing import Optional

from .types import Vector2, Color
from .node2d import Node2D

import logging


logger = logging.getLogger(__name__)


class Label2D(Node2D):
    """Text label node for displaying text in 2D space.
    
    Properties:
        text: The text to display (str)
        font_size: Size of the text in pixels (int)
        font_family: Font family name (str)
        color: Text color (Color)
        outline_color: Outline color (Color)
        outline_size: Outline thickness in pixels (int)
        horizontal_alignment: Text alignment - left, center, right (str)
        vertical_alignment: Text alignment - top, center, bottom (str)
        line_spacing: Space between lines (int)
        max_width: Maximum width before wrapping, 0 for no wrap (int)
        uppercase: Convert text to uppercase (bool)
        
    Signals:
        text_changed: Emitted when text changes
    """
    
    __slots__ = [
        "text", "font_size", "font_family",
        "color", "outline_color", "outline_size",
        "horizontal_alignment", "vertical_alignment",
        "line_spacing", "max_width", "uppercase",
        "_text_size"
    ]
    
    _SIGNALS = ["text_changed"]
    
    def __init__(self, name: str = "Label2D"):
        super().__init__(name)
        self.node_type = "Label2D"
        
        # Text content
        self.text: str = "Label"
        self.font_size: int = 16
        self.font_family: str = "Arial"
        
        # Appearance
        self.color: Color = Color.white()
        self.outline_color: Color = Color.black()
        self.outline_size: int = 0
        
        # Alignment
        self.horizontal_alignment: str = "center"  # "left", "center", "right"
        self.vertical_alignment: str = "center"  # "top", "center", "bottom"
        
        # Layout
        self.line_spacing: int = 3
        self.max_width: int = 0  # 0 = no wrapping
        self.uppercase: bool = False
        
        # Cached size
        self._text_size: tuple = (0, 0)
    
    def set_text(self, text: str) -> None:
        """Set the label text."""
        if self.text != text:
            self.text = text.upper() if self.uppercase else text
            self._text_size = self._calculate_size()
            self.signals.emit("text_changed", self.text)
    
    def append_text(self, text: str) -> None:
        """Append text to current label."""
        self.set_text(self.text + text)
    
    def get_text(self) -> str:
        """Get current text."""
        return self.text
    
    def set_font(self, family: str, size: int) -> None:
        """Set font family and size."""
        self.font_family = family
        self.font_size = size
        self._text_size = self._calculate_size()
    
    def set_color(self, color: Color) -> None:
        """Set text color."""
        self.color = color
    
    def set_color_rgb(self, r: int, g: int, b: int) -> None:
        """Set text color from RGB values."""
        self.color = Color(r, g, b)
    
    def set_outline(self, color: Color, size: int) -> None:
        """Set text outline."""
        self.outline_color = color
        self.outline_size = size
    
    def set_alignment(self, horizontal: str, vertical: str) -> None:
        """Set text alignment.
        
        horizontal: "left", "center", "right"
        vertical: "top", "center", "bottom"
        """
        self.horizontal_alignment = horizontal
        self.vertical_alignment = vertical
    
    def set_max_width(self, width: int) -> None:
        """Set maximum text width (0 for unlimited)."""
        self.max_width = width
        self._text_size = self._calculate_size()
    
    def _calculate_size(self) -> tuple:
        """Calculate text size."""
        lines = self.text.split('\n')
        # Rough estimation: width ~ font_size * 0.6 * max_line_length
        max_chars = max(len(line) for line in lines) if lines else 0
        width = max_chars * self.font_size * 0.6
        height = len(lines) * (self.font_size + self.line_spacing)
        return (int(width), int(height))
    
    def get_size(self) -> tuple:
        """Get text size in pixels."""
        return self._text_size
    
    def get_line_count(self) -> int:
        """Get number of lines."""
        return len(self.text.split('\n'))
    
    def _draw(self, renderer) -> None:
        """Draw the label text."""
        if not self.visible or not self.text:
            return
        
        # Get global position
        pos = self.get_global_position()
        
        # Calculate offset based on alignment
        text_w, text_h = self._text_size
        
        if self.horizontal_alignment == "center":
            x_offset = -text_w / 2
        elif self.horizontal_alignment == "right":
            x_offset = -text_w
        else:  # left
            x_offset = 0
        
        if self.vertical_alignment == "center":
            y_offset = -text_h / 2
        elif self.vertical_alignment == "bottom":
            y_offset = -text_h
        else:  # top
            y_offset = 0
        
        # Draw text via renderer
        if hasattr(renderer, 'draw_text'):
            renderer.draw_text(
                text=self.text,
                position=Vector2(pos.x + x_offset, pos.y + y_offset),
                font_size=self.font_size,
                color=self.color,
                outline_color=self.outline_color if self.outline_size > 0 else None,
                outline_size=self.outline_size
            )
