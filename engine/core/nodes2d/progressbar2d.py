# /**************************************************************************/
# /*  progressbar2d.py                                                       */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""ProgressBar2D - Progress bar widget node."""

from __future__ import annotations

from typing import Optional

from .types import Vector2, Color
from .node2d import Node2D

import logging


logger = logging.getLogger(__name__)


class ProgressBar2D(Node2D):
    """Progress bar widget for displaying progress values.
    
    Properties:
        value: Current progress value (float)
        min_value: Minimum value (float)
        max_value: Maximum value (float)
        step: Step increment value (float)
        show_percentage: Show percentage text (bool)
        width: Bar width in pixels (int)
        height: Bar height in pixels (int)
        bg_color: Background color (Color)
        fill_color: Fill/progress color (Color)
        border_color: Border color (Color)
        border_width: Border thickness (int)
        
    Signals:
        value_changed: Emitted when value changes
    """
    
    __slots__ = [
        "value", "min_value", "max_value", "step",
        "show_percentage",
        "width", "height",
        "bg_color", "fill_color", "border_color", "border_width"
    ]
    
    _SIGNALS = ["value_changed"]
    
    def __init__(self, name: str = "ProgressBar2D"):
        super().__init__(name)
        self.node_type = "ProgressBar2D"
        
        # Value range
        self.value: float = 0.0
        self.min_value: float = 0.0
        self.max_value: float = 100.0
        self.step: float = 1.0
        
        # Display
        self.show_percentage: bool = True
        
        # Size
        self.width: int = 200
        self.height: int = 24
        
        # Colors
        self.bg_color: Color = Color(60, 60, 60)
        self.fill_color: Color = Color(100, 200, 100)
        self.border_color: Color = Color(100, 100, 100)
        self.border_width: int = 2
    
    def set_value(self, value: float) -> None:
        """Set the progress value."""
        # Clamp to range
        new_value = max(self.min_value, min(self.max_value, value))
        
        # Round to step
        if self.step > 0:
            steps = round((new_value - self.min_value) / self.step)
            new_value = self.min_value + steps * self.step
        
        if new_value != self.value:
            self.value = new_value
            self.signals.emit("value_changed", self.value)
    
    def get_value(self) -> float:
        """Get current value."""
        return self.value
    
    def set_range(self, min_val: float, max_val: float) -> None:
        """Set the value range."""
        self.min_value = min_val
        self.max_value = max_val
        self.set_value(self.value)  # Re-clamp current value
    
    def get_percentage(self) -> float:
        """Get percentage (0.0 to 100.0)."""
        if self.max_value == self.min_value:
            return 0.0
        return ((self.value - self.min_value) / (self.max_value - self.min_value)) * 100.0
    
    def increment(self) -> None:
        """Increment by step value."""
        self.set_value(self.value + self.step)
    
    def decrement(self) -> None:
        """Decrement by step value."""
        self.set_value(self.value - self.step)
    
    def set_as_ratio(self, ratio: float) -> None:
        """Set value as ratio 0.0-1.0."""
        value = self.min_value + ratio * (self.max_value - self.min_value)
        self.set_value(value)
    
    def set_colors(self, bg: Color, fill: Color, border: Optional[Color] = None) -> None:
        """Set bar colors."""
        self.bg_color = bg
        self.fill_color = fill
        if border:
            self.border_color = border
    
    def get_fill_width(self) -> int:
        """Get width of filled portion."""
        ratio = self.get_percentage() / 100.0
        fill_w = int((self.width - self.border_width * 2) * ratio)
        return max(0, fill_w)
    
    def _draw(self, renderer) -> None:
        """Draw the progress bar."""
        if not self.visible:
            return
        
        pos = self.get_global_position()
        x = pos.x - self.width / 2
        y = pos.y - self.height / 2
        
        # Draw border
        if self.border_width > 0:
            if hasattr(renderer, 'draw_rect'):
                renderer.draw_rect(
                    x, y, self.width, self.height,
                    self.border_color, filled=True
                )
        
        # Draw background
        inner_x = x + self.border_width
        inner_y = y + self.border_width
        inner_w = self.width - self.border_width * 2
        inner_h = self.height - self.border_width * 2
        
        if hasattr(renderer, 'draw_rect'):
            renderer.draw_rect(
                inner_x, inner_y, inner_w, inner_h,
                self.bg_color, filled=True
            )
        
        # Draw fill
        fill_w = self.get_fill_width()
        if fill_w > 0 and hasattr(renderer, 'draw_rect'):
            renderer.draw_rect(
                inner_x, inner_y, fill_w, inner_h,
                self.fill_color, filled=True
            )
    
    def contains_point(self, point: Vector2) -> bool:
        """Check if point is inside progress bar."""
        pos = self.get_global_position()
        x = pos.x - self.width / 2
        y = pos.y - self.height / 2
        return x <= point.x <= x + self.width and y <= point.y <= y + self.height
