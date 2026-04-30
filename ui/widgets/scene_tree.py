# /**************************************************************************/
# /*  scene_tree.py                                                         */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

from typing import Dict, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QInputDialog, QLineEdit, QMenu, QMessageBox, QTreeWidget, QTreeWidgetItem
)

from engine.core.node import Node, Node2D, Scene
from engine.core.nodes import (
    Sprite, AnimatedSprite, Button, Control, Label,
)
from engine.scene2d import (
    Sprite2D, AnimatedSprite2D, TileMap, Camera2D,
    RigidBody2D, StaticBody2D, CharacterBody2D, CollisionShape2D,
    Light2D, CPUParticles2D, Path2D, PathFollow2D,
    Skeleton2D, Bone2D, NavigationAgent2D, NavigationRegion2D,
    AudioStreamPlayer2D, Marker2D, RayCast2D,
    ParallaxBackground, Parallax2D,
    RemoteTransform2D, VisibleOnScreenNotifier2D,
)
from engine.core.node_registry import (
    get_node_types_registry, NodeCategory
)


class SceneTreeWidget(QTreeWidget):
    node_selected = Signal(Node)
    node_added = Signal(Node)  # Emitted when new node is added
    node_deleted = Signal(str)  # Emitted with node uid when deleted

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabel("Scene Tree")
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.itemSelectionChanged.connect(self.on_selection_changed)
        self.scene: Optional[Scene] = None
        self.node_items: Dict[str, QTreeWidgetItem] = {}
        self._doc_registry = get_node_types_registry()

    def set_scene(self, scene: Scene) -> None:
        self.clear()
        self.node_items.clear()
        self.scene = scene
        self._add_node_recursive(scene.root, None)
        self.expandAll()

    def _add_node_recursive(self, node: Node, parent_item: Optional[QTreeWidgetItem]) -> None:
        item = QTreeWidgetItem()
        item.setText(0, f"{node.name} ({node.node_type.value})")
        item.setData(0, Qt.ItemDataRole.UserRole, node.uid)
        if parent_item is None:
            self.addTopLevelItem(item)
        else:
            parent_item.addChild(item)
        self.node_items[node.uid] = item
        for child in node.children:
            self._add_node_recursive(child, item)

    def on_selection_changed(self) -> None:
        items = self.selectedItems()
        if items and self.scene:
            node_id = items[0].data(0, Qt.ItemDataRole.UserRole)
            node = self.scene.get_node(node_id)
            if node:
                self.node_selected.emit(node)

    def show_context_menu(self, position) -> None:
        """Show context menu with node operations."""
        menu = QMenu()
        
        # Get selected node
        selected_node = self._get_selected_node()
        
        # Add Node submenu with categories
        add_menu = menu.addMenu("➕ Add Node")
        self._populate_add_node_menu(add_menu)
        
        # Other actions (only available if node selected)
        if selected_node:
            menu.addSeparator()
            delete_action = menu.addAction("🗑️ Delete Node")
            delete_action.triggered.connect(self._delete_selected_node)
            
            rename_action = menu.addAction("✏️ Rename Node")
            rename_action.triggered.connect(self._rename_selected_node)
            
            duplicate_action = menu.addAction("📋 Duplicate Node")
            duplicate_action.triggered.connect(self._duplicate_selected_node)
            
            menu.addSeparator()
            doc_action = menu.addAction("📖 Show Documentation")
            doc_action.triggered.connect(self._show_node_documentation)
        
        menu.exec(self.mapToGlobal(position))
    
    def _populate_add_node_menu(self, menu: QMenu) -> None:
        """Populate Add Node menu with all available node types."""
        categories = self._doc_registry.get_categories()
        
        for category in categories:
            nodes = self._doc_registry.get_nodes_by_category(category)
            if not nodes:
                continue
                
            category_menu = menu.addMenu(f"{nodes[0].icon} {category.value}")
            
            for node_doc in nodes:
                action = category_menu.addAction(f"{node_doc.icon} {node_doc.type_name}")
                action.setToolTip(node_doc.brief)
                action.triggered.connect(
                    lambda checked, n=node_doc: self._add_node_of_type(n.type_name)
                )
    
    def _add_node_of_type(self, node_type: str) -> None:
        """Add a new node of the specified type."""
        if not self.scene:
            QMessageBox.warning(self, "Add Node", "No active scene!")
            return
        
        # Get parent node (selected or root)
        parent_node = self._get_selected_node()
        if not parent_node:
            parent_node = self.scene.root
        
        # Create node based on type
        new_node = self._create_node_by_type(node_type)
        if new_node:
            # Add to parent
            self.scene.add_node(new_node, parent=parent_node)
            
            # Refresh tree
            self.set_scene(self.scene)
            
            # Select the new node
            if new_node.uid in self.node_items:
                self.setCurrentItem(self.node_items[new_node.uid])
            
            # Emit signal
            self.node_added.emit(new_node)
            
            QMessageBox.information(
                self, 
                "Node Added", 
                f"Added {node_type} '{new_node.name}' to '{parent_node.name}'"
            )
    
    def _create_node_by_type(self, node_type: str) -> Optional[Node]:
        """Create a node instance by type name."""
        # Map type names to classes
        type_map = {
            "Node": Node,
            "Node2D": Node2D,
            "Sprite": Sprite,
            "Sprite2D": Sprite2D,
            "AnimatedSprite": AnimatedSprite,
            "AnimatedSprite2D": AnimatedSprite2D,
            "TileMap": TileMap,
            "Camera2D": Camera2D,
            "RigidBody2D": RigidBody2D,
            "StaticBody2D": StaticBody2D,
            "CharacterBody2D": CharacterBody2D,
            "CollisionShape2D": CollisionShape2D,
            "Light2D": Light2D,
            "CPUParticles2D": CPUParticles2D,
            "Path2D": Path2D,
            "PathFollow2D": PathFollow2D,
            "Skeleton2D": Skeleton2D,
            "Bone2D": Bone2D,
            "NavigationAgent2D": NavigationAgent2D,
            "NavigationRegion2D": NavigationRegion2D,
            "AudioStreamPlayer2D": AudioStreamPlayer2D,
            "Marker2D": Marker2D,
            "RayCast2D": RayCast2D,
            "ParallaxBackground": ParallaxBackground,
            "Parallax2D": Parallax2D,
            "RemoteTransform2D": RemoteTransform2D,
            "VisibleOnScreenNotifier2D": VisibleOnScreenNotifier2D,
            "Control": Control,
            "Label": Label,
            "Button": Button,
        }
        
        node_class = type_map.get(node_type)
        if not node_class:
            QMessageBox.warning(self, "Add Node", f"Unknown node type: {node_type}")
            return None
        
        # Create with default name
        try:
            new_node = node_class(name=f"{node_type}")
        except TypeError:
            new_node = node_class(f"{node_type}")
        return new_node
    
    def _get_selected_node(self) -> Optional[Node]:
        """Get the currently selected node."""
        items = self.selectedItems()
        if items and self.scene:
            node_id = items[0].data(0, Qt.ItemDataRole.UserRole)
            return self.scene.get_node(node_id)
        return None
    
    def _delete_selected_node(self) -> None:
        """Delete the selected node."""
        node = self._get_selected_node()
        if not node:
            return
        
        # Can't delete root
        if node == self.scene.root:
            QMessageBox.warning(self, "Delete Node", "Cannot delete root node!")
            return
        
        # Confirm
        reply = QMessageBox.question(
            self, 
            "Delete Node",
            f"Delete '{node.name}' and all its children?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Remove from parent
            if node.parent:
                node.parent.remove_child(node)
            
            # Emit signal
            self.node_deleted.emit(node.uid)
            
            # Refresh
            self.set_scene(self.scene)
    
    def _rename_selected_node(self) -> None:
        """Rename the selected node."""
        node = self._get_selected_node()
        if not node:
            return
        
        new_name, ok = QInputDialog.getText(
            self, "Rename Node", "New name:",
            QLineEdit.EchoMode.Normal, node.name
        )
        
        if ok and new_name:
            old_name = node.name
            node.name = new_name
            if node.parent and hasattr(node.parent, "_child_by_name"):
                bucket = node.parent._child_by_name.get(old_name, [])
                if node in bucket:
                    bucket.remove(node)
                if not bucket:
                    node.parent._child_by_name.pop(old_name, None)
                node.parent._child_by_name.setdefault(new_name, []).append(node)
            self.set_scene(self.scene)  # Refresh
    
    def _duplicate_selected_node(self) -> None:
        """Duplicate the selected node."""
        node = self._get_selected_node()
        if not node:
            return
        
        # Serialize and deserialize
        data = node.to_dict()
        data["name"] = f"{node.name}_copy"
        
        # Create copy
        from engine.core.node_base import Node
        new_node = Node.from_dict(data)
        
        # Add to same parent
        if node.parent:
            self.scene.add_node(new_node, parent=node.parent)
            self.set_scene(self.scene)
            self.node_added.emit(new_node)
    
    def _show_node_documentation(self) -> None:
        """Show documentation for selected node type."""
        node = self._get_selected_node()
        if not node:
            return
        
        # Get documentation
        node_type = type(node).__name__
        doc = self._doc_registry.get_node_doc(node_type)
        
        if doc:
            from ui.dialogs.node_documentation_dialog import NodeDocumentationDialog
            dialog = NodeDocumentationDialog(doc, self)
            dialog.exec()
        else:
            QMessageBox.information(
                self, 
                "Documentation",
                f"No documentation available for {node_type}"
            )
