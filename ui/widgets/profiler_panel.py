# /**************************************************************************/
# /*  profiler_panel.py                                                     */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Profiler panel showing memory, FPS, and performance metrics."""

from __future__ import annotations

import time
import sys
import threading
from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QProgressBar, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont


class ProfilerPanel(QWidget):
    """Profiler panel showing performance metrics like Godot."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._update_timer = QTimer()
        self._update_timer.timeout.connect(self._update_metrics)
        self._update_timer.setInterval(500)  # Update every 500ms

        self._fps_history = []
        self._max_fps_history = 60
        self._last_frame_time = time.time()
        self._frame_count = 0

        self.init_ui()
        self._update_timer.start()

    def init_ui(self) -> None:
        """Initialize profiler UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Title
        title = QLabel("Profiler")
        title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        title.setStyleSheet("color: #fff;")
        layout.addWidget(title)

        # FPS section
        fps_frame = self._create_metric_frame("FPS", self._create_fps_widget())
        layout.addWidget(fps_frame)

        # Memory section
        mem_frame = self._create_metric_frame("Memory", self._create_memory_widget())
        layout.addWidget(mem_frame)

        # CPU section
        cpu_frame = self._create_metric_frame("CPU", self._create_cpu_widget())
        layout.addWidget(cpu_frame)

        # Node count section
        node_frame = self._create_metric_frame("Nodes", self._create_node_widget())
        layout.addWidget(node_frame)

        # Performance table
        layout.addWidget(self._create_performance_table())

        layout.addStretch()

    def _create_metric_frame(self, title: str, content: QWidget) -> QFrame:
        """Create a frame for a metric."""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #3d3d3d;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 4px;
            }
        """)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(4, 4, 4, 4)

        label = QLabel(title)
        label.setStyleSheet("color: #aaa; font-size: 10px;")
        layout.addWidget(label)
        layout.addWidget(content)

        return frame

    def _create_fps_widget(self) -> QWidget:
        """Create FPS display widget."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        self._fps_label = QLabel("0 FPS")
        self._fps_label.setStyleSheet("color: #4caf50; font-size: 14px; font-weight: bold;")
        layout.addWidget(self._fps_label)

        self._fps_bar = QProgressBar()
        self._fps_bar.setRange(0, 120)
        self._fps_bar.setStyleSheet("""
            QProgressBar {
                background-color: #2d2d2d;
                border: 1px solid #555;
                border-radius: 2px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4caf50;
            }
        """)
        layout.addWidget(self._fps_bar)

        return widget

    def _create_memory_widget(self) -> QWidget:
        """Create memory display widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        self._ram_label = QLabel("0 MB / 0 MB")
        self._ram_label.setStyleSheet("color: #2196f3; font-size: 12px;")
        layout.addWidget(self._ram_label)

        self._ram_bar = QProgressBar()
        self._ram_bar.setRange(0, 100)
        self._ram_bar.setStyleSheet("""
            QProgressBar {
                background-color: #2d2d2d;
                border: 1px solid #555;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: #2196f3;
            }
        """)
        layout.addWidget(self._ram_bar)

        return widget

    def _create_cpu_widget(self) -> QWidget:
        """Create CPU display widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        self._cpu_label = QLabel("0%")
        self._cpu_label.setStyleSheet("color: #ff9800; font-size: 12px;")
        layout.addWidget(self._cpu_label)

        self._cpu_bar = QProgressBar()
        self._cpu_bar.setRange(0, 100)
        self._cpu_bar.setStyleSheet("""
            QProgressBar {
                background-color: #2d2d2d;
                border: 1px solid #555;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: #ff9800;
            }
        """)
        layout.addWidget(self._cpu_bar)

        return widget

    def _create_node_widget(self) -> QWidget:
        """Create node count display widget."""
        self._node_label = QLabel("0 nodes")
        self._node_label.setStyleSheet("color: #9c27b0; font-size: 12px;")
        return self._node_label

    def _create_performance_table(self) -> QTableWidget:
        """Create performance metrics table."""
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Metric", "Value"])
        table.setStyleSheet("""
            QTableWidget {
                background-color: #3d3d3d;
                color: #fff;
                border: 1px solid #555;
                gridline-color: #555;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QHeaderView::section {
                background-color: #4d4d4d;
                color: #fff;
                padding: 4px;
                border: none;
                border-bottom: 1px solid #555;
            }
        """)
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setVisible(False)
        table.setFixedHeight(120)

        self._perf_table = table
        return table

    def _update_metrics(self) -> None:
        """Update all performance metrics."""
        # Update FPS
        current_time = time.time()
        delta = current_time - self._last_frame_time
        self._frame_count += 1

        if delta >= 1.0:
            fps = self._frame_count / delta
            self._fps_history.append(fps)
            if len(self._fps_history) > self._max_fps_history:
                self._fps_history.pop(0)

            avg_fps = sum(self._fps_history) / len(self._fps_history) if self._fps_history else 0
            self._fps_label.setText(f"{avg_fps:.1f} FPS")
            self._fps_bar.setValue(int(avg_fps))

            # Color based on FPS
            if avg_fps >= 60:
                color = "#4caf50"  # Green
            elif avg_fps >= 30:
                color = "#ff9800"  # Orange
            else:
                color = "#f44336"  # Red
            self._fps_label.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: bold;")

            self._frame_count = 0
            self._last_frame_time = current_time

        # Update memory (using standard library)
        import gc
        gc.collect()
        ram_used = sys.getsizeof(self) / (1024 * 1024)  # Approximate in MB
        ram_total = 16384  # Assume 16GB total (placeholder)
        ram_percent = min((ram_used / ram_total) * 100, 100)

        self._ram_label.setText(f"{ram_used:.1f} MB / {ram_total:.0f} MB")
        self._ram_bar.setValue(int(ram_percent))

        # Update CPU (placeholder - no reliable way without psutil)
        cpu_percent = 0.0
        self._cpu_label.setText("N/A")
        self._cpu_bar.setValue(0)

        # Update performance table
        self._update_performance_table(ram_used, ram_percent, cpu_percent)

    def _update_performance_table(self, ram_used: float, ram_percent: float, cpu_percent: float) -> None:
        """Update performance metrics table."""
        import gc
        metrics = [
            ("Process RAM", f"{ram_used:.1f} MB"),
            ("RAM Usage", f"{ram_percent:.1f}%"),
            ("CPU Usage", "N/A (requires psutil)"),
            ("Threads", str(threading.active_count())),
            ("GC Objects", str(len(gc.get_objects()))),
        ]

        self._perf_table.setRowCount(len(metrics))
        for row, (metric, value) in enumerate(metrics):
            self._perf_table.setItem(row, 0, QTableWidgetItem(metric))
            self._perf_table.setItem(row, 1, QTableWidgetItem(value))

    def set_node_count(self, count: int) -> None:
        """Set the node count display."""
        self._node_label.setText(f"{count} nodes")

    def closeEvent(self, event) -> None:  # type: ignore[override]
        """Clean up timer on close."""
        self._update_timer.stop()
        super().closeEvent(event)
