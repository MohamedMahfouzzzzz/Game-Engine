# /**************************************************************************/
# /*  canvas_view.py                                                        */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Canvas view widget with rendering and interaction."""

from typing import Optional
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRect, Signal
from PySide6.QtGui import QPainter, QPen, QColor, QBrush, QImage

from engine.tools.pixel_art_editor.canvas import Canvas
from engine.tools.pixel_art_editor.tools.tool_base import ToolBase

import logging


logger = logging.getLogger(__name__)



class CanvasView(QWidget):
    """Widget for displaying and interacting with canvas."""

    mouse_pressed = Signal(int, int)
    mouse_moved = Signal(int, int)
    mouse_released = Signal(int, int)

    def __init__(self, canvas: Canvas, parent=None):
        super().__init__(parent)
        self._canvas = canvas
        self._tool: Optional[ToolBase] = None
        self._zoom: float = 8.0
        self._show_grid: bool = True
        self._show_preview: bool = False

        self.setFixedSize(
            int(canvas.width * self._zoom),
            int(canvas.height * self._zoom)
        )
        self.setMouseTracking(True)

    def set_canvas(self, canvas: Canvas) -> None:
        """Set canvas to display."""
        self._canvas = canvas
        self._update_size()
        self.update()

    def set_zoom(self, zoom: float) -> None:
        """Set zoom level."""
        self._zoom = zoom
        self._update_size()
        self.update()

    def set_tool(self, tool: ToolBase) -> None:
        """Set active tool."""
        self._tool = tool
        if tool:
            tool.set_canvas(self._canvas)

    def set_current_color(self, color: tuple) -> None:
        """Set current drawing color."""
        self._current_color = color
        if self._tool:
            self._tool.set_color(color)

    def toggle_grid(self) -> None:
        """Toggle grid visibility."""
        self._show_grid = not self._show_grid
        self.update()

    def toggle_preview(self) -> None:
        """Toggle preview mode."""
        self._show_preview = not self._show_preview
        self.update()

    def update_dirty_rect(self) -> None:
        """Update only the canvas region that changed, when known."""
        rect = self._canvas.dirty_rect
        if rect is None:
            for layer in self._canvas.layers:
                if layer.dirty_rect is not None:
                    lx, ly, lw, lh = layer.dirty_rect
                    if rect is None:
                        rect = layer.dirty_rect
                    else:
                        rx, ry, rw, rh = rect
                        x1 = min(rx, lx)
                        y1 = min(ry, ly)
                        x2 = max(rx + rw, lx + lw)
                        y2 = max(ry + rh, ly + lh)
                        rect = (x1, y1, x2 - x1, y2 - y1)
                    layer.dirty_rect = None
        if rect is None:
            self.update()
            return
        x, y, w, h = rect
        pad = max(2, int(self._zoom))
        offset_x = (self.width() - int(self._canvas.width * self._zoom)) // 2
        offset_y = (self.height() - int(self._canvas.height * self._zoom)) // 2
        self.update(QRect(
            offset_x + int(x * self._zoom) - pad,
            offset_y + int(y * self._zoom) - pad,
            int(w * self._zoom) + pad * 2,
            int(h * self._zoom) + pad * 2,
        ))
        self._canvas.dirty_rect = None

    def _update_size(self) -> None:
        """Update widget size based on canvas and zoom."""
        self.setFixedSize(
            int(self._canvas.width * self._zoom),
            int(self._canvas.height * self._zoom)
        )

    def paintEvent(self, event) -> None:
        """Render canvas."""
        painter = QPainter(self)

        # Draw background
        painter.fillRect(self.rect(), QColor(32, 32, 32))

        # Get merged image
        image = self._canvas.get_merged_image()
        qimage = QImage(
            image.tobytes("raw", "RGBA"),
            image.width,
            image.height,
            QImage.Format.Format_RGBA8888
        )

        # Scale image
        scaled = qimage.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation
        )

        # Draw image centered
        x = (self.width() - scaled.width()) // 2
        y = (self.height() - scaled.height()) // 2
        painter.drawImage(x, y, scaled)

        # Draw grid
        if self._show_grid and self._zoom > 4:
            self._draw_grid(painter)

        # Draw selection
        if self._canvas.selection:
            self._draw_selection(painter)

    def _draw_grid(self, painter: QPainter) -> None:
        """Draw pixel grid."""
        pen = QPen(QColor(128, 128, 128, 64))
        pen.setWidthF(0.5)
        painter.setPen(pen)

        offset_x = (self.width() - int(self._canvas.width * self._zoom)) // 2
        offset_y = (self.height() - int(self._canvas.height * self._zoom)) // 2

        for x in range(self._canvas.width + 1):
            screen_x = offset_x + int(x * self._zoom)
            painter.drawLine(
                screen_x, offset_y,
                screen_x, offset_y + int(self._canvas.height * self._zoom)
            )

        for y in range(self._canvas.height + 1):
            screen_y = offset_y + int(y * self._zoom)
            painter.drawLine(
                offset_x, screen_y,
                offset_x + int(self._canvas.width * self._zoom), screen_y
            )

    def _draw_selection(self, painter: QPainter) -> None:
        """Draw selection outline."""
        if not self._canvas.selection:
            return

        x, y, w, h = self._canvas.selection
        offset_x = (self.width() - int(self._canvas.width * self._zoom)) // 2
        offset_y = (self.height() - int(self._canvas.height * self._zoom)) // 2

        screen_x = offset_x + int(x * self._zoom)
        screen_y = offset_y + int(y * self._zoom)
        screen_w = int(w * self._zoom)
        screen_h = int(h * self._zoom)

        pen = QPen(QColor(0, 255, 255))
        pen.setWidth(2)
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.drawRect(QRect(screen_x, screen_y, screen_w, screen_h))

    def mousePressEvent(self, event) -> None:
        """Handle mouse press."""
        x, y = self._screen_to_canvas(event.pos().x(), event.pos().y())
        button = 1 if event.button() == Qt.MouseButton.LeftButton else 2

        if self._tool:
            self._tool.on_mouse_press(x, y, button)

        self.mouse_pressed.emit(x, y)
        self.update_dirty_rect()

    def mouseMoveEvent(self, event) -> None:
        """Handle mouse move."""
        x, y = self._screen_to_canvas(event.pos().x(), event.pos().y())

        if self._tool and self._tool._is_drawing:
            self._tool.on_mouse_move(x, y)

        self.mouse_moved.emit(x, y)
        self.update_dirty_rect()

    def mouseReleaseEvent(self, event) -> None:
        """Handle mouse release."""
        x, y = self._screen_to_canvas(event.pos().x(), event.pos().y())
        button = 1 if event.button() == Qt.MouseButton.LeftButton else 2

        if self._tool:
            self._tool.on_mouse_release(x, y, button)

        self.mouse_released.emit(x, y)
        self.update_dirty_rect()

    def _screen_to_canvas(self, screen_x: int, screen_y: int) -> tuple:
        """Convert screen coordinates to canvas coordinates."""
        offset_x = (self.width() - int(self._canvas.width * self._zoom)) // 2
        offset_y = (self.height() - int(self._canvas.height * self._zoom)) // 2

        x = int((screen_x - offset_x) / self._zoom)
        y = int((screen_y - offset_y) / self._zoom)

        return (max(0, min(x, self._canvas.width - 1)),
                max(0, min(y, self._canvas.height - 1)))
