# /**************************************************************************/
# /*  inspector.py                                                          */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

from typing import Optional, Dict, Any, List, Callable
import os

from PySide6.QtWidgets import (
    QDoubleSpinBox, QLabel, QLineEdit, QPlainTextEdit, QTabWidget, QVBoxLayout,
    QWidget, QCheckBox, QSpinBox, QHBoxLayout, QPushButton, QComboBox,
    QGroupBox, QFormLayout, QLineEdit as QLineEditWidget, QFileDialog,
    QListWidget, QListWidgetItem, QScrollArea, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent

from engine.core.node_base import Node, Node2D
from engine.core.nodes2d.sprite2d import Sprite2D
from engine.core.nodes2d.types import Vector2, Color


class ScriptDropArea(QFrame):
    """Drop area for script files with drag & drop support."""
    
    script_dropped = Signal(str)  # emits file path
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setMinimumHeight(100)
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        
        layout = QVBoxLayout(self)
        self.label = QLabel("Drag & Drop script file here\n(.py, .gdl, .gd)")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("color: #888888; font-size: 12px;")
        layout.addWidget(self.label)
        
        self.current_script: Optional[str] = None
        self.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border: 2px dashed #aaaaaa;
                border-radius: 8px;
            }
        """)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                path = urls[0].toLocalFile()
                if path.endswith(('.py', '.gdl', '.gd', '.lua')):
                    event.acceptProposedAction()
                    self.setStyleSheet("""
                        QFrame {
                            background-color: #e8f4ff;
                            border: 2px dashed #2196F3;
                            border-radius: 8px;
                        }
                    """)
    
    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border: 2px dashed #aaaaaa;
                border-radius: 8px;
            }
        """)
    
    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            for url in urls:
                path = url.toLocalFile()
                if path.endswith(('.py', '.gdl', '.gd', '.lua')):
                    self.current_script = path
                    self.label.setText(f"Script: {os.path.basename(path)}")
                    self.label.setStyleSheet("color: #2196F3; font-weight: bold;")
                    self.script_dropped.emit(path)
                    break
        self.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border: 2px dashed #aaaaaa;
                border-radius: 8px;
            }
        """)


class PropertyGroup(QGroupBox):
    """Group of related properties."""
    
    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        self.layout = QFormLayout(self)
        self.layout.setSpacing(8)
        self._widgets: Dict[str, QWidget] = {}
    
    def add_property(self, name: str, widget: QWidget, label: Optional[str] = None):
        """Add a property widget."""
        self._widgets[name] = widget
        self.layout.addRow(label or name, widget)
    
    def get_widget(self, name: str) -> Optional[QWidget]:
        return self._widgets.get(name)


class InspectorWidget(QWidget):
    """Comprehensive node inspector with all properties, signals, and script support."""
    
    property_changed = Signal(str, str, object)  # node_uid, property_name, value
    script_attached = Signal(str, str)  # node_uid, script_path
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_node: Optional[Node] = None
        self._property_groups: Dict[str, PropertyGroup] = {}
        self._callbacks: Dict[str, List[Callable]] = {}
        self.init_ui()
    
    def init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.tabs = QTabWidget(self)
        
        # === Node Tab ===
        self.node_tab = self._create_node_tab()
        self.tabs.addTab(self.node_tab, "Node")
        
        # === Transform Tab ===
        self.transform_tab = self._create_transform_tab()
        self.tabs.addTab(self.transform_tab, "Transform")
        
        # === Node-Specific Tab (dynamic based on node type) ===
        self.specific_tab = self._create_specific_tab()
        self.tabs.addTab(self.specific_tab, "Properties")
        
        # === Signals Tab ===
        self.signals_tab = self._create_signals_tab()
        self.tabs.addTab(self.signals_tab, "Signals")
        
        # === Script Tab with Drag & Drop ===
        self.script_tab = self._create_script_tab()
        self.tabs.addTab(self.script_tab, "Script")
        
        layout.addWidget(self.tabs)
    
    def _create_node_tab(self) -> QWidget:
        """Create the Node tab with basic node properties."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # Basic Properties Group
        basic_group = PropertyGroup("Basic Properties")
        self._property_groups['basic'] = basic_group
        
        # Node Name
        self.node_name_input = QLineEdit()
        self.node_name_input.textChanged.connect(lambda v: self._on_property_changed('name', v))
        basic_group.add_property('name', self.node_name_input, "Name:")
        
        # Node Type (read-only)
        self.node_type_label = QLineEdit()
        self.node_type_label.setReadOnly(True)
        self.node_type_label.setStyleSheet("background-color: #f0f0f0;")
        basic_group.add_property('type', self.node_type_label, "Type:")
        
        # UID (read-only)
        self.node_uid_label = QLineEdit()
        self.node_uid_label.setReadOnly(True)
        self.node_uid_label.setStyleSheet("background-color: #f0f0f0; font-size: 10px;")
        basic_group.add_property('uid', self.node_uid_label, "UID:")
        
        layout.addWidget(basic_group)
        
        # State Group
        state_group = PropertyGroup("State")
        self._property_groups['state'] = state_group
        
        # Enabled checkbox
        self.enabled_check = QCheckBox("Enabled (processes updates)")
        self.enabled_check.stateChanged.connect(lambda v: self._on_property_changed('enabled', bool(v)))
        state_group.layout.addRow(self.enabled_check)
        
        # Visible checkbox
        self.visible_check = QCheckBox("Visible (renders in viewport)")
        self.visible_check.stateChanged.connect(lambda v: self._on_property_changed('visible', bool(v)))
        state_group.layout.addRow(self.visible_check)
        
        layout.addWidget(state_group)
        
        # Path info
        path_group = PropertyGroup("Hierarchy")
        self._property_groups['hierarchy'] = path_group
        
        self.node_path_label = QLineEdit()
        self.node_path_label.setReadOnly(True)
        self.node_path_label.setStyleSheet("background-color: #f0f0f0;")
        path_group.add_property('path', self.node_path_label, "Path:")
        
        layout.addWidget(path_group)
        layout.addStretch()
        
        return tab
    
    def _create_transform_tab(self) -> QWidget:
        """Create the Transform tab for Node2D nodes."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # Position Group
        pos_group = PropertyGroup("Position")
        self._property_groups['position'] = pos_group
        
        self.pos_x_input = QDoubleSpinBox()
        self.pos_x_input.setRange(-999999, 999999)
        self.pos_x_input.setDecimals(2)
        self.pos_x_input.valueChanged.connect(lambda v: self._on_property_changed('position_x', v))
        pos_group.add_property('x', self.pos_x_input, "X:")
        
        self.pos_y_input = QDoubleSpinBox()
        self.pos_y_input.setRange(-999999, 999999)
        self.pos_y_input.setDecimals(2)
        self.pos_y_input.valueChanged.connect(lambda v: self._on_property_changed('position_y', v))
        pos_group.add_property('y', self.pos_y_input, "Y:")
        
        layout.addWidget(pos_group)
        
        # Rotation Group
        rot_group = PropertyGroup("Rotation & Scale")
        self._property_groups['rotation'] = rot_group
        
        self.rotation_input = QDoubleSpinBox()
        self.rotation_input.setRange(-360, 360)
        self.rotation_input.setDecimals(2)
        self.rotation_input.setSuffix("°")
        self.rotation_input.valueChanged.connect(lambda v: self._on_property_changed('rotation', v))
        rot_group.add_property('rotation', self.rotation_input, "Rotation:")
        
        self.scale_x_input = QDoubleSpinBox()
        self.scale_x_input.setRange(0.001, 999)
        self.scale_x_input.setDecimals(3)
        self.scale_x_input.setValue(1.0)
        self.scale_x_input.valueChanged.connect(lambda v: self._on_property_changed('scale_x', v))
        rot_group.add_property('scale_x', self.scale_x_input, "Scale X:")
        
        self.scale_y_input = QDoubleSpinBox()
        self.scale_y_input.setRange(0.001, 999)
        self.scale_y_input.setDecimals(3)
        self.scale_y_input.setValue(1.0)
        self.scale_y_input.valueChanged.connect(lambda v: self._on_property_changed('scale_y', v))
        rot_group.add_property('scale_y', self.scale_y_input, "Scale Y:")
        
        layout.addWidget(rot_group)
        
        # Rendering Group
        render_group = PropertyGroup("Rendering")
        self._property_groups['rendering'] = render_group
        
        self.z_index_input = QSpinBox()
        self.z_index_input.setRange(-9999, 9999)
        self.z_index_input.valueChanged.connect(lambda v: self._on_property_changed('z_index', v))
        render_group.add_property('z_index', self.z_index_input, "Z-Index:")
        
        layout.addWidget(render_group)
        layout.addStretch()
        
        return tab
    
    def _create_specific_tab(self) -> QWidget:
        """Create node-type specific properties tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.specific_content = QVBoxLayout()
        layout.addLayout(self.specific_content)
        layout.addStretch()
        
        return tab
    
    def _create_signals_tab(self) -> QWidget:
        """Create the Signals tab for viewing and connecting signals."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # Available Signals
        avail_group = QGroupBox("Available Signals")
        avail_layout = QVBoxLayout(avail_group)
        
        self.signals_list = QListWidget()
        self.signals_list.setStyleSheet("""
            QListWidget {
                background-color: #f5f5f5;
                border: 1px solid #cccccc;
                border-radius: 4px;
            }
        """)
        avail_layout.addWidget(self.signals_list)
        
        layout.addWidget(avail_group)
        
        # Connected Signals
        conn_group = QGroupBox("Connections")
        conn_layout = QVBoxLayout(conn_group)
        
        self.connections_list = QListWidget()
        conn_layout.addWidget(self.connections_list)
        
        # Connect button
        btn_layout = QHBoxLayout()
        self.connect_btn = QPushButton("Connect Signal...")
        self.connect_btn.clicked.connect(self._on_connect_signal)
        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.clicked.connect(self._on_disconnect_signal)
        btn_layout.addWidget(self.connect_btn)
        btn_layout.addWidget(self.disconnect_btn)
        conn_layout.addLayout(btn_layout)
        
        layout.addWidget(conn_group)
        layout.addStretch()
        
        return tab
    
    def _create_script_tab(self) -> QWidget:
        """Create the Script tab with drag & drop support."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # Drag & Drop Area
        drop_group = QGroupBox("Attach Script (Drag & Drop)")
        drop_layout = QVBoxLayout(drop_group)
        
        self.script_drop = ScriptDropArea()
        self.script_drop.script_dropped.connect(self._on_script_dropped)
        drop_layout.addWidget(self.script_drop)
        
        layout.addWidget(drop_group)
        
        # Current Script Info
        info_group = QGroupBox("Current Script")
        info_layout = QFormLayout(info_group)
        
        self.script_lang_label = QLabel("-")
        self.script_path_label = QLabel("-")
        self.script_path_label.setWordWrap(True)
        self.script_path_label.setStyleSheet("font-family: monospace; font-size: 11px;")
        
        info_layout.addRow("Language:", self.script_lang_label)
        info_layout.addRow("Path:", self.script_path_label)
        
        # Browse button
        browse_btn = QPushButton("Browse for Script...")
        browse_btn.clicked.connect(self._browse_script)
        info_layout.addRow(browse_btn)
        
        layout.addWidget(info_group)
        
        # Script Preview
        preview_group = QGroupBox("Script Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.script_preview = QPlainTextEdit()
        self.script_preview.setReadOnly(True)
        self.script_preview.setMaximumHeight(150)
        self.script_preview.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                border: 1px solid #3d3d3d;
            }
        """)
        preview_layout.addWidget(self.script_preview)
        
        layout.addWidget(preview_group)
        layout.addStretch()
        
        return tab
    
    def set_node(self, node: Node) -> None:
        """Set the node to inspect and populate all fields."""
        self.current_node = node
        
        # Update basic properties
        self.node_name_input.setText(node.name)
        self.node_type_label.setText(node.node_type.value)
        self.node_uid_label.setText(node.uid)
        self.node_path_label.setText(node.get_path())
        
        self.enabled_check.setChecked(node.enabled)
        self.visible_check.setChecked(node.visible)
        
        # Update transform if Node2D
        is_node2d = isinstance(node, Node2D)
        self.tabs.setTabEnabled(1, is_node2d)  # Transform tab
        
        if is_node2d:
            pos_x, pos_y = node.get_position()
            self.pos_x_input.setValue(pos_x)
            self.pos_y_input.setValue(pos_y)
            self.rotation_input.setValue(node.get_rotation())
            
            scale_x, scale_y = node.get_scale()
            self.scale_x_input.setValue(scale_x)
            self.scale_y_input.setValue(scale_y)
            
            self.z_index_input.setValue(node.z_index)
        
        # Update node-specific properties
        self._update_specific_properties(node)
        
        # Update signals
        self._update_signals(node)
        
        # Update script info
        self._update_script_info(node)
    
    def _update_specific_properties(self, node: Node) -> None:
        """Update node-type specific properties."""
        # Clear existing
        while self.specific_content.count():
            item = self.specific_content.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if isinstance(node, Sprite2D):
            self._add_sprite_properties(node)
        
        self.specific_content.addStretch()
    
    def _add_sprite_properties(self, sprite: Sprite2D) -> None:
        """Add Sprite2D specific properties."""
        # Texture Group
        tex_group = PropertyGroup("Texture")
        
        tex_path = sprite.texture.path if sprite.texture else ""
        self.texture_path = QLineEdit(tex_path)
        self.texture_path.setReadOnly(True)
        tex_group.add_property('texture', self.texture_path, "Texture:")
        
        # Texture select button
        tex_btn = QPushButton("Browse...")
        tex_btn.clicked.connect(lambda: self._browse_texture(sprite))
        tex_group.layout.addRow(tex_btn)
        
        self.specific_content.addWidget(tex_group)
        
        # Flip & Center Group
        flip_group = PropertyGroup("Flip & Center")
        
        self.flip_h_check = QCheckBox("Flip Horizontal")
        self.flip_h_check.setChecked(sprite.flip_h)
        self.flip_h_check.stateChanged.connect(lambda v: setattr(sprite, 'flip_h', bool(v)))
        flip_group.layout.addRow(self.flip_h_check)
        
        self.flip_v_check = QCheckBox("Flip Vertical")
        self.flip_v_check.setChecked(sprite.flip_v)
        self.flip_v_check.stateChanged.connect(lambda v: setattr(sprite, 'flip_v', bool(v)))
        flip_group.layout.addRow(self.flip_v_check)
        
        self.centered_check = QCheckBox("Centered")
        self.centered_check.setChecked(sprite.centered)
        self.centered_check.stateChanged.connect(lambda v: setattr(sprite, 'centered', bool(v)))
        flip_group.layout.addRow(self.centered_check)
        
        self.specific_content.addWidget(flip_group)
        
        # Animation Group
        anim_group = PropertyGroup("Animation Frames")
        
        self.hframes_input = QSpinBox()
        self.hframes_input.setRange(1, 100)
        self.hframes_input.setValue(sprite.hframes)
        self.hframes_input.valueChanged.connect(lambda v: setattr(sprite, 'hframes', v))
        anim_group.add_property('hframes', self.hframes_input, "H-Frames:")
        
        self.vframes_input = QSpinBox()
        self.vframes_input.setRange(1, 100)
        self.vframes_input.setValue(sprite.vframes)
        self.vframes_input.valueChanged.connect(lambda v: setattr(sprite, 'vframes', v))
        anim_group.add_property('vframes', self.vframes_input, "V-Frames:")
        
        self.frame_input = QSpinBox()
        self.frame_input.setRange(0, (sprite.hframes * sprite.vframes) - 1)
        self.frame_input.setValue(sprite.frame)
        self.frame_input.valueChanged.connect(lambda v: setattr(sprite, 'frame', v))
        anim_group.add_property('frame', self.frame_input, "Frame:")
        
        self.specific_content.addWidget(anim_group)
    
    def _browse_texture(self, sprite: Sprite2D) -> None:
        """Browse for texture file."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Texture", "", 
            "Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp)"
        )
        if path:
            from .types import Texture2D
            sprite.texture = Texture2D(path)
            sprite.texture.load()
            self.texture_path.setText(path)
    
    def _update_signals(self, node: Node) -> None:
        """Update signals list."""
        self.signals_list.clear()
        
        # Get signals from node class
        signals = getattr(node, '_SIGNALS', [])
        for signal_name in signals:
            item = QListWidgetItem(f"📡 {signal_name}")
            item.setData(Qt.ItemDataRole.UserRole, signal_name)
            self.signals_list.addItem(item)
        
        if not signals:
            self.signals_list.addItem("No signals available")
    
    def _update_script_info(self, node: Node) -> None:
        """Update script information."""
        lang = node.get_property('script_language', '-')
        source = node.get_property('script_source', '')
        
        self.script_lang_label.setText(lang)
        self.script_preview.setPlainText(source if source else "# No script attached")
        
        if node.script:
            self.script_drop.label.setText(f"Script: {os.path.basename(node.script)}")
            self.script_drop.label.setStyleSheet("color: #2196F3; font-weight: bold;")
            self.script_path_label.setText(node.script)
        else:
            self.script_drop.label.setText("Drag & Drop script file here\n(.py, .gdl, .gd)")
            self.script_drop.label.setStyleSheet("color: #888888; font-size: 12px;")
            self.script_path_label.setText("-")
    
    def _on_property_changed(self, property_name: str, value: Any) -> None:
        """Handle property value change."""
        if not self.current_node:
            return
        
        # Update node property
        if property_name == 'name':
            self.current_node.name = value
        elif property_name == 'enabled':
            self.current_node.enabled = value
        elif property_name == 'visible':
            self.current_node.visible = value
        elif property_name == 'position_x':
            y = self.current_node.get_position()[1] if isinstance(self.current_node, Node2D) else 0
            self.current_node.set_position(value, y)
        elif property_name == 'position_y':
            x = self.current_node.get_position()[0] if isinstance(self.current_node, Node2D) else 0
            self.current_node.set_position(x, value)
        elif property_name == 'rotation':
            self.current_node.set_rotation(value)
        elif property_name == 'scale_x':
            _, y = self.current_node.get_scale()
            self.current_node.set_scale(value, y)
        elif property_name == 'scale_y':
            x, _ = self.current_node.get_scale()
            self.current_node.set_scale(x, value)
        elif property_name == 'z_index':
            self.current_node.z_index = value
        
        # Emit signal
        self.property_changed.emit(self.current_node.uid, property_name, value)
    
    def _on_script_dropped(self, path: str) -> None:
        """Handle script file dropped."""
        if not self.current_node:
            return
        
        self.current_node.script = path
        
        # Detect language from extension
        ext = os.path.splitext(path)[1].lower()
        lang_map = {'.py': 'Python', '.gdl': 'GDLang', '.gd': 'GDScript', '.lua': 'Lua'}
        lang = lang_map.get(ext, 'Unknown')
        
        self.current_node.set_property('script_language', lang)
        
        # Try to load script content
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()[:1000]  # Limit preview
            self.current_node.set_property('script_source', content)
        except:
            self.current_node.set_property('script_source', f"# Could not read {path}")
        
        self._update_script_info(self.current_node)
        self.script_attached.emit(self.current_node.uid, path)
    
    def _browse_script(self) -> None:
        """Browse for script file."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Script", "",
            "Scripts (*.py *.gdl *.gd *.lua);;All Files (*)"
        )
        if path:
            self._on_script_dropped(path)
    
    def _on_connect_signal(self) -> None:
        """Show dialog to connect signal."""
        QMessageBox.information(self, "Connect Signal", 
            "Signal connection dialog would open here.\n"
            "Connect signals to methods in scripts or other nodes.")
    
    def _on_disconnect_signal(self) -> None:
        """Disconnect selected signal."""
        current = self.connections_list.currentItem()
        if current:
            self.connections_list.takeItem(self.connections_list.row(current))
