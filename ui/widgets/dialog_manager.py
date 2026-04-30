# /**************************************************************************/
# /*  dialog_manager.py                                                     */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

from __future__ import annotations

import json
import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
    QListWidget, QTextEdit, QSplitter, QMessageBox
)

class DialogManagerWidget(QWidget):
    def __init__(self, project_path: str, parent=None):
        super().__init__(parent)
        self.project_path = project_path
        self.data_file = os.path.join(self.project_path, "dialogs.json") if project_path else None
        
        # Format: { "dialog_id": [ {"character": "...", "text": "...", "next": "id"} ] }
        self.dialogs = {}
        
        self._build_ui()
        self.load_dialogs()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel("Dialog Manager")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left Panel (List of dialog IDs)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0,0,0,0)
        
        self.id_list = QListWidget()
        self.id_list.currentItemChanged.connect(self._on_id_selected)
        left_layout.addWidget(self.id_list)
        
        btn_layout = QHBoxLayout()
        add_id_btn = QPushButton("Add Dialog ID")
        add_id_btn.clicked.connect(self._add_dialog_id)
        remove_id_btn = QPushButton("Remove")
        remove_id_btn.clicked.connect(self._remove_dialog_id)
        btn_layout.addWidget(add_id_btn)
        btn_layout.addWidget(remove_id_btn)
        left_layout.addLayout(btn_layout)
        
        # Right Panel (Lines)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0,0,0,0)
        
        self.lines_list = QListWidget()
        self.lines_list.currentItemChanged.connect(self._on_line_selected)
        right_layout.addWidget(QLabel("Lines within selected Dialog:"))
        right_layout.addWidget(self.lines_list)
        
        # Editor form
        form_layout = QVBoxLayout()
        
        char_layout = QHBoxLayout()
        char_layout.addWidget(QLabel("Character:"))
        self.char_edit = QLineEdit()
        self.char_edit.textChanged.connect(self._update_current_line)
        char_layout.addWidget(self.char_edit)
        form_layout.addLayout(char_layout)
        
        form_layout.addWidget(QLabel("Line Text:"))
        self.text_edit = QTextEdit()
        self.text_edit.textChanged.connect(self._update_current_line_text)
        form_layout.addWidget(self.text_edit)
        
        lines_btn_layout = QHBoxLayout()
        add_line_btn = QPushButton("Add Line")
        add_line_btn.clicked.connect(self._add_line)
        remove_line_btn = QPushButton("Remove Line")
        remove_line_btn.clicked.connect(self._remove_line)
        lines_btn_layout.addWidget(add_line_btn)
        lines_btn_layout.addWidget(remove_line_btn)
        form_layout.addLayout(lines_btn_layout)
        
        right_layout.addLayout(form_layout)
        
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        layout.addWidget(splitter)
        
        save_btn = QPushButton("Save Dialogs")
        save_btn.clicked.connect(self.save_dialogs)
        layout.addWidget(save_btn)

    def _add_dialog_id(self):
        new_id = f"dialog_{self.id_list.count() + 1}"
        self.dialogs[new_id] = []
        self.id_list.addItem(new_id)
        
    def _remove_dialog_id(self):
        item = self.id_list.currentItem()
        if item:
            del self.dialogs[item.text()]
            self.id_list.takeItem(self.id_list.row(item))

    def _on_id_selected(self, current, previous):
        self.lines_list.clear()
        if not current:
            return
            
        lines = self.dialogs.get(current.text(), [])
        for i, line in enumerate(lines):
            self.lines_list.addItem(f"{i}: {line.get('character', '???')} - {line.get('text', '')}")

    def _add_line(self):
        item = self.id_list.currentItem()
        if not item: return
        dialog_id = item.text()
        new_line = {"character": "Player", "text": "New line"}
        self.dialogs[dialog_id].append(new_line)
        self.lines_list.addItem(f"{len(self.dialogs[dialog_id])-1}: Player - New line")

    def _remove_line(self):
        id_item = self.id_list.currentItem()
        line_item = self.lines_list.currentItem()
        if not id_item or not line_item: return
        
        dialog_id = id_item.text()
        idx = self.lines_list.row(line_item)
        
        del self.dialogs[dialog_id][idx]
        self._on_id_selected(id_item, None)

    def _on_line_selected(self, current, previous):
        if not current:
             self.char_edit.clear()
             self.text_edit.clear()
             return
             
        id_item = self.id_list.currentItem()
        if not id_item: return
        
        idx = self.lines_list.row(current)
        line = self.dialogs[id_item.text()][idx]
        
        # Block signals to prevent overwrite loop
        self.char_edit.blockSignals(True)
        self.text_edit.blockSignals(True)
        self.char_edit.setText(line.get("character", ""))
        self.text_edit.setText(line.get("text", ""))
        self.char_edit.blockSignals(False)
        self.text_edit.blockSignals(False)

    def _update_current_line(self, text):
        self._modify_line("character", text)

    def _update_current_line_text(self):
        self._modify_line("text", self.text_edit.toPlainText())

    def _modify_line(self, key, value):
        id_item = self.id_list.currentItem()
        line_item = self.lines_list.currentItem()
        if not id_item or not line_item: return
        
        idx = self.lines_list.row(line_item)
        self.dialogs[id_item.text()][idx][key] = value
        
        # Update list display
        line = self.dialogs[id_item.text()][idx]
        line_item.setText(f"{idx}: {line.get('character', '???')} - {line.get('text', '')}")

    def save_dialogs(self):
        if not self.data_file: return
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.dialogs, f, indent=4)
            QMessageBox.information(self, "Saved", "Dialogs saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save dialogs: {e}")

    def load_dialogs(self):
        if not self.data_file or not os.path.exists(self.data_file):
            return
        try:
            with open(self.data_file, 'r') as f:
                 self.dialogs = json.load(f)
                 
            self.id_list.clear()
            for k in self.dialogs.keys():
                self.id_list.addItem(k)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load dialogs: {e}")
