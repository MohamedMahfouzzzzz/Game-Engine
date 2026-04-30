# /**************************************************************************/
# /*  extension_manager_dialog.py                                           */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

from __future__ import annotations

from PySide6.QtWidgets import QFileDialog, QDialog, QDialogButtonBox, QHBoxLayout, QLabel, QListWidget, QPushButton, QVBoxLayout

from engine.extensions.manager_secure import SecureExtensionManager as ExtensionManager


class ExtensionManagerDialog(QDialog):
    def __init__(self, manager: ExtensionManager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.setWindowTitle("Extension Manager")
        self.resize(520, 360)
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Installed Extensions"))
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget, 1)

        row = QHBoxLayout()
        install_zip = QPushButton("Install From Zip")
        install_zip.clicked.connect(self.install_from_zip)
        install_folder = QPushButton("Install From Folder")
        install_folder.clicked.connect(self.install_from_folder)
        row.addWidget(install_zip)
        row.addWidget(install_folder)
        layout.addLayout(row)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)

    def refresh(self) -> None:
        self.list_widget.clear()
        for name in self.manager.list_extensions():
            self.list_widget.addItem(name)

    def install_from_zip(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Install Extension Zip", "", "Zip Files (*.zip)")
        if not path:
            return
        self.manager.install_from_zip(path)
        self.refresh()

    def install_from_folder(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Install Extension Folder")
        if not path:
            return
        self.manager.install_from_folder(path)
        self.refresh()
