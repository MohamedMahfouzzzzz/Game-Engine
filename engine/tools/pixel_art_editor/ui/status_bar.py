# /**************************************************************************/
# /*  status_bar.py                                                         */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Status bar for editor."""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel


class StatusBar(QWidget):
    """Status bar showing editor info."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        """Build status bar UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        self._message_label = QLabel("Ready")
        layout.addWidget(self._message_label)

        layout.addStretch()

        self._coords_label = QLabel("0, 0")
        layout.addWidget(self._coords_label)

        layout.addSpacing(16)

        self._zoom_label = QLabel("800%")
        layout.addWidget(self._zoom_label)

    def set_message(self, message: str) -> None:
        """Set status message."""
        self._message_label.setText(message)

    def set_coordinates(self, x: int, y: int) -> None:
        """Set cursor coordinates."""
        self._coords_label.setText(f"{x}, {y}")

    def set_zoom(self, zoom: float) -> None:
        """Set zoom percentage."""
        self._zoom_label.setText(f"{int(zoom * 100)}%")
