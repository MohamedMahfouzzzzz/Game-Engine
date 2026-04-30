# /**************************************************************************/
# /*  script_runner_dialog.py                                               */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

from __future__ import annotations

from typing import Optional
import json

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from engine.core.node import Node
from engine.scripting.abi import ScriptContext
from engine.scripting.host import ScriptHost


class ScriptRunnerDialog(QDialog):
    def __init__(self, node: Optional[Node], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Run Script")
        self.resize(720, 480)
        self.node = node
        self.host = ScriptHost()
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        top = QHBoxLayout()
        top.addWidget(QLabel("Language:"))
        self.lang_combo = QComboBox()
        for language in self.host.available_languages().keys():
            self.lang_combo.addItem(language)
        top.addWidget(self.lang_combo)
        run_btn = QPushButton("Run")
        run_btn.clicked.connect(self._run_script)
        top.addWidget(run_btn)
        layout.addLayout(top)

        self.source = QTextEdit()
        self.source.setPlaceholderText("Write script here...")
        layout.addWidget(self.source, 3)

        layout.addWidget(QLabel("Output"))
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output, 2)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)

    def _run_script(self) -> None:
        if not self.node:
            QMessageBox.warning(self, "No Node", "Select a node first.")
            return
        language = self.lang_combo.currentText()
        source = self.source.toPlainText()
        ctx = ScriptContext(
            node_id=self.node.uid,
            scene_id=self.node.get_property("scene_id", "unknown"),
            properties=self.node.properties,
        )
        try:
            result = self.host.execute(language, source, ctx)
            self.output.setPlainText(json.dumps(result, indent=2, ensure_ascii=False) if isinstance(result, (dict, list)) else str(result))
        except Exception as exc:
            self.output.setPlainText(f"ERROR: {exc}")
