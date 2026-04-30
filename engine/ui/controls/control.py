# /**************************************************************************/
# /*  controls/control.py                                                   */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Control - Base UI node with anchors, margins, and focus."""

from __future__ import annotations

from enum import Enum, auto
from typing import Optional, Set, Any

from engine.core.node_base import Node
from engine.core.types import NodeType

import logging



logger = logging.getLogger(__name__)

class Anchor(Enum):
    """Anchor points for layout."""
    BEGIN = 0.0
    CENTER = 0.5
    END = 1.0
    FILL = -1.0  # Special: fill available space


class SizeFlag(Enum):
    """Size behavior flags."""
    EXPAND = auto()
    FILL = auto()
    SHRINK_CENTER = auto()
    SHRINK_END = auto()


class Margin:
    """Margin container values."""
    
    def __init__(self, left: int = 0, top: int = 0, right: int = 0, bottom: int = 0):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom
    
    def get_horizontal(self) -> int:
        return self.left + self.right
    
    def get_vertical(self) -> int:
        return self.top + self.bottom


class Control(Node):
    """Base UI control node.
    
    Properties:
        anchor_*: Position relative to parent (0-1)
        margin_*: Offset from anchor in pixels
        rect_size: Current size
        rect_min_size: Minimum size
        size_flags_*: How to behave in containers
        focus_mode: How focus behaves
        mouse_filter: How mouse events propagate
    
    Signals:
        resized, focus_entered, focus_exited
        mouse_entered, mouse_exited
        gui_input
    """
    
    __slots__ = [
        "anchor_left", "anchor_right", "anchor_top", "anchor_bottom",
        "margin_left", "margin_right", "margin_top", "margin_bottom",
        "rect_min_size", "rect_size",
        "focus_mode", "mouse_filter",
        "has_focus", "mouse_over",
        "theme_override"
    ]
    
    _SIGNALS = [
        "resized",
        "focus_entered", "focus_exited",
        "mouse_entered", "mouse_exited",
        "gui_input"
    ]
    
    def __init__(self, name: str = "Control"):
        super().__init__(name, NodeType.CONTROL)
        
        # Anchors (0.0-1.0, relative to parent)
        self.anchor_left = 0.0
        self.anchor_right = 0.0
        self.anchor_top = 0.0
        self.anchor_bottom = 0.0
        
        # Margins (pixels from anchor)
        self.margin_left = 0
        self.margin_right = 0
        self.margin_top = 0
        self.margin_bottom = 0
        
        # Size
        self.rect_min_size = (0, 0)
        self.rect_size = (100, 40)
        
        # Interaction
        self.focus_mode = "all"  # none, click, all
        self.mouse_filter = "pass"  # stop, pass, ignore
        self.has_focus = False
        self.mouse_over = False
        
        # Theme
        self.theme_override = {}
    
    def get_combined_minimum_size(self) -> tuple:
        """Get minimum size including margins."""
        return (
            self.rect_min_size[0] + self.margin_left + self.margin_right,
            self.rect_min_size[1] + self.margin_top + self.margin_bottom
        )
    
    def set_anchor_and_margin(
        self,
        side: str,
        anchor: float = None,
        margin: int = None
    ) -> None:
        """Set anchor and/or margin for a side."""
        if side == "left":
            if anchor is not None:
                self.anchor_left = anchor
            if margin is not None:
                self.margin_left = margin
        elif side == "right":
            if anchor is not None:
                self.anchor_right = anchor
            if margin is not None:
                self.margin_right = margin
        elif side == "top":
            if anchor is not None:
                self.anchor_top = anchor
            if margin is not None:
                self.margin_top = margin
        elif side == "bottom":
            if anchor is not None:
                self.anchor_bottom = anchor
            if margin is not None:
                self.margin_bottom = margin
        
        self._update_size()
    
    def _update_size(self) -> None:
        """Recalculate size from anchors."""
        # Calculate based on parent and anchors
        new_width = 100  # Default
        new_height = 40
        
        old_size = self.rect_size
        self.rect_size = (new_width, new_height)
        
        if old_size[0] != new_width or old_size[1] != new_height:
            self.signals.emit("resized", self.rect_size)
    
    def has_point(self, point: tuple) -> bool:
        """Check if point is inside control rect."""
        # Point is local to control
        return (0 <= point[0] <= self.rect_size[0] and
                0 <= point[1] <= self.rect_size[1])
    
    def grab_focus(self) -> None:
        """Take keyboard focus."""
        if self.focus_mode == "none":
            return
        self.has_focus = True
        self.signals.emit("focus_entered")
    
    def release_focus(self) -> None:
        """Give up focus."""
        if self.has_focus:
            self.has_focus = False
            self.signals.emit("focus_exited")
    
    def is_focused(self) -> bool:
        return self.has_focus
    
    def _on_mouse_enter(self) -> None:
        if not self.mouse_over:
            self.mouse_over = True
            self.signals.emit("mouse_entered")
    
    def _on_mouse_exit(self) -> None:
        if self.mouse_over:
            self.mouse_over = False
            self.signals.emit("mouse_exited")
    
    def _gui_input(self, event: Any) -> None:
        self.signals.emit("gui_input", event)


__all__ = ["Control", "Anchor", "SizeFlag", "Margin"]
