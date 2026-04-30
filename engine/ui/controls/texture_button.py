# /**************************************************************************/
# /*  texture_button.py                                                     */
# /**************************************************************************/

"""TextureButton - Button with texture states."""

from __future__ import annotations
from typing import Optional
from enum import IntEnum
from .control import Control

import logging



logger = logging.getLogger(__name__)

class BitMap:
    """Bitmap for click mask."""
    pass


class TextureButton(Control):
    """Button with texture states.
    
    Properties:
        texture_normal: Texture2D - Normal state texture
        texture_pressed: Texture2D - Pressed state texture
        texture_hover: Texture2D - Hover state texture
        texture_disabled: Texture2D - Disabled state texture
        texture_focused: Texture2D - Focused state texture
        texture_click_mask: BitMap - Click detection mask
        stretch_mode: int - 0=SCALE_ON_EXPAND, 1=SCALE, 2=TILE, 3=KEEP, 4=KEEP_CENTERED, 5=KEEP_ASPECT, 6=KEEP_ASPECT_CENTERED, 7=KEEP_ASPECT_COVERED
    
    Signals:
        pressed
        button_down
        button_up
        toggled(toggled_on: bool)
    """
    
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
        "texture_normal",
        "texture_pressed",
        "texture_hover",
        "texture_disabled",
        "texture_focused",
        "texture_click_mask",
        "stretch_mode",
        "_toggle_mode",
        "_toggled"
    ]
    
    _SIGNALS = ["pressed", "button_down", "button_up", "toggled"]
    
    def __init__(self, name: str = "TextureButton"):
        super().__init__(name)
        
        self.texture_normal = None
        self.texture_pressed = None
        self.texture_hover = None
        self.texture_disabled = None
        self.texture_focused = None
        self.texture_click_mask: Optional[BitMap] = None
        self.stretch_mode: int = self.StretchMode.SCALE
        
        self._toggle_mode: bool = False
        self._toggled: bool = False
    
    @property
    def toggle_mode(self) -> bool:
        return self._toggle_mode
    
    @toggle_mode.setter
    def toggle_mode(self, value: bool) -> None:
        self._toggle_mode = value
    
    @property
    def toggled(self) -> bool:
        return self._toggled
    
    def set_pressed(self, pressed: bool) -> None:
        """Set pressed state in toggle mode."""
        if self._toggle_mode and pressed != self._toggled:
            self._toggled = pressed
            self.signals.emit("toggled", pressed)


__all__ = ["TextureButton"]
