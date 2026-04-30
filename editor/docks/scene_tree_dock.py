# /**************************************************************************/
# /*  scene_tree_dock.py                                                     */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Scene tree dock widget - Modern redesign with design system.

Features:
- Color-coded node type icons
- Search/filter functionality
- Modern context menu
- Visual hierarchy improvements
"""

from typing import Dict, Optional, List, Any
from pathlib import Path

from PySide6.QtCore import Qt, Signal, QMimeData, QSize
from PySide6.QtGui import QAction, QContextMenuEvent, QDrag, QMouseEvent, QColor, QFont
from PySide6.QtWidgets import (
    QDockWidget, QTreeWidget, QTreeWidgetItem, QInputDialog,
    QLineEdit, QMenu, QMessageBox, QVBoxLayout, QWidget,
    QHBoxLayout, QPushButton, QLabel, QFrame, QLineEdit as QSearchLine
)

from engine.core.node_base import Node, Node2D
from engine.core.scene import Scene
from engine.core.project_secure import SecureProject as Project
from engine.core.node_registry import get_node_types_registry, NodeCategory
from engine.scene2d import (
    Sprite2D, AnimatedSprite2D, TileMap, Camera2D,
    RigidBody2D, StaticBody2D, CharacterBody2D, CollisionShape2D,
    Light2D, CPUParticles2D, Path2D, PathFollow2D,
    Skeleton2D, Bone2D, NavigationAgent2D, NavigationRegion2D,
    AudioStreamPlayer2D, Marker2D, RayCast2D,
    ParallaxBackground, Parallax2D,
    RemoteTransform2D, VisibleOnScreenNotifier2D,
)

from ..theme import EditorColors, EditorFonts, EditorSpacing
from ..components import EditorInput, EditorIconButton


# Node type icons and colors
NODE_ICONS = {
    "Node": "🔵",
    "Node2D": "📍",
    "Sprite2D": "🖼️",
    "AnimatedSprite2D": "🎬",
    "TileMap": "🧱",
    "Camera2D": "📷",
    "RigidBody2D": "⚙️",
    "StaticBody2D": "🧱",
    "CharacterBody2D": "🏃",
    "CollisionShape2D": "⭕",
    "Light2D": "💡",
    "CPUParticles2D": "✨",
    "Path2D": "〰️",
    "PathFollow2D": "🎯",
    "Skeleton2D": "🦴",
    "Bone2D": "🦴",
    "NavigationAgent2D": "🧭",
    "NavigationRegion2D": "🗺️",
    "AudioStreamPlayer2D": "🔊",
    "Marker2D": "📍",
    "RayCast2D": "📡",
    "ParallaxBackground": "🌄",
    "Parallax2D": "🌄",
    "RemoteTransform2D": "🔗",
    "VisibleOnScreenNotifier2D": "👁️",
    "Control": "🎛️",
    "Button": "🔘",
    "Label": "🏷️",
}

NODE_COLORS = {
    "Node": EditorColors.NODE_GENERIC,
    "Node2D": EditorColors.NODE_GENERIC,
    "Sprite2D": EditorColors.NODE_SPRITE,
    "AnimatedSprite2D": EditorColors.NODE_ANIMATION,
    "TileMap": EditorColors.NODE_SPRITE,
    "Camera2D": EditorColors.NODE_CAMERA,
    "RigidBody2D": EditorColors.NODE_PHYSICS,
    "StaticBody2D": EditorColors.NODE_PHYSICS,
    "CharacterBody2D": EditorColors.NODE_PHYSICS,
    "CollisionShape2D": EditorColors.NODE_COLLISION,
    "Light2D": EditorColors.NODE_LIGHT,
    "CPUParticles2D": EditorColors.NODE_PARTICLES,
    "Path2D": EditorColors.NODE_PATH,
    "PathFollow2D": EditorColors.NODE_PATH,
    "Skeleton2D": EditorColors.NODE_GENERIC,
    "Bone2D": EditorColors.NODE_GENERIC,
    "NavigationAgent2D": EditorColors.NODE_NAVIGATION,
    "NavigationRegion2D": EditorColors.NODE_NAVIGATION,
    "AudioStreamPlayer2D": EditorColors.NODE_AUDIO,
    "Marker2D": EditorColors.NODE_GENERIC,
    "RayCast2D": EditorColors.NODE_GENERIC,
    "ParallaxBackground": EditorColors.NODE_SPRITE,
    "Parallax2D": EditorColors.NODE_SPRITE,
    "RemoteTransform2D": EditorColors.NODE_GENERIC,
    "VisibleOnScreenNotifier2D": EditorColors.NODE_GENERIC,
    "Control": EditorColors.NODE_UI,
    "Button": EditorColors.NODE_UI,
    "Label": EditorColors.NODE_UI,
}


class SceneTreeWidget(QTreeWidget):
    """Modern scene tree widget with color-coded nodes."""

    node_selected = Signal(Node)
    node_added = Signal(Node)
    node_deleted = Signal(str)
    node_renamed = Signal(str, str)  # uid, new_name

    def __init__(self, parent=None):
        super().__init__(parent)

        # Hide default header, use custom
        self.setHeaderHidden(True)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.itemSelectionChanged.connect(self.on_selection_changed)
        self.itemExpanded.connect(self._on_item_expanded)
        self.itemCollapsed.connect(self._on_item_collapsed)

        self.scene: Optional[Scene] = None
        self.project: Optional[Project] = None
        self.node_items: Dict[str, QTreeWidgetItem] = {}
        self._registry = get_node_types_registry()
        self._expanded_nodes: set = set()

        # Enable drag and drop
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)

        # Styling
        self._apply_style()

    def _apply_style(self) -> None:
        """Apply modern tree styling."""
        self.setStyleSheet(f"""
            QTreeWidget {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_SECONDARY)};
                border: none;
                outline: none;
                font-family: "{EditorFonts._get_ui_font_family()}";
                font-size: {EditorFonts.SIZE_MD}pt;
            }}
            QTreeWidget::item {{
                padding: {EditorSpacing.XS}px {EditorSpacing.SM}px;
                border-radius: {EditorSpacing.RADIUS_SM}px;
                min-height: {EditorSpacing.ROW_HEIGHT}px;
            }}
            QTreeWidget::item:selected {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_SELECTED)};
                color: white;
            }}
            QTreeWidget::item:hover {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_HOVER)};
            }}
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {{
                image: none;
                border-left: 6px solid {EditorColors.to_stylesheet(EditorColors.TEXT_SECONDARY)};
                border-top: 4px solid transparent;
                border-bottom: 4px solid transparent;
            }}
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings {{
                image: none;
                border-left: 6px solid {EditorColors.to_stylesheet(EditorColors.TEXT_PRIMARY)};
                border-top: 4px solid transparent;
                border-bottom: 4px solid transparent;
                transform: rotate(90deg);
            }}
        """)
        self.setFont(EditorFonts.node_tree_item())

    def set_scene(self, scene: Scene) -> None:
        """Set the current scene."""
        self.clear()
        self.node_items.clear()
        self.scene = scene
        if scene:
            self._add_node_recursive(scene.root, None)
            self.expandAll()
            # Restore expanded state
            for uid in self._expanded_nodes:
                item = self.node_items.get(uid)
                if item:
                    self.expandItem(item)

    def set_project(self, project: Project) -> None:
        """Set the current project."""
        self.project = project
        if project and project.scenes:
            # Load first scene
            scene = project.scenes[0]
            self.set_scene(scene)

    def _add_node_recursive(self, node: Node, parent_item: Optional[QTreeWidgetItem]) -> None:
        """Add node and all children to tree with color coding."""
        item = QTreeWidgetItem()

        # Get icon and color for node type
        node_type_name = node.__class__.__name__
        icon = NODE_ICONS.get(node_type_name, "🔵")
        color = NODE_COLORS.get(node_type_name, EditorColors.NODE_GENERIC)

        # Set display text with icon
        item.setText(0, f"{icon} {node.name}")
        item.setData(0, Qt.ItemDataRole.UserRole, node.uid)

        # Set text color based on node type
        item.setForeground(0, color)

        # Bold for root node
        if parent_item is None:
            font = item.font(0)
            font.setBold(True)
            item.setFont(0, font)

        if parent_item is None:
            self.addTopLevelItem(item)
        else:
            parent_item.addChild(item)

        self.node_items[node.uid] = item

        # Add children
        if hasattr(node, 'children'):
            for child in node.children:
                self._add_node_recursive(child, item)
    
    def _on_item_expanded(self, item: QTreeWidgetItem) -> None:
        """Track expanded items."""
        node_uid = item.data(0, Qt.ItemDataRole.UserRole)
        if node_uid:
            self._expanded_nodes.add(node_uid)

    def _on_item_collapsed(self, item: QTreeWidgetItem) -> None:
        """Track collapsed items."""
        node_uid = item.data(0, Qt.ItemDataRole.UserRole)
        if node_uid:
            self._expanded_nodes.discard(node_uid)

    def on_selection_changed(self) -> None:
        """Handle selection change."""
        selected_items = self.selectedItems()
        if selected_items and self.scene:
            node_uid = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
            node = self.scene.get_node_by_uid(node_uid)
            if node:
                self.node_selected.emit(node)

    def show_context_menu(self, position) -> None:
        """Show modern styled context menu."""
        menu = QMenu(self)

        # Style the menu
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_SECONDARY)};
                border: 1px solid {EditorColors.to_stylesheet(EditorColors.BORDER_DEFAULT)};
                padding: 4px;
            }}
            QMenu::item {{
                padding: 6px 24px;
                color: {EditorColors.to_stylesheet(EditorColors.TEXT_PRIMARY)};
            }}
            QMenu::item:selected {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_SELECTED)};
                color: white;
            }}
            QMenu::separator {{
                height: 1px;
                background-color: {EditorColors.to_stylesheet(EditorColors.BORDER_DEFAULT)};
                margin: 4px 8px;
            }}
        """)

        # Add node submenu
        add_menu = menu.addMenu("➕ Add Child Node")
        self._populate_add_node_menu(add_menu)

        menu.addSeparator()

        # Actions with icons
        rename_action = QAction("✏️ Rename", self)
        rename_action.setShortcut("F2")
        rename_action.triggered.connect(self.rename_selected_node)
        menu.addAction(rename_action)

        duplicate_action = QAction("📋 Duplicate", self)
        duplicate_action.setShortcut("Ctrl+D")
        duplicate_action.triggered.connect(self.duplicate_selected_node)
        menu.addAction(duplicate_action)

        menu.addSeparator()

        delete_action = QAction("🗑️ Delete", self)
        delete_action.setShortcut("Delete")
        delete_action.triggered.connect(self.delete_selected_node)
        menu.addAction(delete_action)

        menu.exec(self.mapToGlobal(position))
    
    def _populate_add_node_menu(self, menu: QMenu) -> None:
        """Populate add node menu with available node types."""
        categories = {}
        
        # Group nodes by category
        for node_type_name, node_doc in self._registry.get_all_nodes().items():
            category = node_doc.category
            if category not in categories:
                categories[category] = []
            categories[category].append((node_type_name, node_doc))
        
        # Add category submenus
        for category in sorted(categories.keys(), key=lambda c: c.value):
            category_menu = menu.addMenu(category.value)
            
            for node_type_name, node_doc in sorted(categories[category], key=lambda n: n[1].brief):
                action = QAction(f"{node_doc.icon} {node_doc.brief}", self)
                action.setData(node_type_name)
                action.triggered.connect(lambda checked, name=node_type_name: self.add_node(name))
                category_menu.addAction(action)
    
    def add_node(self, node_type_name: str) -> None:
        """Add new node of specified type."""
        if not self.scene:
            print(f"[SceneTree] Cannot add node - no scene loaded")
            return

        if not self.scene.root:
            print(f"[SceneTree] Cannot add node - scene has no root")
            return

        # Get selected parent node
        selected_items = self.selectedItems()
        parent_node = self.scene.root

        if selected_items:
            parent_uid = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
            found_parent = self.scene.get_node_by_uid(parent_uid)
            if found_parent:
                parent_node = found_parent

        # Create new node
        node = self._create_node_by_type(node_type_name)
        if node:
            node.name = f"{node_type_name}"
            parent_node.add_child(node)

            # Update tree
            parent_item = self.node_items.get(parent_node.uid)
            self._add_node_recursive(node, parent_item)

            # Select new node
            new_item = self.node_items.get(node.uid)
            if new_item:
                self.setCurrentItem(new_item)

            self.node_added.emit(node)
            print(f"[SceneTree] Added node: {node.name} ({node.uid})")
    
    def _create_node_by_type(self, node_type_name: str) -> Optional[Node]:
        """Create node instance by type name."""
        # Map type names to actual classes
        node_classes = {
            "Node": Node,
            "Node2D": Node2D,
            "Sprite2D": Sprite2D,
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
        }
        
        node_class = node_classes.get(node_type_name)
        if node_class:
            return node_class()

        return None

    def delete_selected_node(self) -> None:
        """Delete selected node with undo support."""
        selected_items = self.selectedItems()
        if not selected_items or not self.scene:
            return

        node_uid = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        node = self.scene.get_node_by_uid(node_uid)

        if node and node != self.scene.root:
            # Confirm deletion with styled message box
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Delete Node")
            msg_box.setText(f"Delete '{node.name}'?")
            msg_box.setInformativeText("This action cannot be undone.")
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.setDefaultButton(QMessageBox.No)
            msg_box.button(QMessageBox.Yes).setText("Delete")

            # Style the message box
            msg_box.setStyleSheet(f"""
                QMessageBox {{
                    background-color: {EditorColors.to_stylesheet(EditorColors.BG_PRIMARY)};
                }}
                QLabel {{
                    color: {EditorColors.to_stylesheet(EditorColors.TEXT_PRIMARY)};
                }}
                QPushButton {{
                    background-color: {EditorColors.to_stylesheet(EditorColors.BUTTON_SECONDARY_BG)};
                    color: {EditorColors.to_stylesheet(EditorColors.TEXT_PRIMARY)};
                    padding: 6px 16px;
                    border: 1px solid {EditorColors.to_stylesheet(EditorColors.BORDER_DEFAULT)};
                    border-radius: {EditorSpacing.RADIUS_SM}px;
                }}
                QPushButton:hover {{
                    background-color: {EditorColors.to_stylesheet(EditorColors.BUTTON_SECONDARY_HOVER)};
                }}
            """)

            reply = msg_box.exec()

            if reply == QMessageBox.Yes:
                parent = node.parent
                if parent:
                    parent.remove_child(node)

                    # Remove from tree
                    item = self.node_items.get(node.uid)
                    if item:
                        parent_item = item.parent()
                        if parent_item:
                            parent_item.removeChild(item)
                        else:
                            self.takeTopLevelItem(self.indexOfTopLevelItem(item))

                    del self.node_items[node_uid]
                    self._expanded_nodes.discard(node_uid)
                    self.node_deleted.emit(node_uid)

    def rename_selected_node(self) -> None:
        """Rename selected node inline."""
        selected_items = self.selectedItems()
        if not selected_items or not self.scene:
            return

        node_uid = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        node = self.scene.get_node_by_uid(node_uid)

        if node:
            old_name = node.name
            new_name, ok = QInputDialog.getText(self, "Rename Node",
                                              "New name:", QLineEdit.Normal, old_name)

            if ok and new_name and new_name != old_name:
                node.name = new_name
                node_type_name = node.__class__.__name__
                icon = NODE_ICONS.get(node_type_name, "🔵")
                selected_items[0].setText(0, f"{icon} {new_name}")
                self.node_renamed.emit(node_uid, new_name)
    
    def duplicate_selected_node(self) -> None:
        """Duplicate selected node."""
        selected_items = self.selectedItems()
        if not selected_items or not self.scene:
            return
        
        node_uid = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        node = self.scene.get_node_by_uid(node_uid)
        
        if node:
            # TODO: Implement node duplication
            pass


