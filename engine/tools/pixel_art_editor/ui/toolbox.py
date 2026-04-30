# /**************************************************************************/
# /*  toolbox.py                                                            */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Toolbox widget for selecting tools."""

from typing import List
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QButtonGroup
from PySide6.QtCore import Signal

from engine.tools.pixel_art_editor.tools.tool_base import ToolBase

class Toolbox(QWidget):
    """Widget for tool selection."""

    tool_selected = Signal(ToolBase)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tools: List[ToolBase] = []
        self._button_group = QButtonGroup(self)
        self._button_group.setExclusive(True)

        self._build_ui()

    def _build_ui(self) -> None:
        """Build the toolbox UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(4, 4, 4, 4)

        self._button_group.idClicked.connect(self._on_button_clicked)

    def add_tool(self, tool: ToolBase) -> None:
        """Add a tool to the toolbox."""
        self._tools.append(tool)

        btn = QPushButton(tool.name)
        btn.setCheckable(True)
        btn.setToolTip(f"{tool.name} Tool")

        index = len(self._tools) - 1
        self._button_group.addButton(btn, index)
        self.layout().addWidget(btn)

    def select_tool(self, index: int) -> None:
        """Select tool by index."""
        if 0 <= index < len(self._tools):
            btn = self._button_group.button(index)
            if btn:
                btn.setChecked(True)
            self._emit_tool_selected(index)

    def _on_button_clicked(self, index: int) -> None:
        """Handle button click."""
        self._emit_tool_selected(index)

    def _emit_tool_selected(self, index: int) -> None:
        """Emit tool selected signal."""
        if 0 <= index < len(self._tools):
            self.tool_selected.emit(self._tools[index])

    def get_current_tool(self) -> ToolBase:
        """Get currently selected tool."""
        index = self._button_group.checkedId()
        if 0 <= index < len(self._tools):
            return self._tools[index]
        return self._tools[0] if self._tools else None
