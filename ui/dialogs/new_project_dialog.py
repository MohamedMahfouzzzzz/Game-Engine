# /**************************************************************************/
# /*  new_project_dialog.py                                                 */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

from __future__ import annotations

import os
from typing import Dict, Any

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, 
    QCheckBox, QDialogButtonBox, QMessageBox, QGroupBox
)


class NewProjectWizardDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Project")
        self.resize(500, 300)
        
        self.project_name = "NewGame"
        self.project_path = os.path.expanduser("~")
        self.features: Dict[str, bool] = {"kanban": False, "dialog": False}
        
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Project Name:"))
        self.name_edit = QLineEdit(self.project_name)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)

        # Path
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Location:"))
        self.path_edit = QLineEdit(self.project_path)
        path_layout.addWidget(self.path_edit)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_path)
        path_layout.addWidget(browse_btn)
        layout.addLayout(path_layout)
        
        # Features Group
        feat_group = QGroupBox("Additional Features")
        feat_layout = QVBoxLayout(feat_group)
        self.kanban_cb = QCheckBox("Add Kanban Board")
        self.dialog_cb = QCheckBox("Add Dialog Manager")
        feat_layout.addWidget(self.kanban_cb)
        feat_layout.addWidget(self.dialog_cb)
        layout.addWidget(feat_group)

        layout.addStretch(1)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _browse_path(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select Project Domain", self.path_edit.text())
        if path:
            self.path_edit.setText(path)

    def _validate_and_accept(self) -> None:
        name = self.name_edit.text().strip()
        path = self.path_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Invalid Name", "Please enter a valid project name.")
            return
        if not os.path.exists(path) or not os.path.isdir(path):
            QMessageBox.warning(self, "Invalid Path", "Please select a valid directory.")
            return
        
        self.project_name = name
        self.project_path = os.path.join(path, name)
        self.features["kanban"] = self.kanban_cb.isChecked()
        self.features["dialog"] = self.dialog_cb.isChecked()
        
        # Verify if directory already exists and is not empty
        if os.path.exists(self.project_path) and os.listdir(self.project_path):
            reply = QMessageBox.question(
                self, "Directory Exists", 
                f"The directory '{self.project_path}' already exists and is not empty.\nAre you sure you want to create the project here?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        self.accept()
