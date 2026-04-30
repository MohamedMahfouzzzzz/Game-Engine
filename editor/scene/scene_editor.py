# /**************************************************************************/
# /*  scene_editor.py                                                       */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Scene editor widget - Modern viewport with gizmos and design system.

Features:
- Selection gizmos with handles
- Transform controls (move, rotate, scale)
- Color-coded axis indicators
- Improved visual feedback
"""

from typing import Optional, Dict, Any, List, Tuple
from enum import Enum, auto
import math

from PySide6.QtCore import Qt, Signal, QRectF, QPointF
from PySide6.QtGui import (
    QPainter, QColor, QPen, QBrush, QMouseEvent, QWheelEvent,
    QKeyEvent, QFont, QFontMetrics, QPainterPath
)
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QFrame

from engine.core.node_base import Node, Node2D
from engine.core.scene import Scene
from engine.core.nodes2d import Vector2
from engine.scene2d import Sprite2D, Camera2D
from ..theme import EditorColors, EditorFonts, EditorSpacing


class GizmoMode(Enum):
    """Gizmo interaction modes."""
    SELECT = auto()
    MOVE = auto()
    ROTATE = auto()
    SCALE = auto()


class ViewportGizmo:
    """Visual gizmo for node manipulation."""

    HANDLE_SIZE = 8
    AXIS_LENGTH = 60

    def __init__(self):
        self.mode = GizmoMode.SELECT
        self.hovered_handle: Optional[str] = None
        self.active_handle: Optional[str] = None

    def draw(self, painter: QPainter, node: Node2D, world_to_screen, zoom: float) -> None:
        """Draw gizmo for selected node."""
        if not isinstance(node, Node2D):
            return

        screen_pos = world_to_screen(node.position)
        handle_size = int(self.HANDLE_SIZE / zoom)
        axis_length = int(self.AXIS_LENGTH / zoom)

        # Draw position marker
        self._draw_position_marker(painter, screen_pos, handle_size)

        if self.mode == GizmoMode.MOVE:
            self._draw_move_gizmo(painter, screen_pos, axis_length, handle_size)
        elif self.mode == GizmoMode.ROTATE:
            self._draw_rotate_gizmo(painter, screen_pos, axis_length)
        elif self.mode == GizmoMode.SCALE:
            self._draw_scale_gizmo(painter, screen_pos, axis_length, handle_size)

    def _draw_position_marker(self, painter: QPainter, pos: Vector2, size: int) -> None:
        """Draw crosshair at node position."""
        color = EditorColors.GIZMO_SELECTED
        pen = QPen(color, 2)
        painter.setPen(pen)

        # Draw crosshair
        half = size // 2
        painter.drawLine(int(pos.x - half), int(pos.y), int(pos.x + half), int(pos.y))
        painter.drawLine(int(pos.x), int(pos.y - half), int(pos.x), int(pos.y + half))

        # Draw center dot
        painter.setBrush(QBrush(color))
        painter.drawEllipse(int(pos.x - 3), int(pos.y - 3), 6, 6)

    def _draw_move_gizmo(self, painter: QPainter, pos: Vector2, axis_length: int, handle_size: int) -> None:
        """Draw move gizmo with X/Y axis handles."""
        # X axis (Red)
        x_color = EditorColors.GRID_AXIS_X
        x_pen = QPen(x_color, 2)
        painter.setPen(x_pen)
        painter.drawLine(int(pos.x), int(pos.y), int(pos.x + axis_length), int(pos.y))

        # X handle
        self._draw_axis_handle(painter, pos.x + axis_length, pos.y, handle_size, x_color, "X")

        # Y axis (Green)
        y_color = EditorColors.GRID_AXIS_Y
        y_pen = QPen(y_color, 2)
        painter.setPen(y_pen)
        painter.drawLine(int(pos.x), int(pos.y), int(pos.x), int(pos.y + axis_length))

        # Y handle
        self._draw_axis_handle(painter, pos.x, pos.y + axis_length, handle_size, y_color, "Y")

    def _draw_rotate_gizmo(self, painter: QPainter, pos: Vector2, radius: int) -> None:
        """Draw rotation gizmo."""
        color = EditorColors.GIZMO_ACTIVE
        pen = QPen(color, 2, Qt.PenStyle.DashLine)
        painter.setPen(pen)

        # Draw circle
        painter.drawEllipse(int(pos.x - radius), int(pos.y - radius), radius * 2, radius * 2)

        # Draw rotation handle
        pen.setStyle(Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        painter.drawLine(int(pos.x), int(pos.y - radius - 5), int(pos.x), int(pos.y - radius - 15))
        painter.setBrush(QBrush(color))
        painter.drawEllipse(int(pos.x - 4), int(pos.y - radius - 19), 8, 8)

    def _draw_scale_gizmo(self, painter: QPainter, pos: Vector2, axis_length: int, handle_size: int) -> None:
        """Draw scale gizmo."""
        # Draw uniform scale box
        box_size = handle_size + 4
        color = EditorColors.GIZMO_ACTIVE
        pen = QPen(color, 2)
        painter.setPen(pen)
        painter.setBrush(QBrush(QColor(255, 255, 255, 100)))
        painter.drawRect(int(pos.x - box_size/2), int(pos.y - box_size/2), box_size, box_size)

        # Draw axis handles
        self._draw_move_gizmo(painter, pos, axis_length, handle_size)

    def _draw_axis_handle(self, painter: QPainter, x: float, y: float, size: int, color: QColor, label: str) -> None:
        """Draw axis handle."""
        half = size // 2
        painter.setPen(QPen(color, 1))
        painter.setBrush(QBrush(color))

        # Draw square handle
        painter.drawRect(int(x - half), int(y - half), size, size)

        # Draw label
        painter.setPen(QPen(EditorColors.TEXT_PRIMARY))
        font = painter.font()
        font.setBold(True)
        font.setPointSize(8)
        painter.setFont(font)
        painter.drawText(int(x + half + 2), int(y + 4), label)


class ViewportWidget(QWidget):
    """Viewport widget with gizmos and modern rendering."""

    node_selected = Signal(Node)
    transform_changed = Signal(Node)  # Emitted when node is transformed via gizmo

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene: Optional[Scene] = None
        self.camera: Optional[Camera2D] = None

        # Viewport state
        self.zoom = 1.0
        self.offset = Vector2(0, 0)
        self.grid_size = 32
        self.show_grid = True
        self.show_origin = True
        self.show_gizmos = True

        # Gizmo
        self.gizmo = ViewportGizmo()
        self.gizmo_mode = GizmoMode.MOVE

        # Interaction state
        self.dragging = False
        self.drag_start = Vector2(0, 0)
        self.drag_offset = Vector2(0, 0)
        self.selected_node: Optional[Node] = None
        self.transforming = False
        self.transform_start_pos = Vector2(0, 0)

        # Set minimum size
        self.setMinimumSize(400, 300)

        # Enable mouse tracking
        self.setMouseTracking(True)

        # Set background color
        self.setStyleSheet(f"background-color: {EditorColors.to_stylesheet(EditorColors.BG_PRIMARY)};")
    
    def set_scene(self, scene: Scene) -> None:
        """Set the current scene."""
        self.scene = scene
        self.update()
    
    def set_camera(self, camera: Optional[Camera2D]) -> None:
        """Set the active camera."""
        self.camera = camera
        self.update()
    
    def set_zoom(self, zoom: float) -> None:
        """Set viewport zoom level."""
        self.zoom = max(0.1, min(10.0, zoom))
        self.update()
    
    def set_offset(self, offset: Vector2) -> None:
        """Set viewport offset."""
        self.offset = offset
        self.update()
    
    def world_to_screen(self, world_pos: Vector2) -> Vector2:
        """Convert world coordinates to screen coordinates."""
        screen_x = (world_pos.x - self.offset.x) * self.zoom + self.width() / 2
        screen_y = (world_pos.y - self.offset.y) * self.zoom + self.height() / 2
        return Vector2(screen_x, screen_y)
    
    def screen_to_world(self, screen_pos: Vector2) -> Vector2:
        """Convert screen coordinates to world coordinates."""
        world_x = (screen_pos.x - self.width() / 2) / self.zoom + self.offset.x
        world_y = (screen_pos.y - self.height() / 2) / self.zoom + self.offset.y
        return Vector2(world_x, world_y)
    
    def paintEvent(self, event) -> None:
        """Paint the viewport with design system colors."""
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # Clear background
            painter.fillRect(self.rect(), EditorColors.VIEWPORT_BG)

            if not self.scene:
                # Show empty state
                painter.setPen(QPen(EditorColors.TEXT_SECONDARY))
                font = EditorFonts.empty_state()
                painter.setFont(font)
                painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No scene loaded\nCreate or open a project")
                return

            # Draw grid
            if self.show_grid:
                self._draw_grid(painter)

            # Draw origin
            if self.show_origin:
                self._draw_origin(painter)

            # Draw scene nodes
            self._draw_scene(painter)

            # Draw gizmo for selected node
            if self.show_gizmos and self.selected_node and isinstance(self.selected_node, Node2D):
                self.gizmo.mode = self.gizmo_mode
                self.gizmo.draw(painter, self.selected_node, self.world_to_screen, self.zoom)
        finally:
            painter.end()
    
    def _draw_grid(self, painter: QPainter) -> None:
        """Draw background grid with design system colors."""
        # Calculate visible grid range
        top_left = self.screen_to_world(Vector2(0, 0))
        bottom_right = self.screen_to_world(Vector2(self.width(), self.height()))

        # Draw grid lines
        minor_color = EditorColors.GRID_MINOR
        major_color = EditorColors.GRID_MAJOR

        start_x = int(top_left.x / self.grid_size) * self.grid_size
        start_y = int(top_left.y / self.grid_size) * self.grid_size

        # Draw minor grid
        painter.setPen(QPen(minor_color, 1))
        for x in range(int(start_x), int(bottom_right.x) + self.grid_size, self.grid_size):
            if x % 128 != 0:  # Skip major lines
                screen_pos = self.world_to_screen(Vector2(x, 0))
                painter.drawLine(int(screen_pos.x), 0, int(screen_pos.x), self.height())

        for y in range(int(start_y), int(bottom_right.y) + self.grid_size, self.grid_size):
            if y % 128 != 0:  # Skip major lines
                screen_pos = self.world_to_screen(Vector2(0, y))
                painter.drawLine(0, int(screen_pos.y), self.width(), int(screen_pos.y))

        # Draw major grid (every 128 units)
        painter.setPen(QPen(major_color, 1))
        for x in range(int(start_x), int(bottom_right.x) + self.grid_size, self.grid_size):
            if x % 128 == 0:
                screen_pos = self.world_to_screen(Vector2(x, 0))
                painter.drawLine(int(screen_pos.x), 0, int(screen_pos.x), self.height())

        for y in range(int(start_y), int(bottom_right.y) + self.grid_size, self.grid_size):
            if y % 128 == 0:
                screen_pos = self.world_to_screen(Vector2(0, y))
                painter.drawLine(0, int(screen_pos.y), self.width(), int(screen_pos.y))
    
    def _draw_origin(self, painter: QPainter) -> None:
        """Draw world origin."""
        origin = self.world_to_screen(Vector2(0, 0))
        
        # Draw X axis (red)
        painter.setPen(QPen(QColor(255, 0, 0), 2))
        painter.drawLine(int(origin.x), int(origin.y), int(origin.x + 50), int(origin.y))
        
        # Draw Y axis (green)
        painter.setPen(QPen(QColor(0, 255, 0), 2))
        painter.drawLine(int(origin.x), int(origin.y), int(origin.x), int(origin.y + 50))
    
    def _draw_scene(self, painter: QPainter) -> None:
        """Draw all scene nodes."""
        if self.scene:
            self._draw_node_recursive(painter, self.scene.root)
    
    def _draw_node_recursive(self, painter: QPainter, node: Node) -> None:
        """Draw node and all children."""
        if isinstance(node, Node2D):
            self._draw_node2d(painter, node)
        
        # Draw children
        if hasattr(node, 'children'):
            for child in node.children:
                self._draw_node_recursive(painter, child)
    
    def _draw_node2d(self, painter: QPainter, node: Node2D) -> None:
        """Draw a 2D node with design system styling."""
        world_pos = self.world_to_screen(node.position)

        # Get node type color
        from ..docks.scene_tree_dock import NODE_COLORS
        node_type_name = node.__class__.__name__
        node_color = NODE_COLORS.get(node_type_name, EditorColors.NODE_GENERIC)

        # Draw node icon/marker
        icon_size = 12
        painter.setPen(QPen(node_color, 2))
        painter.setBrush(QBrush(node_color.darker(120)))
        painter.drawRect(int(world_pos.x - icon_size/2), int(world_pos.y - icon_size/2), icon_size, icon_size)

        # Draw node name
        painter.setPen(QPen(EditorColors.TEXT_PRIMARY))
        font = EditorFonts.node_tree_item()
        painter.setFont(font)
        painter.drawText(int(world_pos.x + icon_size), int(world_pos.y + 4), node.name)

        # Draw node type indicator
        type_text = f" ({node_type_name})"
        painter.setPen(QPen(EditorColors.TEXT_SECONDARY))
        metrics = QFontMetrics(font)
        name_width = metrics.horizontalAdvance(node.name)
        painter.drawText(int(world_pos.x + icon_size + name_width + 4), int(world_pos.y + 4), type_text)

        # Highlight selected node (gizmo handles this, but add subtle outline)
        if node == self.selected_node:
            painter.setPen(QPen(EditorColors.GIZMO_SELECTED, 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(int(world_pos.x - icon_size/2 - 3), int(world_pos.y - icon_size/2 - 3), icon_size + 6, icon_size + 6)

        # Draw specific node types
        if isinstance(node, Sprite2D):
            self._draw_sprite(painter, node)
        elif isinstance(node, Camera2D):
            self._draw_camera(painter, node)
    
    def _draw_sprite(self, painter: QPainter, sprite: Sprite2D) -> None:
        """Draw sprite node with icon representation."""
        pos = self.world_to_screen(sprite.position)

        # Draw sprite icon (since we don't have actual textures yet)
        size = 32
        painter.setPen(QPen(EditorColors.NODE_SPRITE, 2))
        painter.setBrush(QBrush(EditorColors.NODE_SPRITE.darker(150)))
        painter.drawRect(int(pos.x - size/2), int(pos.y - size/2), size, size)

        # Draw sprite icon
        painter.setPen(QPen(EditorColors.TEXT_PRIMARY))
        font = EditorFonts.get_ui_font(EditorFonts.SIZE_SM)
        painter.setFont(font)
        painter.drawText(int(pos.x - 6), int(pos.y + 4), "🖼️")
    
    def _draw_camera(self, painter: QPainter, camera: Camera2D) -> None:
        """Draw camera node with view frustum."""
        pos = self.world_to_screen(camera.position)

        # Draw camera view rectangle
        view_width = 320 * camera.zoom.x if hasattr(camera, 'zoom') else 320
        view_height = 180 * camera.zoom.y if hasattr(camera, 'zoom') else 180

        top_left = self.world_to_screen(Vector2(
            camera.position.x - view_width / 2,
            camera.position.y - view_height / 2
        ))

        # Camera color
        cam_color = EditorColors.NODE_CAMERA

        painter.setPen(QPen(cam_color, 2, Qt.PenStyle.DashLine))
        painter.setBrush(QBrush(cam_color.darker(200)))
        painter.drawRect(int(top_left.x), int(top_left.y),
                        int(view_width * self.zoom), int(view_height * self.zoom))

        # Draw camera icon
        painter.setPen(QPen(EditorColors.TEXT_PRIMARY))
        font = EditorFonts.get_ui_font(EditorFonts.SIZE_SM)
        painter.setFont(font)
        painter.drawText(int(pos.x - 6), int(pos.y + 4), "📷")

    def set_gizmo_mode(self, mode: GizmoMode) -> None:
        """Set the current gizmo mode."""
        self.gizmo_mode = mode
        self.gizmo.mode = mode
        self.update()
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Select node
            world_pos = self.screen_to_world(Vector2(event.x(), event.y()))
            self._select_node_at_position(world_pos)
        
        elif event.button() == Qt.MouseButton.MiddleButton:
            # Start panning
            self.dragging = True
            self.drag_start = Vector2(event.x(), event.y())
            self.drag_offset = self.offset
    
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle mouse move."""
        if self.dragging:
            # Pan viewport
            current = Vector2(event.x(), event.y())
            delta = current - self.drag_start
            self.offset = Vector2(
                self.drag_offset.x - delta.x / self.zoom,
                self.drag_offset.y - delta.y / self.zoom
            )
            self.update()
    
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Handle mouse release."""
        if event.button() == Qt.MouseButton.MiddleButton:
            self.dragging = False
    
    def wheelEvent(self, event: QWheelEvent) -> None:
        """Handle mouse wheel for zooming."""
        delta = event.angleDelta().y() / 120
        zoom_factor = 1.1 if delta > 0 else 0.9
        self.set_zoom(self.zoom * zoom_factor)
    
    def _select_node_at_position(self, world_pos: Vector2) -> None:
        """Select node at world position."""
        if self.scene:
            node = self._find_node_at_position(self.scene.root, world_pos)
            if node:
                self.selected_node = node
                self.node_selected.emit(node)
                self.update()
    
    def _find_node_at_position(self, node: Node, world_pos: Vector2) -> Optional[Node]:
        """Find node at position (recursive)."""
        if isinstance(node, Node2D):
            # Simple bounding box check
            if (abs(node.position.x - world_pos.x) < 20 and 
                abs(node.position.y - world_pos.y) < 20):
                return node
        
        # Check children
        if hasattr(node, 'children'):
            for child in node.children:
                result = self._find_node_at_position(child, world_pos)
                if result:
                    return result
        
        return None


class SceneEditor(QWidget):
    """Main scene editor widget."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene: Optional[Scene] = None
        self.camera: Optional[Camera2D] = None
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Setup modern scene editor UI with gizmo controls."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(EditorSpacing.XS, EditorSpacing.XS, EditorSpacing.XS, EditorSpacing.XS)
        layout.setSpacing(EditorSpacing.SM)

        # Toolbar
        toolbar = self._create_toolbar()
        layout.addWidget(toolbar)

        # Viewport
        self.viewport = ViewportWidget()
        layout.addWidget(self.viewport)

        # Connect signals
        self.viewport.node_selected.connect(self.on_node_selected)

    def _create_toolbar(self) -> QFrame:
        """Create modern toolbar with gizmo controls."""
        toolbar = QFrame()
        toolbar.setFixedHeight(EditorSpacing.TOOLBAR_HEIGHT_SMALL)
        toolbar.setStyleSheet(f"""
            QFrame {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_TERTIARY)};
                border-bottom: 1px solid {EditorColors.to_stylesheet(EditorColors.BORDER_DEFAULT)};
            }}
            QPushButton {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BUTTON_SECONDARY_BG)};
                border: 1px solid {EditorColors.to_stylesheet(EditorColors.BORDER_DEFAULT)};
                color: {EditorColors.to_stylesheet(EditorColors.TEXT_PRIMARY)};
                padding: 4px 8px;
                border-radius: {EditorSpacing.RADIUS_SM}px;
                min-width: 28px;
            }}
            QPushButton:checked {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BUTTON_PRIMARY_BG)};
                border-color: {EditorColors.to_stylesheet(EditorColors.BUTTON_PRIMARY_BG)};
            }}
            QPushButton:hover {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BUTTON_SECONDARY_HOVER)};
            }}
            QLabel {{
                color: {EditorColors.to_stylesheet(EditorColors.TEXT_SECONDARY)};
            }}
            QComboBox {{
                background-color: {EditorColors.to_stylesheet(EditorColors.INPUT_BG)};
                border: 1px solid {EditorColors.to_stylesheet(EditorColors.INPUT_BORDER)};
                color: {EditorColors.to_stylesheet(EditorColors.TEXT_PRIMARY)};
                padding: 4px 8px;
                border-radius: {EditorSpacing.RADIUS_SM}px;
            }}
        """)

        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(EditorSpacing.SM, 0, EditorSpacing.SM, 0)
        toolbar_layout.setSpacing(EditorSpacing.XS)

        # Gizmo mode buttons
        self.gizmo_buttons: Dict[GizmoMode, QPushButton] = {}

        select_btn = QPushButton("🔍")
        select_btn.setCheckable(True)
        select_btn.setToolTip("Select Mode (Q)")
        select_btn.clicked.connect(lambda: self._set_gizmo_mode(GizmoMode.SELECT))
        toolbar_layout.addWidget(select_btn)
        self.gizmo_buttons[GizmoMode.SELECT] = select_btn

        move_btn = QPushButton("↔️")
        move_btn.setCheckable(True)
        move_btn.setChecked(True)
        move_btn.setToolTip("Move Mode (W)")
        move_btn.clicked.connect(lambda: self._set_gizmo_mode(GizmoMode.MOVE))
        toolbar_layout.addWidget(move_btn)
        self.gizmo_buttons[GizmoMode.MOVE] = move_btn

        rotate_btn = QPushButton("🔄")
        rotate_btn.setCheckable(True)
        rotate_btn.setToolTip("Rotate Mode (E)")
        rotate_btn.clicked.connect(lambda: self._set_gizmo_mode(GizmoMode.ROTATE))
        toolbar_layout.addWidget(rotate_btn)
        self.gizmo_buttons[GizmoMode.ROTATE] = rotate_btn

        scale_btn = QPushButton("⤢")
        scale_btn.setCheckable(True)
        scale_btn.setToolTip("Scale Mode (R)")
        scale_btn.clicked.connect(lambda: self._set_gizmo_mode(GizmoMode.SCALE))
        toolbar_layout.addWidget(scale_btn)
        self.gizmo_buttons[GizmoMode.SCALE] = scale_btn

        toolbar_layout.addSpacing(EditorSpacing.MD)

        # Zoom controls
        zoom_label = QLabel("🔍")
        toolbar_layout.addWidget(zoom_label)

        self.zoom_combo = QComboBox()
        self.zoom_combo.addItems(["25%", "50%", "100%", "200%", "400%"])
        self.zoom_combo.setCurrentText("100%")
        self.zoom_combo.currentTextChanged.connect(self._on_zoom_changed)
        self.zoom_combo.setFixedWidth(70)
        toolbar_layout.addWidget(self.zoom_combo)

        toolbar_layout.addSpacing(EditorSpacing.MD)

        # Grid toggle
        self.grid_btn = QPushButton("⊞")
        self.grid_btn.setCheckable(True)
        self.grid_btn.setChecked(True)
        self.grid_btn.setToolTip("Toggle Grid (G)")
        self.grid_btn.clicked.connect(self._toggle_grid)
        toolbar_layout.addWidget(self.grid_btn)

        # Gizmos toggle
        self.gizmos_btn = QPushButton("➕")
        self.gizmos_btn.setCheckable(True)
        self.gizmos_btn.setChecked(True)
        self.gizmos_btn.setToolTip("Toggle Gizmos")
        self.gizmos_btn.clicked.connect(self._toggle_gizmos)
        toolbar_layout.addWidget(self.gizmos_btn)

        toolbar_layout.addStretch()

        return toolbar

    def _set_gizmo_mode(self, mode: GizmoMode) -> None:
        """Set the current gizmo mode."""
        # Uncheck all buttons
        for btn in self.gizmo_buttons.values():
            btn.setChecked(False)

        # Check the selected button
        if mode in self.gizmo_buttons:
            self.gizmo_buttons[mode].setChecked(True)

        # Update viewport
        self.viewport.set_gizmo_mode(mode)
    
    def set_scene(self, scene: Scene) -> None:
        """Set the current scene."""
        self.scene = scene
        self.viewport.set_scene(scene)
        
        # Find first camera in scene
        self.camera = self._find_camera(scene.root) if scene else None
        self.viewport.set_camera(self.camera)
    
    def _find_camera(self, node: Node) -> Optional[Camera2D]:
        """Find first camera node in scene."""
        if isinstance(node, Camera2D):
            return node
        
        if hasattr(node, 'children'):
            for child in node.children:
                result = self._find_camera(child)
                if result:
                    return result
        
        return None
    
    def _on_zoom_changed(self, text: str) -> None:
        """Handle zoom change."""
        zoom_map = {
            "25%": 0.25,
            "50%": 0.5,
            "100%": 1.0,
            "200%": 2.0,
            "400%": 4.0
        }
        zoom = zoom_map.get(text, 1.0)
        self.viewport.set_zoom(zoom)
    
    def _toggle_grid(self) -> None:
        """Toggle grid visibility."""
        self.viewport.show_grid = not self.viewport.show_grid
        self.viewport.update()

    def _toggle_gizmos(self) -> None:
        """Toggle gizmos visibility."""
        self.viewport.show_gizmos = not self.viewport.show_gizmos
        self.viewport.update()

    def on_node_selected(self, node: Node) -> None:
        """Handle node selection."""
        # TODO: Update inspector
        pass
    
    def refresh(self) -> None:
        """Refresh the scene editor."""
        self.viewport.update()
