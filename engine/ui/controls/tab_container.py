# /**************************************************************************/
# /*  tab_container.py                                                      */
# /**************************************************************************/

"""TabContainer - Tabbed interface container."""

from __future__ import annotations
from enum import IntEnum
from typing import List
from .container import Container

import logging


logger = logging.getLogger(__name__)



class TabContainer(Container):
    """Tabbed interface with multiple pages.
    
    Properties:
        tab_alignment: int - 0=LEFT, 1=CENTER, 2=RIGHT
        current_tab: int - Active tab index
        clip_tabs: bool - Clip tab text
        tabs_visible: bool - Show tab bar
        all_tabs_in_front: bool - Tabs always on top
    
    Signals:
        tab_selected(tab: int)
        tab_clicked(tab: int)
        tab_hovered(tab: int)
        tab_changed(tab: int)
    """
    
    class TabAlignment(IntEnum):
        LEFT = 0
        CENTER = 1
        RIGHT = 2
    
    __slots__ = [
        "tab_alignment",
        "current_tab",
        "clip_tabs",
        "tabs_visible",
        "all_tabs_in_front",
        "_tab_titles"
    ]
    
    _SIGNALS = ["tab_selected", "tab_clicked", "tab_hovered", "tab_changed"]
    
    def __init__(self, name: str = "TabContainer"):
        super().__init__(name)
        
        self.tab_alignment: int = self.TabAlignment.LEFT
        self.current_tab: int = 0
        self.clip_tabs: bool = True
        self.tabs_visible: bool = True
        self.all_tabs_in_front: bool = False
        
        self._tab_titles: List[str] = []
    
    def get_tab_count(self) -> int:
        """Get number of tabs."""
        return len([c for c in self.children if hasattr(c, 'visible')])
    
    def set_current_tab(self, tab_idx: int) -> None:
        """Switch to tab."""
        if tab_idx != self.current_tab:
            old_tab = self.current_tab
            self.current_tab = tab_idx
            self.signals.emit("tab_changed", tab_idx)
            self.signals.emit("tab_selected", tab_idx)
    
    def select_next_available(self) -> None:
        """Select next available tab."""
        count = self.get_tab_count()
        if count > 0 and self.current_tab < count - 1:
            self.set_current_tab(self.current_tab + 1)
    
    def select_previous_available(self) -> None:
        """Select previous available tab."""
        if self.current_tab > 0:
            self.set_current_tab(self.current_tab - 1)
    
    def set_tab_title(self, tab_idx: int, title: str) -> None:
        """Set tab title."""
        while len(self._tab_titles) <= tab_idx:
            self._tab_titles.append("")
        self._tab_titles[tab_idx] = title
    
    def get_tab_title(self, tab_idx: int) -> str:
        """Get tab title."""
        if tab_idx < len(self._tab_titles):
            return self._tab_titles[tab_idx]
        return f"Tab {tab_idx}"


__all__ = ["TabContainer"]
