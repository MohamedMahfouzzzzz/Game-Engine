# /**************************************************************************/
# /*  console_panel.py                                                      */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

from __future__ import annotations

from typing import Callable, List

from PySide6.QtCore import Signal, QStringListModel, Qt
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QPlainTextEdit,
    QVBoxLayout, QWidget, QCompleter
)


MAX_CONSOLE_LINES = 10000  # Prevent memory leak from unlimited logging


class ConsolePanel(QWidget):
    command_submitted = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._setup_autocomplete()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Engine Console"))
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output, 1)

        row = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Type command (help, save, add_node, etc.)")
        self.input.returnPressed.connect(self._submit)
        run_btn = QPushButton("Run")
        run_btn.clicked.connect(self._submit)
        row.addWidget(self.input, 1)
        row.addWidget(run_btn)
        layout.addLayout(row)

    def _setup_autocomplete(self) -> None:
        """Setup auto-complete for console commands."""
        commands = [
            # System commands
            "cls", "clear",
            "mkdir", "cd", "ls", "dir", "pwd",
            # Engine commands
            "help", "save", "open",
            "project_info",
            "add_node", "delete", "list_nodes", "select",
            "create_scene", "list_scenes", "switch_scene",
            "fps", "mem", "memory",
        ]

        completer = QCompleter(commands)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.input.setCompleter(completer)

    def log(self, message: str) -> None:
        """Log a message to the console with memory protection."""
        self.output.appendPlainText(message)
        # Prevent memory leak by limiting total lines
        self._enforce_line_limit()

    def _enforce_line_limit(self) -> None:
        """Remove old lines if exceeding max limit to prevent memory leak."""
        doc = self.output.document()
        if doc.lineCount() > MAX_CONSOLE_LINES:
            # Remove oldest 20% of lines when limit exceeded
            lines_to_remove = MAX_CONSOLE_LINES // 5
            cursor = self.output.textCursor()
            cursor.moveToStart()
            cursor.movePosition(cursor.MoveOperation.Down, cursor.MoveMode.KeepAnchor, lines_to_remove)
            cursor.removeSelectedText()
            cursor.deletePreviousChar()  # Remove trailing newline

    def clear(self) -> None:
        """Clear the console output."""
        self.output.clear()

    def _submit(self) -> None:
        cmd = self.input.text().strip()
        if not cmd:
            return
        self.command_submitted.emit(cmd)
        self.input.clear()
