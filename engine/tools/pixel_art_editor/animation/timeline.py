# /**************************************************************************/
# /*  timeline.py                                                           */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Animation timeline widget."""

from typing import List, Optional, Callable
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QSlider, QLabel, QSpinBox
)
from PySide6.QtCore import Qt, Signal, QTimer

import logging


logger = logging.getLogger(__name__)



class Timeline(QWidget):
    """Animation timeline for frame-based animation."""

    frame_changed = Signal(int)
    play_started = Signal()
    play_stopped = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._frames: List[int] = [0]  # Frame indices
        self._current_frame: int = 0
        self._fps: int = 12
        self._is_playing: bool = False
        self._loop: bool = True

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_frame_tick)

        self._build_ui()

    def _build_ui(self) -> None:
        """Build timeline UI."""
        layout = QHBoxLayout(self)
        layout.setSpacing(8)

        # Playback controls
        self._play_btn = QPushButton("Play")
        self._play_btn.clicked.connect(self._toggle_playback)
        layout.addWidget(self._play_btn)

        self._stop_btn = QPushButton("Stop")
        self._stop_btn.clicked.connect(self._stop)
        layout.addWidget(self._stop_btn)

        # Frame display
        self._frame_label = QLabel("Frame: 0")
        layout.addWidget(self._frame_label)

        # Frame slider
        self._frame_slider = QSlider(Qt.Orientation.Horizontal)
        self._frame_slider.setRange(0, len(self._frames) - 1)
        self._frame_slider.valueChanged.connect(self._on_slider_changed)
        layout.addWidget(self._frame_slider, 1)

        # Frame spinbox
        self._frame_spin = QSpinBox()
        self._frame_spin.setRange(0, len(self._frames) - 1)
        self._frame_spin.valueChanged.connect(self._on_spin_changed)
        layout.addWidget(self._frame_spin)

        # FPS control
        layout.addWidget(QLabel("FPS:"))
        self._fps_spin = QSpinBox()
        self._fps_spin.setRange(1, 60)
        self._fps_spin.setValue(self._fps)
        self._fps_spin.valueChanged.connect(self._on_fps_changed)
        layout.addWidget(self._fps_spin)

        # Frame management
        self._add_frame_btn = QPushButton("+F")
        self._add_frame_btn.setToolTip("Add Frame")
        self._add_frame_btn.clicked.connect(self._add_frame)
        layout.addWidget(self._add_frame_btn)

        self._del_frame_btn = QPushButton("-F")
        self._del_frame_btn.setToolTip("Delete Frame")
        self._del_frame_btn.clicked.connect(self._delete_frame)
        layout.addWidget(self._del_frame_btn)

    def _toggle_playback(self) -> None:
        """Toggle play/pause."""
        if self._is_playing:
            self._pause()
        else:
            self._play()

    def _play(self) -> None:
        """Start playback."""
        self._is_playing = True
        self._play_btn.setText("Pause")
        self._timer.start(int(1000 / self._fps))
        self.play_started.emit()

    def _pause(self) -> None:
        """Pause playback."""
        self._is_playing = False
        self._play_btn.setText("Play")
        self._timer.stop()

    def _stop(self) -> None:
        """Stop and reset."""
        self._pause()
        self._current_frame = 0
        self._update_display()
        self.play_stopped.emit()
        self.frame_changed.emit(0)

    def _on_frame_tick(self) -> None:
        """Handle frame tick during playback."""
        self._current_frame += 1

        if self._current_frame >= len(self._frames):
            if self._loop:
                self._current_frame = 0
            else:
                self._stop()
                return

        self._update_display()
        self.frame_changed.emit(self._current_frame)

    def _on_slider_changed(self, value: int) -> None:
        """Handle slider change."""
        self._current_frame = value
        self._update_display()
        self.frame_changed.emit(value)

    def _on_spin_changed(self, value: int) -> None:
        """Handle spinbox change."""
        self._current_frame = value
        self._update_display()
        self.frame_changed.emit(value)

    def _on_fps_changed(self, value: int) -> None:
        """Handle FPS change."""
        self._fps = value
        if self._is_playing:
            self._timer.setInterval(int(1000 / self._fps))

    def _update_display(self) -> None:
        """Update UI display."""
        self._frame_label.setText(f"Frame: {self._current_frame}")
        self._frame_slider.setValue(self._current_frame)
        self._frame_spin.setValue(self._current_frame)

    def _add_frame(self) -> None:
        """Add new frame."""
        self._frames.append(len(self._frames))
        self._frame_slider.setMaximum(len(self._frames) - 1)
        self._frame_spin.setMaximum(len(self._frames) - 1)

    def _delete_frame(self) -> None:
        """Delete current frame."""
        if len(self._frames) > 1:
            self._frames.pop(self._current_frame)
            if self._current_frame >= len(self._frames):
                self._current_frame = len(self._frames) - 1
            self._frame_slider.setMaximum(len(self._frames) - 1)
            self._frame_spin.setMaximum(len(self._frames) - 1)
            self._update_display()

    @property
    def current_frame(self) -> int:
        return self._current_frame

    @property
    def is_playing(self) -> bool:
        return self._is_playing

    def set_frame_count(self, count: int) -> None:
        """Set total frame count."""
        self._frames = list(range(count))
        self._frame_slider.setMaximum(max(0, count - 1))
        self._frame_spin.setMaximum(max(0, count - 1))
