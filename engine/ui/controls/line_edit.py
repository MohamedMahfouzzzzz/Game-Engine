# /**************************************************************************/
# /*  line_edit.py                                                          */
# /**************************************************************************/

"""LineEdit - Single-line text input control."""

from __future__ import annotations
from typing import Optional
from enum import IntEnum
from .control import Control

import logging


logger = logging.getLogger(__name__)



class LineEdit(Control):
    """Single-line text input control.
    
    Properties:
        text: String - Current text
        placeholder_text: String - Placeholder when empty
        alignment: int - 0=LEFT, 1=CENTER, 2=RIGHT, 3=FILL
        max_length: int - Max character count (0=unlimited)
        editable: bool - Can edit text
        secret: bool - Password mode
        secret_character: String - Character for secrets
        context_menu_enabled: bool - Show context menu
        virtual_keyboard_enabled: bool - Show virtual keyboard
        clear_button_enabled: bool - Show clear button
        shortcut_keys_enabled: bool - Enable shortcuts
        selecting_enabled: bool - Allow selection
        deselect_on_focus_loss_enabled: bool - Clear selection on focus loss
    
    Signals:
        text_changed(new_text: String)
        text_submitted(new_text: String)
        text_change_rejected(rejected_substring: String)
    """
    
    class Alignment(IntEnum):
        LEFT = 0
        CENTER = 1
        RIGHT = 2
        FILL = 3
    
    __slots__ = [
        "text",
        "placeholder_text",
        "alignment",
        "max_length",
        "editable",
        "secret",
        "secret_character",
        "context_menu_enabled",
        "virtual_keyboard_enabled",
        "clear_button_enabled",
        "shortcut_keys_enabled",
        "selecting_enabled",
        "deselect_on_focus_loss_enabled"
    ]
    
    _SIGNALS = ["text_changed", "text_submitted", "text_change_rejected"]
    
    def __init__(self, name: str = "LineEdit"):
        super().__init__(name)
        
        self.text: str = ""
        self.placeholder_text: str = ""
        self.alignment: int = self.Alignment.LEFT
        self.max_length: int = 0
        self.editable: bool = True
        self.secret: bool = False
        self.secret_character: str = "•"
        self.context_menu_enabled: bool = True
        self.virtual_keyboard_enabled: bool = True
        self.clear_button_enabled: bool = False
        self.shortcut_keys_enabled: bool = True
        self.selecting_enabled: bool = True
        self.deselect_on_focus_loss_enabled: bool = True
    
    def clear(self) -> None:
        """Clear text."""
        if self.text:
            self.text = ""
            self.signals.emit("text_changed", "")
    
    def select_all(self) -> None:
        """Select all text."""
        pass
    
    def deselect(self) -> None:
        """Clear selection."""
        pass
    
    def set_text(self, text: str) -> None:
        """Set text."""
        if text != self.text:
            if self.max_length > 0 and len(text) > self.max_length:
                self.signals.emit("text_change_rejected", text[self.max_length:])
                text = text[:self.max_length]
            self.text = text
            self.signals.emit("text_changed", text)
    
    def submit(self) -> None:
        """Submit current text."""
        self.signals.emit("text_submitted", self.text)


__all__ = ["LineEdit"]
