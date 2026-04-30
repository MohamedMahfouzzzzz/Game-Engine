"""Visual Dialogue Editor with node-based graph."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGraphicsView, 
    QGraphicsScene, QGraphicsItem, QGraphicsRectItem, 
    QGraphicsTextItem, QGraphicsEllipseItem, QGraphicsPathItem,
    QLineEdit, QPushButton, QComboBox, QTextEdit, QLabel, QSplitter,
    QGraphicsProxyWidget, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QRectF, Signal, QPointF
from PySide6.QtGui import QPen, QBrush, QColor, QFont, QPainterPath, QPainter
import json

class DialogueNodeItem(QGraphicsRectItem):
    """Visual node for dialogue graph."""
    
    NODE_COLORS = {
        "dialogue": QColor(100, 149, 237),      # Cornflower blue
        "choice": QColor(255, 165, 0),          # Orange
        "condition": QColor(147, 112, 219),     # Medium purple
        "action": QColor(60, 179, 113),         # Medium sea green
        "end": QColor(220, 20, 60),             # Crimson
    }
    
    def __init__(self, node_type: str, title: str, x: float, y: float):
        super().__init__(x, y, 200, 100)
        self.node_type = node_type
        self.title = title
        self.setBrush(QBrush(self.NODE_COLORS.get(node_type, QColor(128, 128, 128))))
        self.setPen(QPen(Qt.GlobalColor.black, 2))
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable | 
                     QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        
        # Title text
        self.title_item = QGraphicsTextItem(title, self)
        self.title_item.setPos(x + 5, y + 5)
        font = QFont()
        font.setBold(True)
        self.title_item.setFont(font)
        
        self.connections = []
    
    def add_connection(self, target):
        """Add connection to another node."""
        if target not in self.connections:
            self.connections.append(target)

class ConnectionItem(QGraphicsPathItem):
    """Visual connection between nodes."""
    
    def __init__(self, start_node: DialogueNodeItem, end_node: DialogueNodeItem):
        super().__init__()
        self.start_node = start_node
        self.end_node = end_node
        self.setPen(QPen(Qt.GlobalColor.darkGray, 2))
        self.update_path()
    
    def update_path(self):
        """Update the connection path."""
        start_rect = self.start_node.rect()
        end_rect = self.end_node.rect()
        
        start_x = start_rect.x() + start_rect.width()
        start_y = start_rect.y() + start_rect.height() / 2
        
        end_x = end_rect.x()
        end_y = end_rect.y() + end_rect.height() / 2
        
        path = QPainterPath()
        path.moveTo(start_x, start_y)
        
        # Bezier curve
        ctrl_x1 = start_x + 50
        ctrl_x2 = end_x - 50
        path.cubicTo(ctrl_x1, start_y, ctrl_x2, end_y, end_x, end_y)
        
        self.setPath(path)

class DialogueGraphScene(QGraphicsScene):
    """Scene for dialogue graph editor."""
    
    node_selected = Signal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.nodes = []
        self.connections = []
        self.selected_node = None
    
    def add_node(self, node_type: str, title: str, x: float = 0, y: float = 0) -> DialogueNodeItem:
        """Add a new node to the scene."""
        node = DialogueNodeItem(node_type, title, x, y)
        self.addItem(node)
        self.nodes.append(node)
        return node
    
    def connect_nodes(self, start: DialogueNodeItem, end: DialogueNodeItem):
        """Connect two nodes."""
        connection = ConnectionItem(start, end)
        self.addItem(connection)
        self.connections.append(connection)
        start.add_connection(end)
    
    def mousePressEvent(self, event):
        """Handle mouse press."""
        item = self.itemAt(event.scenePos(), self.views()[0].transform())
        if isinstance(item, DialogueNodeItem):
            self.selected_node = item
            self.node_selected.emit(item)
        super().mousePressEvent(event)

class DialogueEditor(QWidget):
    """Visual dialogue editor widget."""
    
    dialogue_saved = Signal(str)  # Emits file path
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_file = None
        self._build_ui()
    
    def _build_ui(self):
        """Build the UI."""
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        new_btn = QPushButton("New")
        new_btn.clicked.connect(self.new_dialogue)
        toolbar.addWidget(new_btn)
        
        open_btn = QPushButton("Open")
        open_btn.clicked.connect(self.open_dialogue)
        toolbar.addWidget(open_btn)
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_dialogue)
        toolbar.addWidget(save_btn)
        
        toolbar.addStretch()
        
        # Node creation buttons
        toolbar.addWidget(QLabel("Add:"))
        
        dialogue_btn = QPushButton("Dialogue")
        dialogue_btn.clicked.connect(lambda: self.add_node("dialogue"))
        toolbar.addWidget(dialogue_btn)
        
        choice_btn = QPushButton("Choice")
        choice_btn.clicked.connect(lambda: self.add_node("choice"))
        toolbar.addWidget(choice_btn)
        
        condition_btn = QPushButton("Condition")
        condition_btn.clicked.connect(lambda: self.add_node("condition"))
        toolbar.addWidget(condition_btn)
        
        action_btn = QPushButton("Action")
        action_btn.clicked.connect(lambda: self.add_node("action"))
        toolbar.addWidget(action_btn)
        
        layout.addLayout(toolbar)
        
        # Splitter for graph and properties
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Graph view
        self.scene = DialogueGraphScene()
        self.scene.node_selected.connect(self._on_node_selected)
        
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHints(QPainter.RenderHint.Antialiasing)
        self.view.setSceneRect(-500, -500, 1000, 1000)
        splitter.addWidget(self.view)
        
        # Properties panel
        self.properties = QWidget()
        props_layout = QVBoxLayout(self.properties)
        
        props_layout.addWidget(QLabel("Node Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["dialogue", "choice", "condition", "action", "end"])
        self.type_combo.currentTextChanged.connect(self._update_node_type)
        props_layout.addWidget(self.type_combo)
        
        props_layout.addWidget(QLabel("Title:"))
        self.title_edit = QLineEdit()
        self.title_edit.textChanged.connect(self._update_node_title)
        props_layout.addWidget(self.title_edit)
        
        props_layout.addWidget(QLabel("Text/Script:"))
        self.text_edit = QTextEdit()
        props_layout.addWidget(self.text_edit)
        
        props_layout.addStretch()
        
        delete_btn = QPushButton("Delete Node")
        delete_btn.clicked.connect(self._delete_selected_node)
        props_layout.addWidget(delete_btn)
        
        splitter.addWidget(self.properties)
        splitter.setSizes([600, 200])
        
        layout.addWidget(splitter)
        
        # Status bar
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
    
    def add_node(self, node_type: str):
        """Add a new node to the graph."""
        title = f"New {node_type.capitalize()}"
        x = len(self.scene.nodes) * 50
        y = len(self.scene.nodes) * 30
        node = self.scene.add_node(node_type, title, x, y)
        self.scene.selected_node = node
        self._update_properties_panel()
        self.status_label.setText(f"Added {node_type} node")
    
    def _on_node_selected(self, node):
        """Handle node selection."""
        self._update_properties_panel()
    
    def _update_properties_panel(self):
        """Update properties panel from selected node."""
        node = self.scene.selected_node
        if node:
            self.type_combo.setCurrentText(node.node_type)
            self.title_edit.setText(node.title)
            self.properties.setEnabled(True)
        else:
            self.properties.setEnabled(False)
    
    def _update_node_type(self, new_type: str):
        """Update selected node type."""
        if self.scene.selected_node:
            self.scene.selected_node.node_type = new_type
            self.scene.selected_node.setBrush(
                QBrush(DialogueNodeItem.NODE_COLORS.get(new_type, QColor(128, 128, 128)))
            )
    
    def _update_node_title(self, new_title: str):
        """Update selected node title."""
        if self.scene.selected_node:
            self.scene.selected_node.title = new_title
            self.scene.selected_node.title_item.setPlainText(new_title)
    
    def _delete_selected_node(self):
        """Delete the selected node."""
        if self.scene.selected_node:
            self.scene.removeItem(self.scene.selected_node)
            self.scene.nodes.remove(self.scene.selected_node)
            self.scene.selected_node = None
            self._update_properties_panel()
    
    def new_dialogue(self):
        """Create new dialogue."""
        self.scene.clear()
        self.scene.nodes = []
        self.scene.connections = []
        self.current_file = None
        self.status_label.setText("New dialogue created")
    
    def open_dialogue(self):
        """Open dialogue file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Dialogue", "", "Dialogue Files (*.dlg *.json)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self._load_from_data(data)
                self.current_file = file_path
                self.status_label.setText(f"Opened: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open: {e}")
    
    def save_dialogue(self):
        """Save dialogue file."""
        if not self.current_file:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Dialogue", "", "Dialogue Files (*.dlg *.json)"
            )
            if not file_path:
                return
            self.current_file = file_path
        
        try:
            data = self._export_to_data()
            with open(self.current_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            self.status_label.setText(f"Saved: {self.current_file}")
            self.dialogue_saved.emit(self.current_file)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save: {e}")
    
    def _load_from_data(self, data: dict):
        """Load dialogue from JSON data."""
        self.new_dialogue()
        
        for node_data in data.get("nodes", []):
            node = self.scene.add_node(
                node_data.get("type", "dialogue"),
                node_data.get("title", "Untitled"),
                node_data.get("x", 0),
                node_data.get("y", 0)
            )
            # Additional data loading...
    
    def _export_to_data(self) -> dict:
        """Export dialogue to JSON data."""
        nodes = []
        for node in self.scene.nodes:
            nodes.append({
                "type": node.node_type,
                "title": node.title,
                "x": node.rect().x(),
                "y": node.rect().y(),
            })
        
        return {"nodes": nodes, "connections": []}
