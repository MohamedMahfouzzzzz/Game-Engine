# /**************************************************************************/
# /*  color_palette.py                                                      */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Color palette widget."""

from typing import Tuple, List, Callable, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QColorDialog, QLabel
)
from PySide6.QtCore import Signal
from PySide6.QtGui import QColor


class ColorSwatch(QPushButton):
    """Single color swatch button."""

    def __init__(self, color: Tuple[int, int, int, int], parent=None):
        super().__init__(parent)
        self._color = color
        self._update_style()
        self.setFixedSize(24, 24)

    def _update_style(self) -> None:
        """Update button style with current color."""
        r, g, b, a = self._color
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba({r}, {g}, {b}, {a});
                border: 2px solid #888;
                border-radius: 2px;
            }}
            QPushButton:hover {{
                border: 2px solid #fff;
            }}
        """)

    @property
    def color(self) -> Tuple[int, int, int, int]:
        return self._color

    @color.setter
    def color(self, value: Tuple[int, int, int, int]) -> None:
        self._color = value
        self._update_style()


class ColorPalette(QWidget):
    """Color palette for selecting colors."""

    color_selected = Signal(tuple)  # RGBA tuple

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_color: Tuple[int, int, int, int] = (0, 0, 0, 255)
        self._secondary_color: Tuple[int, int, int, int] = (255, 255, 255, 255)
        self._color_history: List[Tuple[int, int, int, int]] = []

        self._build_ui()
        self._setup_default_palette()

    def _build_ui(self) -> None:
        """Build the palette UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(4)

        # Current colors display
        colors_layout = QHBoxLayout()

        self._primary_btn = ColorSwatch(self._current_color)
        self._primary_btn.setToolTip("Primary color (Left Click)")
        self._primary_btn.clicked.connect(self._pick_primary_color)
        colors_layout.addWidget(self._primary_btn)

        self._secondary_btn = ColorSwatch(self._secondary_color)
        self._secondary_btn.setToolTip("Secondary color (Right Click)")
        self._secondary_btn.clicked.connect(self._pick_secondary_color)
        colors_layout.addWidget(self._secondary_btn)

        layout.addLayout(colors_layout)

        # Preset palette grid
        layout.addWidget(QLabel("Presets:"))
        self._preset_grid = QGridLayout()
        self._preset_grid.setSpacing(2)
        layout.addLayout(self._preset_grid)

        # History
        layout.addWidget(QLabel("History:"))
        self._history_layout = QHBoxLayout()
        self._history_layout.setSpacing(2)
        layout.addLayout(self._history_layout)

        layout.addStretch()

    def _setup_default_palette(self) -> None:
        """Setup default color palette."""
        # Standard 16-color palette
        default_colors = [
            (0, 0, 0, 255),       # Black
            (255, 255, 255, 255), # White
            (255, 0, 0, 255),     # Red
            (0, 255, 0, 255),     # Green
            (0, 0, 255, 255),     # Blue
            (255, 255, 0, 255),   # Yellow
            (255, 0, 255, 255),   # Magenta
            (0, 255, 255, 255),   # Cyan
            (128, 128, 128, 255), # Gray
            (255, 128, 0, 255),   # Orange
            (128, 0, 255, 255),   # Purple
            (255, 192, 203, 255), # Pink
            (139, 69, 19, 255),   # Brown
            (0, 128, 0, 255),     # Dark Green
            (0, 0, 128, 255),     # Dark Blue
            (128, 0, 0, 255),     # Dark Red
        ]

        for i, color in enumerate(default_colors):
            btn = ColorSwatch(color)
            btn.clicked.connect(lambda checked, c=color: self._select_color(c))
            self._preset_grid.addWidget(btn, i // 4, i % 4)

    def _select_color(self, color: Tuple[int, int, int, int]) -> None:
        """Select a color."""
        self._add_to_history(self._current_color)
        self._current_color = color
        self._primary_btn.color = color
        self.color_selected.emit(color)

    def _pick_primary_color(self) -> None:
        """Open color picker for primary."""
        color = QColorDialog.getColor(
            QColor(*self._current_color),
            self,
            "Select Primary Color"
        )
        if color.isValid():
            self._select_color((color.red(), color.green(), color.blue(), 255))

    def _pick_secondary_color(self) -> None:
        """Open color picker for secondary."""
        color = QColorDialog.getColor(
            QColor(*self._secondary_color),
            self,
            "Select Secondary Color"
        )
        if color.isValid():
            self._secondary_color = (color.red(), color.green(), color.blue(), 255)
            self._secondary_btn.color = self._secondary_color

    def _add_to_history(self, color: Tuple[int, int, int, int]) -> None:
        """Add color to history."""
        if color not in self._color_history:
            self._color_history.insert(0, color)
            self._color_history = self._color_history[:8]  # Keep last 8
            self._update_history_display()

    def _update_history_display(self) -> None:
        """Update history buttons."""
        # Clear existing
        while self._history_layout.count():
            item = self._history_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add history buttons
        for color in self._color_history:
            btn = ColorSwatch(color)
            btn.setFixedSize(20, 20)
            btn.clicked.connect(lambda checked, c=color: self._select_color(c))
            self._history_layout.addWidget(btn)

    def get_primary_color(self) -> Tuple[int, int, int, int]:
        """Get current primary color."""
        return self._current_color

    def get_secondary_color(self) -> Tuple[int, int, int, int]:
        """Get secondary color."""
        return self._secondary_color

    def set_primary_color(self, color: Tuple[int, int, int, int]) -> None:
        """Set primary color."""
        self._current_color = color
        self._primary_btn.color = color
        self.color_selected.emit(color)
