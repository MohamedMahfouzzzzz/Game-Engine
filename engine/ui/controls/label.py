# /**************************************************************************/
# /*  controls/label.py                                                     */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Label - Text display control."""

from __future__ import annotations

from typing import Set

from .control import Control, SizeFlag

import logging


logger = logging.getLogger(__name__)



class Label(Control):
    """Text display control.
    
    Properties:
        text: Display text
        align: Horizontal alignment (left, center, right)
        valign: Vertical alignment (top, center, bottom)
        autowrap: Wrap text automatically
        clip_text: Clip if text too long
        uppercase: Display in uppercase
    """
    
    __slots__ = [
        "text", "align", "valign",
        "autowrap", "clip_text", "uppercase",
        "size_flags_horizontal", "size_flags_vertical"
    ]
    
    def __init__(self, text: str = "", name: str = "Label"):
        super().__init__(name)
        
        self.text = text
        self.align = "left"  # left, center, right, fill
        self.valign = "top"  # top, center, bottom, fill
        
        self.autowrap = False
        self.clip_text = False
        self.uppercase = False
        
        self.size_flags_horizontal: Set[SizeFlag] = set()
        self.size_flags_vertical: Set[SizeFlag] = set()
    
    def get_line_count(self) -> int:
        """Get number of visible lines."""
        if not self.text:
            return 0
        return self.text.count('\n') + 1


__all__ = ["Label"]
