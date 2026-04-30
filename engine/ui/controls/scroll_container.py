# /**************************************************************************/
# /*  scroll_container.py                                                   */
# /**************************************************************************/

"""ScrollContainer - Scrollable container."""

from __future__ import annotations
from enum import IntEnum
from typing import Optional
from .container import Container

import logging


logger = logging.getLogger(__name__)



class ScrollContainer(Container):
    """Scrollable container with scrollbars.
    
    Properties:
        follow_focus: bool - Auto-scroll to focused child
        scroll_horizontal: int - Horizontal scroll position
        scroll_vertical: int - Vertical scroll position
        scroll_horizontal_custom_step: float - Custom horizontal step
        scroll_vertical_custom_step: float - Custom vertical step
        horizontal_scroll_mode: int - 0=DISABLED, 1=AUTO, 2=ALWAYS, 3=NEVER
        vertical_scroll_mode: int - 0=DISABLED, 1=AUTO, 2=ALWAYS, 3=NEVER
    
    Signals:
        scroll_started
        scroll_ended
    """
    
    class ScrollMode(IntEnum):
        DISABLED = 0
        AUTO = 1
        ALWAYS = 2
        NEVER = 3
    
    __slots__ = [
        "follow_focus",
        "scroll_horizontal",
        "scroll_vertical",
        "scroll_horizontal_custom_step",
        "scroll_vertical_custom_step",
        "horizontal_scroll_mode",
        "vertical_scroll_mode",
        "_scrolling"
    ]
    
    _SIGNALS = ["scroll_started", "scroll_ended"]
    
    def __init__(self, name: str = "ScrollContainer"):
        super().__init__(name)
        
        self.follow_focus: bool = True
        self.scroll_horizontal: int = 0
        self.scroll_vertical: int = 0
        self.scroll_horizontal_custom_step: float = -1.0
        self.scroll_vertical_custom_step: float = -1.0
        self.horizontal_scroll_mode: int = self.ScrollMode.AUTO
        self.vertical_scroll_mode: int = self.ScrollMode.AUTO
        
        self._scrolling: bool = False
    
    def set_h_scroll(self, value: int) -> None:
        """Set horizontal scroll."""
        if value != self.scroll_horizontal:
            if not self._scrolling:
                self._scrolling = True
                self.signals.emit("scroll_started")
            self.scroll_horizontal = max(0, value)
    
    def set_v_scroll(self, value: int) -> None:
        """Set vertical scroll."""
        if value != self.scroll_vertical:
            if not self._scrolling:
                self._scrolling = True
                self.signals.emit("scroll_started")
            self.scroll_vertical = max(0, value)
    
    def scroll_to_child(self, child: Control) -> None:
        """Scroll to make child visible."""
        pass
    
    def ensure_control_visible(self, control: Control) -> None:
        """Scroll to ensure control is visible."""
        pass


__all__ = ["ScrollContainer"]
