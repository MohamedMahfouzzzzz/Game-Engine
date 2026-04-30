# /**************************************************************************/
# /*  kanban_board.py                                                       */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

from __future__ import annotations

import json
import os
from typing import Dict, List

from PySide6.QtCore import Qt, Signal, QMimeData
from PySide6.QtGui import QDrag
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
    QScrollArea, QFrame, QInputDialog, QMessageBox, QMenu
)


class KanbanCard(QFrame):
    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.text = text
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setStyleSheet("background-color: #3b3b4f; border-radius: 4px; padding: 5px;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setStyleSheet("color: white;")
        layout.addWidget(self.label)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(self.text)
            drag.setMimeData(mime)
            drag.exec(Qt.DropAction.MoveAction)


class KanbanColumn(QWidget):
    card_moved = Signal()
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.setAcceptDrops(True)
        self.cards: List[str] = []
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Header
        header = QLabel(title)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("font-weight: bold; font-size: 14px; background-color: #2b2b36; color: white; padding: 5px;")
        layout.addWidget(header)
        
        # Cards Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background-color: #1e1e24; border: none;")
        
        self.cards_widget = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_widget)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.cards_widget)
        layout.addWidget(self.scroll)
        
        # Add Card Btn
        self.add_btn = QPushButton("+ Add Card")
        self.add_btn.setStyleSheet("background-color: #4a4a5e; color: white;")
        self.add_btn.clicked.connect(self._add_new_card)
        layout.addWidget(self.add_btn)

    def _add_new_card(self):
        text, ok = QInputDialog.getText(self, "New Card", "Enter task description:")
        if ok and text.strip():
            self.add_card(text.strip())
            self.card_moved.emit()

    def add_card(self, text: str):
        self.cards.append(text)
        self._render_cards()

    def remove_card(self, text: str):
        if text in self.cards:
            self.cards.remove(text)
            self._render_cards()

    def _render_cards(self):
        # Clear layout
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
                
        # Rebuild
        for c in self.cards:
            card_widget = KanbanCard(c)
            self.cards_layout.addWidget(card_widget)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        text = event.mimeData().text()
        # Emit a signal and let the board handle the move between columns
        source_widget = event.source()
        if source_widget and isinstance(source_widget, KanbanCard):
            # Tell parent board to process the move
            self.parentWidget().process_card_move(text, source_widget.parentWidget().parentWidget().parentWidget(), self)
            event.acceptProposedAction()


class KanbanBoardWidget(QWidget):
    def __init__(self, project_path: str, parent=None):
        super().__init__(parent)
        self.project_path = project_path
        self.data_file = os.path.join(self.project_path, "kanban.json") if project_path else None
        
        self.columns: List[KanbanColumn] = []
        self._build_ui()
        self.load_board()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar = QHBoxLayout()
        title = QLabel("Project Kanban Board")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        toolbar.addWidget(title)
        
        toolbar.addStretch()
        
        save_btn = QPushButton("Save Board")
        save_btn.clicked.connect(self.save_board)
        toolbar.addWidget(save_btn)
        layout.addLayout(toolbar)
        
        # Board
        self.board_layout = QHBoxLayout()
        layout.addLayout(self.board_layout)
        
        # Init base columns
        for col in ["To Do", "In Progress", "Done"]:
            c = KanbanColumn(col, self)
            c.card_moved.connect(self._auto_save)
            self.columns.append(c)
            self.board_layout.addWidget(c)

    def process_card_move(self, text: str, source_col: KanbanColumn, target_col: KanbanColumn):
        if source_col != target_col:
            source_col.remove_card(text)
            target_col.add_card(text)
            self._auto_save()

    def _auto_save(self):
        self.save_board()

    def save_board(self):
        if not self.data_file: return
        data = {}
        for col in self.columns:
            data[col.title] = col.cards
        
        try:
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Failed to save Kanban: {e}")

    def load_board(self):
        if not self.data_file or not os.path.exists(self.data_file):
            return
            
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            
            for col in self.columns:
                if col.title in data:
                    col.cards = data[col.title]
                    col._render_cards()
        except Exception as e:
            print(f"Failed to load Kanban: {e}")
