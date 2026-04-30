# /**************************************************************************/
# /*  viewport.py                                                           */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QBrush, QColor, QImage, QPainter, QPen, QFont, QPixmap, QTransform
from PySide6.QtWidgets import QFrame

from engine.core.node import Node, Node2D, Scene
from engine.core.nodes import Sprite, TileMap, Button, Label


class ViewportWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #1a1a2e; border: 1px solid #444;")
        self.scene: Optional[Scene] = None
        self.selected_node: Optional[Node] = None
        self.pan_x: float = 0.0
        self.pan_y: float = 0.0
        self.zoom: float = 1.0
        self.grid_enabled: bool = True
        self.grid_size: int = 32
        self.pan_start = (0, 0)
        
        # Texture cache
        self._texture_cache: Dict[str, QPixmap] = {}
        self._sorted_children_cache: Dict[int, Tuple[int, Tuple[str, ...], List[Node]]] = {}
        self._project_root: Optional[str] = None
        
        # Play mode
        self.play_mode: bool = False
        self.show_colliders: bool = False
        self.show_gizmos: bool = True
        
        # Camera follow target (e.g., Player)
        self.camera_target: Optional[Node2D] = None
        self.camera_smooth: float = 0.1
        
        # Game loop timer
        self._game_timer = QTimer(self)
        self._game_timer.timeout.connect(self._on_game_update)
        self._game_fps = 60
        
        # Input state
        self._keys_pressed: set = set()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def set_scene(self, scene: Scene) -> None:
        self.scene = scene
        self._sorted_children_cache.clear()
        self.update()

    def select_node(self, node: Node) -> None:
        self.selected_node = node
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            pos = event.position()
            self.pan_start = (pos.x(), pos.y())

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.MiddleButton:
            pos = event.position()
            dx = pos.x() - self.pan_start[0]
            dy = pos.y() - self.pan_start[1]
            self.pan_x += dx
            self.pan_y += dy
            self.pan_start = (pos.x(), pos.y())
            self.update()

    def wheelEvent(self, event):
        self.zoom *= 1.1 if event.angleDelta().y() > 0 else 1 / 1.1
        self.zoom = max(0.1, min(self.zoom, 10.0))
        self.update()
    
    def paintEvent(self, event) -> None:
        """Render the scene."""
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Fill background
            painter.fillRect(self.rect(), QColor(26, 26, 46))
            
            # Apply camera transform
            painter.translate(self.pan_x, self.pan_y)
            painter.scale(self.zoom, self.zoom)
            
            # Draw grid
            if self.grid_enabled:
                self._draw_grid(painter)
            
            # Draw scene
            if self.scene and self.scene.root:
                self._draw_node(painter, self.scene.root, 0, 0)
        finally:
            painter.end()
    
    def _draw_grid(self, painter: QPainter) -> None:
        """Draw the grid."""
        pen = QPen(QColor(80, 80, 80))
        pen.setWidthF(1.0 / self.zoom)
        painter.setPen(pen)
        
        width = self.width()
        height = self.height()
        
        # Calculate visible grid range
        start_x = int(-self.pan_x / self.zoom / self.grid_size) * self.grid_size
        start_y = int(-self.pan_y / self.zoom / self.grid_size) * self.grid_size
        end_x = start_x + int(width / self.zoom) + self.grid_size * 2
        end_y = start_y + int(height / self.zoom) + self.grid_size * 2
        
        for x in range(start_x, end_x, self.grid_size):
            painter.drawLine(x, start_y, x, end_y)
        for y in range(start_y, end_y, self.grid_size):
            painter.drawLine(start_x, y, end_x, y)
        
        # Draw origin
        origin_pen = QPen(QColor(200, 50, 50))
        origin_pen.setWidthF(2.0 / self.zoom)
        painter.setPen(origin_pen)
        painter.drawLine(-20, 0, 20, 0)
        painter.drawLine(0, -20, 0, 20)
    
    def _draw_node(self, painter: QPainter, node: Node, parent_x: float, parent_y: float) -> None:
        """Recursively draw a node and its children."""
        x, y = parent_x, parent_y
        
        # Get node position if it's a Node2D
        if isinstance(node, Node2D):
            pos = node.get_position()
            x += pos[0]
            y += pos[1]
            
            # Apply rotation and scale
            painter.save()
            painter.translate(x, y)
            
            if hasattr(node, 'rotation'):
                painter.rotate(node.rotation)
            
            scale = getattr(node, 'scale', (1, 1))
            if hasattr(scale, '__getitem__'):
                painter.scale(scale[0], scale[1])
            
            # Draw based on node type
            if isinstance(node, Sprite):
                self._draw_sprite(painter, node)
            elif isinstance(node, TileMap):
                self._draw_tilemap(painter, node)
            elif isinstance(node, Button):
                self._draw_button(painter, node)
            elif isinstance(node, Label):
                self._draw_label(painter, node)
            else:
                # Generic Node2D - draw a square
                self._draw_node2d_gizmo(painter, node)
            
            painter.restore()
        else:
            # Regular Node - just a point
            painter.setBrush(QBrush(QColor(100, 150, 200)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(int(x) - 4, int(y) - 4, 8, 8)
        
        # Draw selection highlight
        if node == self.selected_node:
            self._draw_selection(painter, x, y)
        
        # Draw children
        for child in self._get_sorted_children(node):
            self._draw_node(painter, child, x, y)

    def _get_sorted_children(self, node: Node) -> List[Node]:
        """Return children in cached render order.

        The cache is invalidated by Node.add_child/remove_child via
        ``_tree_version``/``_sort_dirty``.  This avoids an O(n log n) sort every
        paint when scene membership and draw order are unchanged.
        """
        children = node.children
        version = getattr(node, "_tree_version", 0)
        signature = tuple(
            f"{getattr(child, 'uid', id(child))}:{getattr(child, 'z_index', 0)}:{int(getattr(child, 'visible', True))}"
            for child in children
        )
        cache_key = id(node)
        cached = self._sorted_children_cache.get(cache_key)
        if cached and cached[0] == version and cached[1] == signature and not getattr(node, "_sort_dirty", False):
            return cached[2]

        indexed_children = list(enumerate(children))
        ordered = [
            child for _, child in sorted(
                indexed_children,
                key=lambda item: (
                    getattr(item[1], "z_index", 0),
                    item[1].get_position()[1]
                    if getattr(node, "y_sort_enabled", False) and isinstance(item[1], Node2D)
                    else 0,
                    item[0],
                ),
            )
        ]
        self._sorted_children_cache[cache_key] = (version, signature, ordered)
        if hasattr(node, "_sort_dirty"):
            node._sort_dirty = False
        return ordered
    
    def _draw_sprite(self, painter: QPainter, sprite: Sprite) -> None:
        """Draw a sprite with actual texture."""
        texture = self._load_texture(getattr(sprite, 'texture_path', None))
        
        centered = getattr(sprite, 'centered', True)
        flip_h = getattr(sprite, 'flip_h', False)
        flip_v = getattr(sprite, 'flip_v', False)
        
        if texture and not texture.isNull():
            # Get texture size
            w = texture.width()
            h = texture.height()
            
            # Apply flipping with transform
            transform = QTransform()
            x_offset = 0
            y_offset = 0
            
            if centered:
                x_offset = -w // 2
                y_offset = -h // 2
            
            if flip_h:
                transform.scale(-1, 1)
                x_offset = -x_offset - w
            
            if flip_v:
                transform.scale(1, -1)
                y_offset = -y_offset - h
            
            painter.setTransform(transform, True)
            painter.drawPixmap(int(x_offset), int(y_offset), texture)
            painter.setTransform(transform.inverted()[0], True)
        else:
            # No texture - draw placeholder
            w, h = getattr(sprite, 'texture_size', (32, 32))
            if w == 0 or h == 0:
                w, h = 32, 32
            
            # Draw colored rectangle
            painter.setBrush(QBrush(QColor(100, 150, 200, 100)))
            painter.setPen(QPen(QColor(100, 150, 200), 2))
            
            if centered:
                painter.drawRect(-w//2, -h//2, w, h)
                painter.drawText(-w//2, -h//2, w, h, Qt.AlignmentFlag.AlignCenter, sprite.name[:4])
            else:
                painter.drawRect(0, 0, w, h)
                painter.drawText(0, 0, w, h, Qt.AlignmentFlag.AlignCenter, sprite.name[:4])
    
    def _draw_tilemap(self, painter: QPainter, tilemap: TileMap) -> None:
        """Draw a tilemap with actual tiles."""
        tile_size = 32
        
        # Check if there's tile data
        tile_data = tilemap.get_property("tile_map_data", None)
        has_data = tile_data is not None and len(str(tile_data)) > 10
        
        if has_data:
            # Parse and draw actual tiles
            tiles = self._parse_tile_data(str(tile_data))
            
            if tiles:
                # Draw actual tiles from data
                for x, y, tile_id in tiles:
                    if tile_id >= 0:
                        color = self._get_tile_color(tile_id)
                        painter.setBrush(QBrush(color))
                        painter.setPen(QPen(QColor(30, 30, 30)))
                        painter.drawRect(x * tile_size, y * tile_size, tile_size, tile_size)
            else:
                # Couldn't parse - draw fallback pattern
                self._draw_fallback_tiles(painter, tile_size)
        else:
            # Empty tilemap - draw fallback pattern
            self._draw_fallback_tiles(painter, tile_size)
        
        # Draw grid lines
        pen = QPen(QColor(50, 50, 50, 100))
        pen.setWidth(1)
        painter.setPen(pen)
        for i in range(25):
            painter.drawLine(i * tile_size, 0, i * tile_size, 20 * tile_size)
            painter.drawLine(0, i * tile_size, 25 * tile_size, i * tile_size)
        
        # Draw label
        painter.setPen(QPen(QColor(200, 200, 200)))
        painter.setFont(QFont("Arial", 10))
        label = f"TileMap: {tilemap.name} ({'has data' if has_data else 'empty'})"
        painter.drawText(5, 15, label)
    
    def _parse_tile_data(self, data: str) -> List[Tuple[int, int, int]]:
        """Parse PackedByteArray tile data. Returns list of (x, y, tile_id)."""
        tiles = []
        try:
            import base64
            import struct
            
            # Decode base64
            decoded = base64.b64decode(data)
            
            # Parse as 8-byte chunks: x (2 bytes), y (2 bytes), tile_id (4 bytes)
            for i in range(0, len(decoded) - 7, 8):
                chunk = decoded[i:i+8]
                if len(chunk) == 8:
                    # Little-endian format
                    x = struct.unpack('<h', chunk[0:2])[0]
                    y = struct.unpack('<h', chunk[2:4])[0]
                    tile_id = struct.unpack('<I', chunk[4:8])[0]
                    if tile_id != 0xFFFFFFFF:  # Not empty
                        tiles.append((x, y, tile_id & 0xFFFF))
        except Exception as e:
            print(f"TileMap parse error: {e}")
        
        return tiles
    
    def _draw_fallback_tiles(self, painter: QPainter, tile_size: int) -> None:
        """Draw sample tiles when no data available."""
        # Draw a simple platform pattern
        for col in range(15):
            # Ground row
            color = QColor(139, 69, 19)  # Brown ground
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor(100, 50, 10)))
            painter.drawRect(col * tile_size, 10 * tile_size, tile_size, tile_size)
            
            # Grass on top
            grass_color = QColor(34, 139, 34)
            painter.setBrush(QBrush(grass_color))
            painter.drawRect(col * tile_size, 9 * tile_size, tile_size, tile_size)
    
    def _get_tile_color(self, tile_id: int) -> QColor:
        """Get color for a tile based on ID."""
        colors = [
            QColor(139, 69, 19),   # 0: Brown (dirt)
            QColor(34, 139, 34),   # 1: Green (grass)
            QColor(100, 100, 100), # 2: Gray (stone)
            QColor(160, 82, 45),   # 3: Sienna
            QColor(139, 90, 43),   # 4: Dark brown
            QColor(0, 100, 0),     # 5: Dark green
            QColor(200, 150, 100), # 6: Sand
            QColor(50, 50, 50),    # 7: Dark stone
            QColor(255, 255, 255), # 8: White
            QColor(0, 0, 255),     # 9: Blue (water)
            QColor(255, 0, 0),     # 10: Red
            QColor(255, 255, 0),   # 11: Yellow
            QColor(255, 0, 255),   # 12: Magenta
            QColor(0, 255, 255),   # 13: Cyan
            QColor(128, 128, 128), # 14: Gray
            QColor(0, 0, 0),       # 15: Black
        ]
        return colors[tile_id % len(colors)]
    
    def _draw_button(self, painter: QPainter, button: Button) -> None:
        """Draw a button."""
        w, h = 100, 30
        
        # Button background
        color = QColor(70, 70, 70) if getattr(button, 'disabled', False) else QColor(100, 100, 200)
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(QColor(150, 150, 150), 2))
        painter.drawRoundedRect(0, 0, w, h, 5, 5)
        
        # Text
        painter.setPen(QPen(QColor(255, 255, 255)))
        painter.setFont(QFont("Arial", 10))
        text = getattr(button, 'text', 'Button')
        painter.drawText(0, 0, w, h, Qt.AlignmentFlag.AlignCenter, text)
    
    def _draw_label(self, painter: QPainter, label: Label) -> None:
        """Draw a label."""
        painter.setPen(QPen(QColor(255, 255, 255)))
        
        font_size = getattr(label, 'font_size', 14)
        font = QFont("Arial", font_size)
        painter.setFont(font)
        
        text = getattr(label, 'text', 'Label')
        painter.drawText(0, 20, text)
    
    def _draw_node2d_gizmo(self, painter: QPainter, node: Node2D) -> None:
        """Draw a generic Node2D gizmo."""
        # Draw cross
        pen = QPen(QColor(200, 200, 100))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(-10, 0, 10, 0)
        painter.drawLine(0, -10, 0, 10)
        
        # Draw circle
        painter.setBrush(QBrush())
        painter.drawEllipse(-8, -8, 16, 16)
    
    def _draw_selection(self, painter: QPainter, x: float, y: float) -> None:
        """Draw selection highlight."""
        pen = QPen(QColor(255, 255, 0))
        pen.setWidth(2)
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.setBrush(QBrush())
        painter.drawRect(int(x) - 20, int(y) - 20, 40, 40)
    
    def set_play_mode(self, enabled: bool) -> None:
        """Enable/disable play mode."""
        self.play_mode = enabled
        self.show_gizmos = not enabled
        self.grid_enabled = not enabled
        
        if enabled:
            self._game_timer.start(1000 // self._game_fps)
            self._find_camera_target()
        else:
            self._game_timer.stop()
            self.camera_target = None
        
        self.update()
    
    def _find_camera_target(self) -> None:
        """Find player node to follow."""
        if not self.scene:
            return
        
        def find_player(node: Node) -> Optional[Node2D]:
            if isinstance(node, Node2D):
                if 'player' in node.name.lower() or 'hero' in node.name.lower():
                    return node
            for child in node.children:
                result = find_player(child)
                if result:
                    return result
            return None
        
        self.camera_target = find_player(self.scene.root)
    
    def _on_game_update(self) -> None:
        """Game loop update - 60 FPS."""
        if self.camera_target and isinstance(self.camera_target, Node2D):
            # Smooth camera follow
            pos = self.camera_target.get_position()
            target_x = -pos[0] + self.width() / 2 / self.zoom
            target_y = -pos[1] + self.height() / 2 / self.zoom

            self.pan_x += (target_x - self.pan_x) * self.camera_smooth
            self.pan_y += (target_y - self.pan_y) * self.camera_smooth

        self.update()
    
    def set_project_root(self, root: str) -> None:
        """Set project root for loading textures."""
        self._project_root = root
        self._texture_cache.clear()
    
    def _load_texture(self, path: str) -> Optional[QPixmap]:
        """Load texture from file with caching."""
        if not path:
            return None
        
        # Check cache
        if path in self._texture_cache:
            return self._texture_cache[path]
        
        # Try to resolve path
        possible_paths = [path]
        if self._project_root:
            possible_paths.extend([
                os.path.join(self._project_root, path),
                os.path.join(self._project_root, path.replace('res://', '')),
            ])
        
        for p in possible_paths:
            if os.path.exists(p):
                pixmap = QPixmap(p)
                if not pixmap.isNull():
                    self._texture_cache[path] = pixmap
                    return pixmap
        
        return None
    
    def keyPressEvent(self, event) -> None:
        """Handle key press for game input."""
        self._keys_pressed.add(event.key())
        
        # Camera controls in editor mode
        if not self.play_mode:
            if event.key() == Qt.Key.Key_Left:
                self.pan_x += 50
            elif event.key() == Qt.Key.Key_Right:
                self.pan_x -= 50
            elif event.key() == Qt.Key.Key_Up:
                self.pan_y += 50
            elif event.key() == Qt.Key.Key_Down:
                self.pan_y -= 50
            self.update()
    
    def keyReleaseEvent(self, event) -> None:
        """Handle key release."""
        self._keys_pressed.discard(event.key())
