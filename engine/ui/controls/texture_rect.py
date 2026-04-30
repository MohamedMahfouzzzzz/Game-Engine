# /**************************************************************************/
# /*  texture_rect.py                                                       */
# /**************************************************************************/

"""TextureRect - Texture display control."""

from __future__ import annotations
from typing import Optional
from enum import IntEnum
from .control import Control

import logging


logger = logging.getLogger(__name__)



class TextureRect(Control):
    """Texture display control.
    
    Properties:
        texture: Texture2D - Display texture
        expand_mode: int - 0=KEEP_SIZE, 1=EXPAND, 2=IGNORE_SIZE
        stretch_mode: int - 0=SCALE_ON_EXPAND, 1=SCALE, 2=TILE, 3=KEEP, 4=KEEP_CENTERED, 5=KEEP_ASPECT, 6=KEEP_ASPECT_CENTERED, 7=KEEP_ASPECT_COVERED
        flip_h: bool - Horizontal flip
        flip_v: bool - Vertical flip
    """
    
    class ExpandMode(IntEnum):
        KEEP_SIZE = 0
        EXPAND = 1
        IGNORE_SIZE = 2
    
    class StretchMode(IntEnum):
        SCALE_ON_EXPAND = 0
        SCALE = 1
        TILE = 2
        KEEP = 3
        KEEP_CENTERED = 4
        KEEP_ASPECT = 5
        KEEP_ASPECT_CENTERED = 6
        KEEP_ASPECT_COVERED = 7
    
    __slots__ = [
        "texture",
        "expand_mode",
        "stretch_mode",
        "flip_h",
        "flip_v"
    ]
    
    def __init__(self, name: str = "TextureRect"):
        super().__init__(name)
        
        self.texture = None
        self.expand_mode: int = self.ExpandMode.KEEP_SIZE
        self.stretch_mode: int = self.StretchMode.SCALE_ON_EXPAND
        self.flip_h: bool = False
        self.flip_v: bool = False


__all__ = ["TextureRect"]