class SceneTreeDock(QDockWidget):
    """Modern scene tree dock with toolbar and search."""

    node_selected = Signal(Node)
    node_added = Signal(Node)
    node_deleted = Signal(str)

    def __init__(self, parent=None):
        super().__init__("Scene", parent)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        # Create main widget
        widget = QWidget()
        self.setWidget(widget)

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Search box (create first)
        self.search_box = EditorInput("Search nodes...")
        self.search_box.setPlaceholderText("🔍 Search nodes...")
        self.search_box.textChanged.connect(self._on_search_changed)

        # Scene tree (create before toolbar that references it)
        self.scene_tree = SceneTreeWidget()

        # Connect signals
        self.scene_tree.node_selected.connect(self._on_node_selected)
        self.scene_tree.node_added.connect(self._on_node_added)
        self.scene_tree.node_deleted.connect(self._on_node_deleted)
        self.scene_tree.node_renamed.connect(self._on_node_renamed)

        # Toolbar (after scene_tree is created)
        toolbar = self._create_toolbar()
        layout.addWidget(toolbar)

        layout.addWidget(self.search_box)
        layout.addWidget(self.scene_tree)

    def _create_toolbar(self) -> QFrame:
        """Create modern toolbar."""
        toolbar = QFrame()
        toolbar.setFixedHeight(EditorSpacing.TOOLBAR_HEIGHT_SMALL)
        toolbar.setStyleSheet(f"""
            QFrame {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_TERTIARY)};
                border-bottom: 1px solid {EditorColors.to_stylesheet(EditorColors.BORDER_DEFAULT)};
            }}
        """)

        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(EditorSpacing.SM, 0, EditorSpacing.SM, 0)
        layout.setSpacing(EditorSpacing.XS)

        # Add node button
        add_btn = QPushButton("➕")
        add_btn.setFlat(True)
        add_btn.setFixedSize(28, 28)
        add_btn.setToolTip("Add Node")
        add_btn.clicked.connect(self._show_add_node_menu)
        layout.addWidget(add_btn)

        # Delete button
        del_btn = QPushButton("🗑️")
        del_btn.setFlat(True)
        del_btn.setFixedSize(28, 28)
        del_btn.setToolTip("Delete Selected")
        del_btn.clicked.connect(self.scene_tree.delete_selected_node)
        layout.addWidget(del_btn)

        layout.addStretch()

        # Filter button
        filter_btn = QPushButton("⚙️")
        filter_btn.setFlat(True)
        filter_btn.setFixedSize(28, 28)
        filter_btn.setToolTip("View Options")
        layout.addWidget(filter_btn)

        return toolbar

    def _show_add_node_menu(self) -> None:
        """Show add node menu."""
        menu = QMenu(self)
        self.scene_tree._populate_add_node_menu(menu)
        menu.exec(self.mapToGlobal(self.pos()))

    def _on_search_changed(self, text: str) -> None:
        """Filter tree based on search text."""
        if not text:
            # Show all
            for i in range(self.scene_tree.topLevelItemCount()):
                self._set_item_visible_recursive(self.scene_tree.topLevelItem(i), True)
            return

        # Filter
        for i in range(self.scene_tree.topLevelItemCount()):
            self._filter_item_recursive(self.scene_tree.topLevelItem(i), text.lower())

    def _set_item_visible_recursive(self, item: QTreeWidgetItem, visible: bool) -> None:
        """Set item and children visibility."""
        item.setHidden(not visible)
        for i in range(item.childCount()):
            self._set_item_visible_recursive(item.child(i), visible)

    def _filter_item_recursive(self, item: QTreeWidgetItem, search_text: str) -> bool:
        """Filter item and children, return True if any visible."""
        item_text = item.text(0).lower()
        matches = search_text in item_text

        # Check children
        child_visible = False
        for i in range(item.childCount()):
            if self._filter_item_recursive(item.child(i), search_text):
                child_visible = True

        # Show if matches or has visible children
        visible = matches or child_visible
        item.setHidden(not visible)

        # Expand if has visible children
        if child_visible:
            item.setExpanded(True)

        return visible

    def set_scene(self, scene: Scene) -> None:
        """Set the current scene."""
        self.scene_tree.set_scene(scene)

    def set_project(self, project: Project) -> None:
        """Set the current project."""
        self.scene_tree.set_project(project)

    def _on_node_selected(self, node: Node) -> None:
        """Handle node selection."""
        self.node_selected.emit(node)

    def _on_node_added(self, node: Node) -> None:
        """Handle node addition."""
        self.node_added.emit(node)

    def _on_node_deleted(self, node_uid: str) -> None:
        """Handle node deletion."""
        self.node_deleted.emit(node_uid)

    def _on_node_renamed(self, node_uid: str, new_name: str) -> None:
        """Handle node rename."""
        # Update other UI components
        pass

    def refresh(self) -> None:
        """Refresh the tree."""
        if self.scene_tree.scene:
            self.scene_tree.set_scene(self.scene_tree.scene)
