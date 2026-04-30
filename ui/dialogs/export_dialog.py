# /**************************************************************************/
# /*  export_dialog.py                                                      */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

from __future__ import annotations

import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, 
    QCheckBox, QDialogButtonBox, QMessageBox, QComboBox
)

from engine.export.build_pipeline import ExportProfile, BuildPipeline

class ExportDialog(QDialog):
    def __init__(self, project_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export Project")
        self.resize(500, 300)
        self.project_name = project_name
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Target Platform
        plat_layout = QHBoxLayout()
        plat_layout.addWidget(QLabel("Target Platform:"))
        self.target_combo = QComboBox()
        self.target_combo.addItems(["windows", "linux", "zip"])
        plat_layout.addWidget(self.target_combo)
        layout.addLayout(plat_layout)

        # Output Name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Output Base Name:"))
        self.name_edit = QLineEdit(self.project_name)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)

        # Output Directory
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("Output Directory:"))
        default_out = os.path.join(os.getcwd(), "dist")
        self.dir_edit = QLineEdit(default_out)
        dir_layout.addWidget(self.dir_edit)
        dir_btn = QPushButton("Browse...")
        dir_btn.clicked.connect(self._browse_dir)
        dir_layout.addWidget(dir_btn)
        layout.addLayout(dir_layout)

        # Options
        self.opt_assets_cb = QCheckBox("Optimize Assets")
        self.opt_assets_cb.setChecked(True)
        layout.addWidget(self.opt_assets_cb)

        self.one_file_cb = QCheckBox("One File Executable")
        self.one_file_cb.setChecked(True)
        layout.addWidget(self.one_file_cb)

        self.windowed_cb = QCheckBox("Windowed (No Console)")
        self.windowed_cb.setChecked(True)
        layout.addWidget(self.windowed_cb)
        
        self.upx_cb = QCheckBox("Compress with UPX (if available)")
        layout.addWidget(self.upx_cb)

        layout.addStretch(1)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._do_export)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _browse_dir(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select Output Directory", self.dir_edit.text())
        if path:
            self.dir_edit.setText(path)

    def _do_export(self) -> None:
        target = self.target_combo.currentText()
        output_name = self.name_edit.text().strip()
        out_dir = self.dir_edit.text().strip()

        if not output_name or not out_dir:
            QMessageBox.warning(self, "Invalid Input", "Please provide name and output directory.")
            return

        profile = ExportProfile(
            target=target,
            output_name=output_name,
            optimize_assets=self.opt_assets_cb.isChecked(),
            one_file=self.one_file_cb.isChecked(),
            windowed=self.windowed_cb.isChecked(),
            upx=self.upx_cb.isChecked()
        )
        pipeline = BuildPipeline()
        try:
            # Assuming project.gep is handled by the caller, here we just do basic call
            # The actual implementation might require project_file and entry_point
            proj_file = os.path.join(os.getcwd(), f"{self.project_name}.gep")
            if not os.path.exists(proj_file):
                proj_file = None
                
            out_path = pipeline.build(
                project_name=self.project_name,
                output_dir=out_dir,
                profile=profile,
                project_file=proj_file
            )
            QMessageBox.information(self, "Export Successful", f"Export completed successfully.\nSaved to: {out_path}")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"An error occurred during export:\n{e}")
