# /**************************************************************************/
# /*  layer_panel.py                                                        */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Layer management panel."""

from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QSlider, QCheckBox
)
from PySide6.QtCore import Qt

from engine.tools.pixel_art_editor.canvas import Canvas, Layer


class LayerPanel(QWidget):
    """Panel for managing canvas layers."""

    def __init__(self, canvas: Canvas, parent=None):
        super().__init__(parent)
        self._canvas = canvas
        self._build_ui()
        self._update_list()

    def _build_ui(self) -> None:
        """Build the layer panel UI."""
        layout = QVBoxLayout(self)

        # Header
        layout.addWidget(QLabel("Layers"))

        # Layer list
        self._list = QListWidget()
        self._list.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self._list)

        # Opacity slider
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("Opacity:"))
        self._opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self._opacity_slider.setRange(0, 100)
        self._opacity_slider.setValue(100)
        self._opacity_slider.valueChanged.connect(self._on_opacity_changed)
        opacity_layout.addWidget(self._opacity_slider)
        layout.addLayout(opacity_layout)

        # Buttons
        btn_layout = QHBoxLayout()

        self._add_btn = QPushButton("+")
        self._add_btn.clicked.connect(self._add_layer)
        btn_layout.addWidget(self._add_btn)

        self._del_btn = QPushButton("-")
        self._del_btn.clicked.connect(self._delete_layer)
        btn_layout.addWidget(self._del_btn)

        self._dup_btn = QPushButton("Dup")
        self._dup_btn.clicked.connect(self._duplicate_layer)
        btn_layout.addWidget(self._dup_btn)

        layout.addLayout(btn_layout)

        # Move buttons
        move_layout = QHBoxLayout()
        self._up_btn = QPushButton("Up")
        self._up_btn.clicked.connect(self._move_layer_up)
        move_layout.addWidget(self._up_btn)

        self._down_btn = QPushButton("Down")
        self._down_btn.clicked.connect(self._move_layer_down)
        move_layout.addWidget(self._down_btn)

        layout.addLayout(move_layout)

    def set_canvas(self, canvas: Canvas) -> None:
        """Set the canvas to manage."""
        self._canvas = canvas
        self._update_list()

    def _update_list(self) -> None:
        """Update layer list display."""
        self._list.clear()

        for i, layer in enumerate(self._canvas.layers):
            text = f"{i}: {layer.name}"
            if not layer.visible:
                text += " (hidden)"
            if layer.locked:
                text += " (locked)"

            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, i)
            self._list.addItem(item)

            if i == self._canvas._active_layer_index:
                item.setSelected(True)

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        """Handle layer selection."""
        index = item.data(Qt.ItemDataRole.UserRole)
        self._canvas.set_active_layer(index)
        self._update_opacity_slider()

    def _update_opacity_slider(self) -> None:
        """Update opacity slider for selected layer."""
        layer = self._canvas.get_active_layer()
        if layer:
            self._opacity_slider.setValue(int(layer.opacity * 100))

    def _on_opacity_changed(self, value: int) -> None:
        """Handle opacity change."""
        layer = self._canvas.get_active_layer()
        if layer:
            layer.opacity = value / 100.0

    def _add_layer(self) -> None:
        """Add new layer."""
        layer = self._canvas.add_layer(f"Layer {len(self._canvas.layers)}")
        self._update_list()

    def _delete_layer(self) -> None:
        """Delete selected layer."""
        if len(self._canvas.layers) > 1:
            current = self._list.currentRow()
            self._canvas.remove_layer(current)
            self._update_list()

    def _duplicate_layer(self) -> None:
        """Duplicate selected layer."""
        current = self._list.currentRow()
        self._canvas.duplicate_layer(current)
        self._update_list()

    def _move_layer_up(self) -> None:
        """Move layer up in stack."""
        current = self._list.currentRow()
        if current > 0:
            self._canvas.move_layer(current, current - 1)
            self._update_list()
            self._list.setCurrentRow(current - 1)

    def _move_layer_down(self) -> None:
        """Move layer down in stack."""
        current = self._list.currentRow()
        if current < len(self._canvas.layers) - 1:
            self._canvas.move_layer(current, current + 1)
            self._update_list()
            self._list.setCurrentRow(current + 1)
