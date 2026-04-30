# /**************************************************************************/
# /*  rich_text_label.py                                                    */
# /**************************************************************************/

"""RichTextLabel - BBCode-enabled rich text display."""

from __future__ import annotations
from typing import Optional, Any
from enum import IntEnum
from .control import Control

import logging


logger = logging.getLogger(__name__)



class RichTextLabel(Control):
    """Rich text with BBCode support.
    
    Properties:
        bbcode_enabled: bool - Parse BBCode tags
        text: String - Display text
        fit_content: bool - Auto-resize to content
        scroll_active: bool - Allow scrolling
        scroll_following: bool - Auto-scroll to bottom
        autowrap_mode: int - 0=OFF, 1=ARBITRARY, 2=WORD, 3=WORD_SMART
        tab_size: int - Tab character width
        context_menu_enabled: bool - Show context menu
        selection_enabled: bool - Allow text selection
    
    Signals:
        meta_clicked(meta: Variant)
        meta_hover_started(meta: Variant)
        meta_hover_ended(meta: Variant)
        finished
    """
    
    class AutowrapMode(IntEnum):
        OFF = 0
        ARBITRARY = 1
        WORD = 2
        WORD_SMART = 3
    
    __slots__ = [
        "bbcode_enabled",
        "text",
        "fit_content",
        "scroll_active",
        "scroll_following",
        "autowrap_mode",
        "tab_size",
        "context_menu_enabled",
        "selection_enabled"
    ]
    
    _SIGNALS = ["meta_clicked", "meta_hover_started", "meta_hover_ended", "finished"]
    
    def __init__(self, name: str = "RichTextLabel"):
        super().__init__(name)
        
        self.bbcode_enabled: bool = False
        self.text: str = ""
        self.fit_content: bool = False
        self.scroll_active: bool = True
        self.scroll_following: bool = False
        self.autowrap_mode: int = self.AutowrapMode.OFF
        self.tab_size: int = 4
        self.context_menu_enabled: bool = True
        self.selection_enabled: bool = False
    
    def clear(self) -> None:
        """Clear all text."""
        self.text = ""
    
    def add_text(self, text: str) -> None:
        """Append text."""
        self.text += text
    
    def add_image(self, image: Any, width: int = 0, height: int = 0) -> None:
        """Add inline image."""
        pass
    
    def push_meta(self, data: Any) -> None:
        """Start meta tag."""
        pass
    
    def pop_meta(self) -> None:
        """End meta tag."""
        pass
    
    def push_bold(self) -> None:
        """Start bold."""
        if self.bbcode_enabled:
            self.text += "[b]"
    
    def pop_bold(self) -> None:
        """End bold."""
        if self.bbcode_enabled:
            self.text += "[/b]"
    
    def push_italic(self) -> None:
        """Start italic."""
        if self.bbcode_enabled:
            self.text += "[i]"
    
    def pop_italic(self) -> None:
        """End italic."""
        if self.bbcode_enabled:
            self.text += "[/i]"
    
    def push_color(self, color: str) -> None:
        """Start color."""
        if self.bbcode_enabled:
            self.text += f"[color={color}]"
    
    def pop_color(self) -> None:
        """End color."""
        if self.bbcode_enabled:
            self.text += "[/color]"
    
    def parse_bbcode(self, bbcode: str) -> str:
        """Parse BBCode to display text."""
        if self.bbcode_enabled:
            self.text = bbcode
        return self.text
    
    def get_content_height(self) -> int:
        """Get content height."""
        return 0
    
    def scroll_to_line(self, line: int) -> None:
        """Scroll to line."""
        pass


__all__ = ["RichTextLabel"]
