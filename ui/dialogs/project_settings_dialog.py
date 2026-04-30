# /**************************************************************************/
# /*  project_settings_dialog.py                                            */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

from __future__ import annotations

from PySide6.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QVBoxLayout

from engine.core.project_secure import SecureProject as Project


class ProjectSettingsDialog(QDialog):
    def __init__(self, project: Project, parent=None):
        super().__init__(parent)
        self.project = project
        self.setWindowTitle("Project Settings")
        self.resize(420, 180)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.name_input = QLineEdit(self.project.name)
        self.active_scene_combo = QComboBox()
        scene_items = [(s.name, sid) for sid, s in self.project.scenes.items()]
        for scene_name, scene_id in scene_items:
            self.active_scene_combo.addItem(scene_name, scene_id)
        if self.project.active_scene:
            idx = self.active_scene_combo.findData(self.project.active_scene.id)
            if idx >= 0:
                self.active_scene_combo.setCurrentIndex(idx)
        form.addRow("Project Name", self.name_input)
        form.addRow("Active Scene", self.active_scene_combo)
        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def apply_changes(self) -> None:
        self.project.name = self.name_input.text().strip() or self.project.name
        sid = self.active_scene_combo.currentData()
        if sid:
            self.project.set_active_scene(sid)
