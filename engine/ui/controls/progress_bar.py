# /**************************************************************************/
# /*  progress_bar.py                                                       */
# /**************************************************************************/

"""ProgressBar - Value display with progress indication."""

from __future__ import annotations
from enum import IntEnum
from .control import Control

import logging


logger = logging.getLogger(__name__)



class ProgressBar(Control):
    """Value display with progress indication.
    
    Properties:
        value: float - Current value
        min_value: float - Minimum value
        max_value: float - Maximum value
        step: float - Step increment
        page: float - Page size for scrollable
        exp_edit: bool - Exponential editing
        rounded: bool - Use integers
        allow_greater: bool - Allow > max
        allow_lesser: bool - Allow < min
        fill_mode: int - 0=BEGIN_TO_END, 1=END_TO_BEGIN, 2=TOP_TO_BOTTOM, 3=BOTTOM_TO_TOP
        show_percentage: bool - Show percentage text
    
    Signals:
        value_changed(value: float)
        changed
    """
    
    class FillMode(IntEnum):
        BEGIN_TO_END = 0
        END_TO_BEGIN = 1
        TOP_TO_BOTTOM = 2
        BOTTOM_TO_TOP = 3
    
    __slots__ = [
        "value",
        "min_value",
        "max_value",
        "step",
        "page",
        "exp_edit",
        "rounded",
        "allow_greater",
        "allow_lesser",
        "fill_mode",
        "show_percentage"
    ]
    
    _SIGNALS = ["value_changed", "changed"]
    
    def __init__(self, name: str = "ProgressBar"):
        super().__init__(name)
        
        self.value: float = 0.0
        self.min_value: float = 0.0
        self.max_value: float = 100.0
        self.step: float = 1.0
        self.page: float = 0.0
        self.exp_edit: bool = False
        self.rounded: bool = False
        self.allow_greater: bool = False
        self.allow_lesser: bool = False
        self.fill_mode: int = self.FillMode.BEGIN_TO_END
        self.show_percentage: bool = True
    
    def set_value(self, value: float) -> None:
        """Set value with clamping."""
        if not self.allow_lesser and value < self.min_value:
            value = self.min_value
        if not self.allow_greater and value > self.max_value:
            value = self.max_value
        
        if self.rounded:
            value = round(value)
        
        if value != self.value:
            self.value = value
            self.signals.emit("value_changed", value)
            self.signals.emit("changed")
    
    def get_as_ratio(self) -> float:
        """Get value as 0.0-1.0 ratio."""
        if self.max_value == self.min_value:
            return 0.0
        return (self.value - self.min_value) / (self.max_value - self.min_value)
    
    def get_percentage(self) -> float:
        """Get value as percentage."""
        return self.get_as_ratio() * 100.0


__all__ = ["ProgressBar"]
