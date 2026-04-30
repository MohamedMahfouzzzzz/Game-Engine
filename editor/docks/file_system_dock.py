# /**************************************************************************/
# /*  file_system_dock.py                                                    */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""File system dock widget - Python port of Godot's FileSystemDock.

Provides project file browsing and management.
"""

from typing import Optional, List, Dict
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QContextMenuEvent, QDrag, QMouseEvent, QIcon, QColor, QFont
from PySide6.QtWidgets import (
    QDockWidget, QTreeWidget, QTreeWidgetItem, QInputDialog,
    QLineEdit, QMenu, QMessageBox, QVBoxLayout, QWidget, QLabel, QFrame
)

from engine.core.project_secure import SecureProject as Project
from ..theme import EditorColors, EditorFonts, EditorSpacing


class FileSystemWidget(QTreeWidget):
    """Custom tree widget for file system."""
    
    file_selected = Signal(str)  # Emitted with file path
    folder_selected = Signal(str)  # Emitted with folder path
    file_double_clicked = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabel("File System")
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.itemSelectionChanged.connect(self.on_selection_changed)
        self.itemDoubleClicked.connect(self.on_item_double_clicked)

        self.project: Optional[Project] = None
        self.current_path: Optional[Path] = None
        self.folder_items: Dict[str, QTreeWidgetItem] = {}

        # Enable drag and drop
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)

        # Apply design system styling
        self._apply_styling()
    
    def set_project(self, project: Project) -> None:
        """Set the current project."""
        self.project = project
        self.current_path = Path(project.path) if project else None
        self._refresh_tree()
    
    def _refresh_tree(self) -> None:
        """Refresh the file system tree."""
        self.clear()
        self.folder_items.clear()
        
        if not self.current_path or not self.current_path.exists():
            # Show empty state
            empty_item = QTreeWidgetItem(["No project loaded"])
            empty_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.addTopLevelItem(empty_item)
            return
        
        # Add project root
        self._add_folder_recursive(self.current_path, None)
        self.expandAll()
    
    def _add_folder_recursive(self, folder_path: Path, parent_item: Optional[QTreeWidgetItem]) -> None:
        """Add folder and all subfolders to tree."""
        item = QTreeWidgetItem()
        item.setText(0, folder_path.name)
        item.setData(0, Qt.ItemDataRole.UserRole, str(folder_path))
        item.setIcon(0, self._get_folder_icon())
        
        if parent_item is None:
            self.addTopLevelItem(item)
        else:
            parent_item.addChild(item)
        
        self.folder_items[str(folder_path)] = item
        
        # Add subfolders
        try:
            for item_path in folder_path.iterdir():
                if item_path.is_dir() and not item_path.name.startswith('.'):
                    self._add_folder_recursive(item_path, item)
        except PermissionError:
            pass
    
    def _get_folder_icon(self) -> Optional[QIcon]:
        """Get folder icon."""
        # TODO: Return actual folder icon
        return None
    
    def on_selection_changed(self) -> None:
        """Handle selection change."""
        selected_items = self.selectedItems()
        if selected_items:
            path = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
            if path:
                path_obj = Path(path)
                if path_obj.is_dir():
                    self.folder_selected.emit(path)
                else:
                    self.file_selected.emit(path)
    
    def on_item_double_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """Handle double click."""
        path = item.data(0, Qt.ItemDataRole.UserRole)
        if path:
            path_obj = Path(path)
            if path_obj.is_file():
                self.file_double_clicked.emit(path)
    
    def show_context_menu(self, position) -> None:
        """Show context menu for file system."""
        menu = QMenu(self)
        
        selected_items = self.selectedItems()
        if selected_items:
            path = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
            if path:
                path_obj = Path(path)
                
                if path_obj.is_dir():
                    # Folder actions
                    new_folder_action = QAction("New Folder", self)
                    new_folder_action.triggered.connect(lambda: self.create_folder(path))
                    menu.addAction(new_folder_action)
                    
                    new_file_action = QAction("New File", self)
                    new_file_action.triggered.connect(lambda: self.create_file(path))
                    menu.addAction(new_file_action)
                    
                    menu.addSeparator()
                    
                    rename_action = QAction("Rename", self)
                    rename_action.triggered.connect(lambda: self.rename_item(path))
                    menu.addAction(rename_action)
                    
                    delete_action = QAction("Delete", self)
                    delete_action.triggered.connect(lambda: self.delete_item(path))
                    menu.addAction(delete_action)
                else:
                    # File actions
                    open_action = QAction("Open", self)
                    open_action.triggered.connect(lambda: self.open_file(path))
                    menu.addAction(open_action)
                    
                    menu.addSeparator()
                    
                    rename_action = QAction("Rename", self)
                    rename_action.triggered.connect(lambda: self.rename_item(path))
                    menu.addAction(rename_action)
                    
                    delete_action = QAction("Delete", self)
                    delete_action.triggered.connect(lambda: self.delete_item(path))
                    menu.addAction(delete_action)
        
        menu.addSeparator()
        
        # Refresh action
        refresh_action = QAction("🔄 Refresh", self)
        refresh_action.triggered.connect(self._refresh_tree)
        menu.addAction(refresh_action)

        self._style_context_menu(menu)
        menu.exec_(self.mapToGlobal(position))
    
    def create_folder(self, parent_path: str) -> None:
        """Create new folder."""
        name, ok = QInputDialog.getText(self, "New Folder", "Folder name:")
        if ok and name:
            try:
                new_folder = Path(parent_path) / name
                new_folder.mkdir(exist_ok=True)
                self._refresh_tree()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create folder: {e}")
    
    def create_file(self, parent_path: str) -> None:
        """Create new file."""
        name, ok = QInputDialog.getText(self, "New File", "File name:")
        if ok and name:
            try:
                new_file = Path(parent_path) / name
                new_file.touch()
                self._refresh_tree()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create file: {e}")
    
    def rename_item(self, item_path: str) -> None:
        """Rename file or folder."""
        path_obj = Path(item_path)
        old_name = path_obj.name
        
        new_name, ok = QInputDialog.getText(self, "Rename", "New name:", QLineEdit.Normal, old_name)
        if ok and new_name and new_name != old_name:
            try:
                new_path = path_obj.parent / new_name
                path_obj.rename(new_path)
                self._refresh_tree()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to rename: {e}")
    
    def delete_item(self, item_path: str) -> None:
        """Delete file or folder."""
        path_obj = Path(item_path)
        
        # Confirm deletion
        item_type = "folder" if path_obj.is_dir() else "file"
        reply = QMessageBox.question(self, f"Delete {item_type}", 
                                   f"Delete {item_type} '{path_obj.name}'?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                if path_obj.is_dir():
                    path_obj.rmdir()  # Only removes empty directories
                else:
                    path_obj.unlink()
                self._refresh_tree()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete: {e}")
    
    def open_file(self, file_path: str) -> None:
        """Open file with appropriate editor."""
        # TODO: Implement file opening based on extension
        pass
    
    def get_selected_path(self) -> Optional[str]:
        """Get selected file or folder path."""
        selected_items = self.selectedItems()
        if selected_items:
            return selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        return None
    
    def get_current_folder(self) -> Optional[str]:
        """Get current folder path."""
        return str(self.current_path) if self.current_path else None


    def _apply_styling(self) -> None:
        """Apply design system styling to the tree widget."""
        self.setStyleSheet(f"""
            QTreeWidget {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_SECONDARY)};
                border: none;
                color: {EditorColors.to_stylesheet(EditorColors.TEXT_PRIMARY)};
                font-family: "{EditorFonts._get_ui_font_family()}";
                font-size: {EditorFonts.SIZE_MD}pt;
            }}
            QTreeWidget::item {{
                padding: 4px 8px;
                border-radius: 4px;
                min-height: {EditorSpacing.ROW_HEIGHT}px;
            }}
            QTreeWidget::item:selected {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_SELECTED)};
                color: white;
            }}
            QTreeWidget::item:hover {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_HOVER)};
            }}
            QHeaderView::section {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_TERTIARY)};
                color: {EditorColors.to_stylesheet(EditorColors.TEXT_PRIMARY)};
                padding: 8px;
                border: none;
                font-weight: 600;
            }}
        """)
        self.setFont(EditorFonts.body_text())

    def _style_context_menu(self, menu: QMenu) -> None:
        """Apply design system styling to context menu."""
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_SECONDARY)};
                border: 1px solid {EditorColors.to_stylesheet(EditorColors.BORDER_DEFAULT)};
                padding: 4px;
                border-radius: {EditorSpacing.RADIUS_MD}px;
            }}
            QMenu::item {{
                padding: 6px 24px;
                color: {EditorColors.to_stylesheet(EditorColors.TEXT_PRIMARY)};
                border-radius: {EditorSpacing.RADIUS_SM}px;
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


class FileSystemDock(QDockWidget):
    """File system dock widget with modern design system styling."""

    def __init__(self, parent=None):
        super().__init__("File System", parent)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        # Create widget
        widget = QWidget()
        self.setWidget(widget)

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # File system tree
        self.file_system = FileSystemWidget()
        layout.addWidget(self.file_system)

        # Connect signals
        self.file_system.file_selected.connect(self.on_file_selected)
        self.file_system.folder_selected.connect(self.on_folder_selected)
        self.file_system.file_double_clicked.connect(self.on_file_double_clicked)
    
    def set_project(self, project: Project) -> None:
        """Set the current project."""
        self.file_system.set_project(project)
    
    def on_file_selected(self, file_path: str) -> None:
        """Handle file selection."""
        # TODO: Update editor status or preview
        pass
    
    def on_folder_selected(self, folder_path: str) -> None:
        """Handle folder selection."""
        # TODO: Update editor status
        pass
    
    def on_file_double_clicked(self, file_path: str) -> None:
        """Handle file double click."""
        # TODO: Open file in appropriate editor
        pass
    
    def refresh(self) -> None:
        """Refresh the file system tree."""
        self.file_system._refresh_tree()
    
    def get_selected_path(self) -> Optional[str]:
        """Get selected file or folder path."""
        return self.file_system.get_selected_path()
