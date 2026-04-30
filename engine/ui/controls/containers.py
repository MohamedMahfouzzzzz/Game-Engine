# /**************************************************************************/
# /*  controls/containers.py                                                */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Layout containers: HBox, VBox, Grid, Margin."""

from __future__ import annotations

from typing import List, Set
from enum import Enum, auto

from .control import Control, SizeFlag
from .container import Container

import logging



logger = logging.getLogger(__name__)

class HBoxContainer(Container):
    """Horizontal box container.
    
    Arranges children horizontally left-to-right.
    Respects EXPAND/FILL size flags.
    """
    
    __slots__ = ["separation", "alignment"]
    
    def __init__(self, name: str = "HBoxContainer"):
        super().__init__(name)
        self.separation = 4  # pixels between children
        self.alignment = "begin"  # begin, center, end
    
    def _update_layout(self) -> None:
        """Recalculate horizontal layout."""
        if not self.children:
            return
        
        available_width = self.rect_size[0]
        available_height = self.rect_size[1]
        
        # Filter to control children
        controls = [c for c in self.children if isinstance(c, Control)]
        
        if not controls:
            return
        
        # Calculate minimum widths and count expands
        total_min_width = 0
        expand_count = 0
        
        for child in controls:
            min_size = child.get_combined_minimum_size()
            total_min_width += min_size[0]
            
            flags = getattr(child, 'size_flags_horizontal', set())
            if SizeFlag.EXPAND in flags:
                expand_count += 1
        
        # Add separation
        total_min_width += self.separation * (len(controls) - 1)
        
        # Calculate extra space distribution
        extra_width = max(0, available_width - total_min_width)
        expand_width = extra_width // expand_count if expand_count > 0 else 0
        
        # Position children
        x = 0
        for child in controls:
            flags = getattr(child, 'size_flags_horizontal', set())
            
            # Determine child width
            min_size = child.get_combined_minimum_size()
            child_width = min_size[0]
            
            if SizeFlag.FILL in flags and expand_count > 0:
                child_width += expand_width
            
            # Height fills by default
            child_height = min_size[1]
            if SizeFlag.FILL in getattr(child, 'size_flags_vertical', set()):
                child_height = available_height
            
            # Set position and size
            # Note: In production, would use proper positioning system
            x += child_width + self.separation


class VBoxContainer(Container):
    """Vertical box container.
    
    Arranges children vertically top-to-bottom.
    """
    
    __slots__ = ["separation", "alignment"]
    
    def __init__(self, name: str = "VBoxContainer"):
        super().__init__(name)
        self.separation = 4
        self.alignment = "begin"
    
    def _update_layout(self) -> None:
        """Recalculate vertical layout."""
        if not self.children:
            return
        
        available_height = self.rect_size[1]
        
        controls = [c for c in self.children if isinstance(c, Control)]
        if not controls:
            return
        
        # Calculate heights
        total_min_height = 0
        expand_count = 0
        
        for child in controls:
            min_size = child.get_combined_minimum_size()
            total_min_height += min_size[1]
            
            flags = getattr(child, 'size_flags_vertical', set())
            if SizeFlag.EXPAND in flags:
                expand_count += 1
        
        total_min_height += self.separation * (len(controls) - 1)
        
        extra_height = max(0, available_height - total_min_height)
        expand_height = extra_height // expand_count if expand_count > 0 else 0
        
        # Position children
        y = 0
        for child in controls:
            flags = getattr(child, 'size_flags_vertical', set())
            
            min_size = child.get_combined_minimum_size()
            child_height = min_size[1]
            
            if SizeFlag.FILL in flags and expand_count > 0:
                child_height += expand_height
            
            y += child_height + self.separation


class GridContainer(Container):
    """Grid container with rows and columns.
    
    Properties:
        columns: Number of columns (rows auto-calculated)
    """
    
    __slots__ = ["columns"]
    
    def __init__(self, columns: int = 1, name: str = "GridContainer"):
        super().__init__(name)
        self.columns = max(1, columns)
    
    def _update_layout(self) -> None:
        """Recalculate grid layout."""
        if not self.children:
            return
        
        controls = [c for c in self.children if isinstance(c, Control)]
        if not controls:
            return
        
        # Calculate rows needed
        rows = (len(controls) + self.columns - 1) // self.columns
        
        # Calculate column widths
        col_widths = [0] * self.columns
        for i, child in enumerate(controls):
            col = i % self.columns
            min_size = child.get_combined_minimum_size()
            col_widths[col] = max(col_widths[col], min_size[0])
        
        # Calculate row heights
        row_heights = [0] * rows
        for i, child in enumerate(controls):
            row = i // self.columns
            min_size = child.get_combined_minimum_size()
            row_heights[row] = max(row_heights[row], min_size[1])
        
        # Position children
        # (Simplified - would position properly in production)


class MarginContainer(Container):
    """Container with margin padding around children."""
    
    __slots__ = ["margin_left", "margin_top", "margin_right", "margin_bottom"]
    
    def __init__(self, name: str = "MarginContainer"):
        super().__init__(name)
        self.margin_left = 0
        self.margin_top = 0
        self.margin_right = 0
        self.margin_bottom = 0
    
    def set_margin(self, left: int = 0, top: int = 0, right: int = 0, bottom: int = 0) -> None:
        """Set all margins."""
        self.margin_left = left
        self.margin_top = top
        self.margin_right = right
        self.margin_bottom = bottom
        self._update_layout()
    
    def _update_layout(self) -> None:
        """Apply margin to single child."""
        if not self.children:
            return
        
        controls = [c for c in self.children if isinstance(c, Control)]
        if not controls:
            return
        
        # Margin container typically has one child
        child = controls[0]
        
        available_width = self.rect_size[0]
        available_height = self.rect_size[1]
        
        # Calculate available space inside margins
        inner_width = available_width - self.margin_left - self.margin_right
        inner_height = available_height - self.margin_top - self.margin_bottom
        
        # Position and size child
        # (Simplified implementation)


__all__ = ["HBoxContainer", "VBoxContainer", "GridContainer", "MarginContainer"]
