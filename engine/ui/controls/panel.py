# /**************************************************************************/
# /*  controls/panel.py                                                     */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Panel - Styled panel container with background."""

from __future__ import annotations

from typing import Set, Optional, Tuple

from .control import Control, SizeFlag
from .container import Container

import logging


logger = logging.getLogger(__name__)



class Panel(Container):
    """Panel with background styling.
    
    Properties:
        background_color: Panel background color
        border_width: Border thickness
        border_color: Border color
        corner_radius: Rounded corners
    """
    
    __slots__ = [
        "background_color", "border_width", "border_color", "corner_radius",
        "size_flags_horizontal", "size_flags_vertical"
    ]
    
    def __init__(self, name: str = "Panel"):
        super().__init__(name)
        
        self.background_color: Optional[Tuple[float, float, float, float]] = None
        self.border_width = 0
        self.border_color: Optional[Tuple[float, float, float, float]] = None
        self.corner_radius = 0
        
        self.size_flags_horizontal: Set[SizeFlag] = {SizeFlag.FILL}
        self.size_flags_vertical: Set[SizeFlag] = {SizeFlag.FILL}


__all__ = ["Panel"]
