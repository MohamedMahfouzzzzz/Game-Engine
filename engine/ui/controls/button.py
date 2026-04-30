# /**************************************************************************/
# /*  controls/button.py                                                    */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Button - Clickable button control."""

from __future__ import annotations

from typing import Set

from .control import Control, SizeFlag

import logging


logger = logging.getLogger(__name__)



class Button(Control):
    """Clickable button control.
    
    Properties:
        text: Button label text
        disabled: If True, cannot be clicked
        toggle_mode: If True, stays pressed
        pressed: Current pressed state (in toggle mode)
    
    Signals:
        pressed: When clicked
        button_down, button_up: State changes
    """
    
    __slots__ = ["text", "disabled", "toggle_mode", "pressed", "size_flags_horizontal", "size_flags_vertical"]
    
    _SIGNALS = ["pressed", "button_down", "button_up"]
    
    def __init__(self, text: str = "Button", name: str = "Button"):
        super().__init__(name)
        
        self.text = text
        self.disabled = False
        self.toggle_mode = False
        self.pressed = False
        
        self.size_flags_horizontal: Set[SizeFlag] = {SizeFlag.FILL}
        self.size_flags_vertical: Set[SizeFlag] = {SizeFlag.FILL}
    
    def _on_pressed(self) -> None:
        """Handle press."""
        if self.disabled:
            return
        
        if self.toggle_mode:
            self.pressed = not self.pressed
        
        self.signals.emit("pressed")
    
    def _on_button_down(self) -> None:
        if not self.disabled:
            self.signals.emit("button_down")
    
    def _on_button_up(self) -> None:
        if not self.disabled:
            self.signals.emit("button_up")
    
    def is_pressed(self) -> bool:
        return self.pressed


__all__ = ["Button"]
