# /**************************************************************************/
# /*  controls/container.py                                                 */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Container - Base class for layout containers."""

from __future__ import annotations

from typing import List, Optional

from .control import Control

import logging



logger = logging.getLogger(__name__)

class Container(Control):
    """Base class for layout containers.
    
    Automatically arranges children based on layout rules.
    
    Properties:
        theme: Container theme settings
    """
    
    __slots__ = ["theme"]
    
    def __init__(self, name: str = "Container"):
        super().__init__(name)
        self.theme = {}
    
    def add_child(self, child: Control) -> None:
        """Add child control."""
        super().add_child(child)
        self._sort_children()
        self._update_layout()
    
    def remove_child(self, child: Control) -> None:
        """Remove child control."""
        super().remove_child(child)
        self._update_layout()
    
    def _sort_children(self) -> None:
        """Sort children by drawing order. Override in subclasses."""
        pass
    
    def _update_layout(self) -> None:
        """Recalculate child positions. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement _update_layout")
    
    def fit_child_in_rect(self, child: Control, rect: tuple) -> None:
        """Position child within rectangle."""
        # rect = (x, y, width, height)
        x, y, w, h = rect
        
        # Apply size flags
        child_width = child.rect_min_size[0]
        child_height = child.rect_min_size[1]
        
        if SizeFlag.FILL in getattr(child, 'size_flags_horizontal', set()):
            child_width = max(child_width, w)
        if SizeFlag.FILL in getattr(child, 'size_flags_vertical', set()):
            child_height = max(child_height, h)
        
        # Clamp to min size
        child_width = max(child_width, child.rect_min_size[0])
        child_height = max(child_height, child.rect_min_size[1])
        
        # Clamp to available space
        child_width = min(child_width, w)
        child_height = min(child_height, h)
        
        # Position based on flags
        child_x = x
        child_y = y
        
        # Update child rect
        child.rect_size = (child_width, child_height)
        # Position would be set via child's position property


__all__ = ["Container"]
