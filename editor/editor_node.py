# /**************************************************************************/
# /*  editor_node.py                                                        */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Main editor window - Python port of Godot's EditorNode.

Provides the main editor interface with dock system, menu bar, and scene editing.
"""

from typing import Optional, Dict, Any
import sys
import os

from PySide6.QtCore import Qt, QTimer, Signal, QSize
from PySide6.QtGui import QKeySequence, QAction, QIcon
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QDockWidget, QTabWidget,
    QSplitter, QHBoxLayout, QVBoxLayout, QToolBar, QStatusBar,
    QMenuBar, QLabel, QMessageBox, QFrame, QDialog
)

from engine.core.node_base import Node
from engine.core.project_secure import SecureProject as Project
from engine import crash_handler
from engine.session_manager import SessionManager

from .editor_interface import EditorInterface, get_editor_interface
from .editor_data import EditorData
from .editor_log import EditorLog
from .docks import SceneTreeDock, InspectorDock, FileSystemDock
from .scene import SceneEditor
from .project_manager import ProjectManager
from .theme import EditorColors, EditorFonts, EditorSpacing
from .components import EditorPrimaryButton, EditorSecondaryButton


class EditorNode(QMainWindow):
    """Main editor window.
    
    Central hub for all editor functionality including:
    - Dock system for tools
    - Scene editing viewport
    - Menu bar and toolbars
    - Project management
    """
    
    def __init__(self):
        super().__init__()
        
        self.project: Optional[Project] = None
        self.editor_data = EditorData()
        self.editor_log = EditorLog()
        self.editor_interface = get_editor_interface()
        self.editor_interface.set_main_window(self)
        
        self._setup_window()
        self._setup_ui()
        self._setup_docks()
        self._setup_menu_bar()
        self._setup_status_bar()
        self._setup_timers()
        
        # Load last project if available
        self._load_last_project()
    
    def _setup_window(self) -> None:
        """Configure main window properties with golden ratio sizing."""
        self.setWindowTitle("Game Engine Editor")
        
        # Calculate optimal window size based on screen
        screen = QApplication.primaryScreen().geometry()
        
        # Golden ratio proportions
        PHI = 1.618
        
        # Default to 80% of screen with golden ratio
        if screen.width() >= 1920:
            width = 1680
            height = int(width / PHI)
        elif screen.width() >= 1440:
            width = 1440
            height = int(width / PHI)
        else:
            width = int(screen.width() * 0.9)
            height = int(width / PHI)
        
        # Center on screen
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        
        self.setGeometry(x, y, width, height)
        self.setMinimumSize(1200, 700)
        
        # Set window background with modern styling like welcome page
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_PRIMARY)};
            }}
            QWidget {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_PRIMARY)};
            }}
            QDockWidget {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_SECONDARY)};
                border: 1px solid {EditorColors.to_stylesheet(EditorColors.BORDER_DEFAULT)};
                border-radius: {EditorSpacing.RADIUS_MD}px;
            }}
            QDockWidget::title {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_TERTIARY)};
                padding: 8px 12px;
                border-top-left-radius: {EditorSpacing.RADIUS_MD}px;
                border-top-right-radius: {EditorSpacing.RADIUS_MD}px;
                color: {EditorColors.to_stylesheet(EditorColors.TEXT_PRIMARY)};
                font-weight: 600;
            }}
            QTabWidget::pane {{
                border: 1px solid {EditorColors.to_stylesheet(EditorColors.BORDER_DEFAULT)};
                border-radius: {EditorSpacing.RADIUS_SM}px;
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_SECONDARY)};
            }}
            QTabBar::tab {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_TERTIARY)};
                color: {EditorColors.to_stylesheet(EditorColors.TEXT_SECONDARY)};
                padding: 8px 16px;
                border-top-left-radius: {EditorSpacing.RADIUS_SM}px;
                border-top-right-radius: {EditorSpacing.RADIUS_SM}px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_SECONDARY)};
                color: {EditorColors.to_stylesheet(EditorColors.TEXT_PRIMARY)};
            }}
            QTabBar::tab:hover {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_HOVER)};
            }}
        """)
    
    def _setup_ui(self) -> None:
        """Setup central widget and layout."""
        # Central widget with scene editor
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Scene editor (placeholder for now)
        self.scene_editor = SceneEditor()
        layout.addWidget(self.scene_editor)
    
    def _setup_docks(self) -> None:
        """Create and setup all editor docks with golden ratio layout.
        
        Layout: 15% - 61.8% - 23.2% (Golden ratio divisions)
        """
        # Calculate widths based on golden ratio
        total_width = self.width()
        
        # Scene Tree Dock (Left) - ~15% of width
        self.scene_tree_dock = SceneTreeDock(self)
        self.scene_tree_dock.setObjectName("SceneTreeDock")
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.scene_tree_dock)
        
        # File System Dock (Left) - tabified with scene tree
        self.file_system_dock = FileSystemDock(self)
        self.file_system_dock.setObjectName("FileSystemDock")
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.file_system_dock)
        
        # Tabify left docks
        self.tabifyDockWidget(self.scene_tree_dock, self.file_system_dock)
        self.scene_tree_dock.raise_()
        
        # Inspector Dock (Right) - ~23% of width
        self.inspector_dock = InspectorDock(self)
        self.inspector_dock.setObjectName("InspectorDock")
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.inspector_dock)
        
        # Set dock sizes after a brief delay (to ensure geometry is calculated)
        QTimer.singleShot(100, self._set_dock_sizes)
        
        # Style docks
        self._style_docks()
    
    def _set_dock_sizes(self) -> None:
        """Set optimal dock sizes based on golden ratio."""
        total_width = self.width()
        
        # Golden ratio proportions
        left_width = int(total_width * 0.18)  # ~18% for left docks
        right_width = int(total_width * 0.22)  # ~22% for right docks
        
        # Resize docks
        self.scene_tree_dock.setMinimumWidth(EditorSpacing.SCENE_TREE_MIN_WIDTH)
        self.scene_tree_dock.setMaximumWidth(EditorSpacing.SCENE_TREE_MAX_WIDTH)
        self.scene_tree_dock.resize(left_width, self.scene_tree_dock.height())
        
        self.file_system_dock.setMinimumWidth(EditorSpacing.FILE_BROWSER_MIN_WIDTH)
        self.file_system_dock.setMaximumWidth(EditorSpacing.FILE_BROWSER_MAX_WIDTH)
        
        self.inspector_dock.setMinimumWidth(EditorSpacing.INSPECTOR_MIN_WIDTH)
        self.inspector_dock.setMaximumWidth(EditorSpacing.INSPECTOR_MAX_WIDTH)
        self.inspector_dock.resize(right_width, self.inspector_dock.height())
    
    def _style_docks(self) -> None:
        """Apply consistent styling to all docks."""
        dock_style = f"""
            QDockWidget {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_SECONDARY)};
                border: 1px solid {EditorColors.to_stylesheet(EditorColors.BORDER_DEFAULT)};
            }}
            QDockWidget::title {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_TERTIARY)};
                padding: {EditorSpacing.SM}px;
                font-weight: bold;
                color: {EditorColors.to_stylesheet(EditorColors.TEXT_PRIMARY)};
            }}
            QDockWidget::close-button, QDockWidget::float-button {{
                background: transparent;
                padding: 0px;
            }}
            QTabBar::tab {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_TERTIARY)};
                color: {EditorColors.to_stylesheet(EditorColors.TEXT_SECONDARY)};
                padding: {EditorSpacing.SM}px {EditorSpacing.MD}px;
                border: none;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_SECONDARY)};
                color: {EditorColors.to_stylesheet(EditorColors.TEXT_PRIMARY)};
                border-bottom: 2px solid {EditorColors.to_stylesheet(EditorColors.BORDER_FOCUS)};
            }}
            QTabBar::tab:hover {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_HOVER)};
                color: {EditorColors.to_stylesheet(EditorColors.TEXT_PRIMARY)};
            }}
        """
        
        for dock in [self.scene_tree_dock, self.file_system_dock, self.inspector_dock]:
            dock.setStyleSheet(dock_style)
    
    def _setup_menu_bar(self) -> None:
        """Create styled main menu bar."""
        menubar = self.menuBar()
        
        # Style menu bar
        menubar.setStyleSheet(f"""
            QMenuBar {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_SECONDARY)};
                border-bottom: 1px solid {EditorColors.to_stylesheet(EditorColors.BORDER_DEFAULT)};
                padding: 2px;
            }}
            QMenuBar::item {{
                background: transparent;
                padding: 4px 12px;
                border-radius: {EditorSpacing.RADIUS_SM}px;
                color: {EditorColors.to_stylesheet(EditorColors.TEXT_PRIMARY)};
            }}
            QMenuBar::item:selected {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_HOVER)};
            }}
            QMenuBar::item:pressed {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_SELECTED)};
            }}
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
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_project_action = QAction("New Project...", self)
        new_project_action.setShortcut(QKeySequence.New)
        new_project_action.triggered.connect(self._new_project)
        file_menu.addAction(new_project_action)
        
        open_project_action = QAction("Open Project...", self)
        open_project_action.setShortcut(QKeySequence.Open)
        open_project_action.triggered.connect(self._open_project)
        file_menu.addAction(open_project_action)
        
        file_menu.addSeparator()
        
        save_scene_action = QAction("Save Scene", self)
        save_scene_action.setShortcut(QKeySequence.Save)
        save_scene_action.triggered.connect(self._save_scene)
        file_menu.addAction(save_scene_action)
        
        file_menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.setShortcut(QKeySequence.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        undo_action = QAction("Undo", self)
        undo_action.setShortcut(QKeySequence.Undo)
        undo_action.triggered.connect(self._undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("Redo", self)
        redo_action.setShortcut(QKeySequence.Redo)
        redo_action.triggered.connect(self._redo)
        edit_menu.addAction(redo_action)
        
        # Scene menu
        scene_menu = menubar.addMenu("&Scene")
        
        new_scene_action = QAction("New Scene", self)
        new_scene_action.triggered.connect(self._new_scene)
        scene_menu.addAction(new_scene_action)
        
        # Project menu
        project_menu = menubar.addMenu("&Project")
        
        project_settings_action = QAction("Project Settings...", self)
        project_settings_action.triggered.connect(self._project_settings)
        project_menu.addAction(project_settings_action)
        
        # Play menu
        play_menu = menubar.addMenu("&Play")
        
        play_scene_action = QAction("Play Scene", self)
        play_scene_action.setShortcut("F5")
        play_scene_action.triggered.connect(self._play_scene)
        play_menu.addAction(play_scene_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")

        pixel_editor_action = QAction("🎨 Pixel Art Editor", self)
        pixel_editor_action.setShortcut("Ctrl+Shift+P")
        pixel_editor_action.triggered.connect(self._open_pixel_editor)
        tools_menu.addAction(pixel_editor_action)

        tools_menu.addSeparator()

        animation_editor_action = QAction("🎬 Animation Editor", self)
        animation_editor_action.setEnabled(False)  # TODO: Implement
        tools_menu.addAction(animation_editor_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self._about)
        help_menu.addAction(about_action)
    
    def _setup_status_bar(self) -> None:
        """Create styled status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Style status bar
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_SECONDARY)};
                border-top: 1px solid {EditorColors.to_stylesheet(EditorColors.BORDER_DEFAULT)};
                color: {EditorColors.to_stylesheet(EditorColors.TEXT_SECONDARY)};
                padding: 2px 8px;
            }}
            QLabel {{
                color: {EditorColors.to_stylesheet(EditorColors.TEXT_SECONDARY)};
            }}
        """)
        
        # Status label (left side)
        self.status_label = QLabel("Ready")
        self.status_label.setFont(EditorFonts.status_text())
        self.status_bar.addWidget(self.status_label)
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setStyleSheet(f"color: {EditorColors.to_stylesheet(EditorColors.BORDER_DEFAULT)};")
        self.status_bar.addWidget(separator)
        
        # Project name (middle)
        self.project_label = QLabel("No Project")
        self.project_label.setFont(EditorFonts.status_text())
        self.status_bar.addWidget(self.project_label)
        
        # FPS counter (right side)
        self.fps_label = QLabel("FPS: 0")
        self.fps_label.setFont(EditorFonts.status_text())
        self.status_bar.addPermanentWidget(self.fps_label)
    
    def _setup_timers(self) -> None:
        """Setup update timers."""
        # FPS counter update
        self.fps_timer = QTimer()
        self.fps_timer.timeout.connect(self._update_fps)
        self.fps_timer.start(1000)  # Update every second
    
    def _update_fps(self) -> None:
        """Update FPS counter."""
        # TODO: Implement FPS calculation
        self.fps_label.setText("FPS: 60")
    
    # Menu actions
    def _new_project(self) -> None:
        """Create new project."""
        project_manager = ProjectManager(self)
        if project_manager.create_new_project():
            self._load_project(project_manager.project_path)
    
    def _open_project(self) -> None:
        """Open existing project."""
        project_manager = ProjectManager(self)
        if project_manager.open_project():
            self._load_project(project_manager.project_path)
    
    def _load_project(self, project_path: str) -> None:
        """Load project from path."""
        import os
        from pathlib import Path

        project_file = Path(project_path)

        # If project file doesn't exist, create a new project
        if not project_file.exists():
            print(f"[Editor] Project file not found, creating new project at: {project_path}")
            try:
                # Ensure directory exists
                project_file.parent.mkdir(parents=True, exist_ok=True)

                # Create new project
                self.project = Project.create_new(str(project_file.parent), project_file.stem)
                if self.project:
                    # Save the project file
                    self.project.save_to_file_sync(project_path)
                    print(f"[Editor] Created new project: {self.project.name}")
                else:
                    QMessageBox.critical(self, "Error", "Failed to create new project")
                    return
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create project: {e}")
                import traceback
                traceback.print_exc()
                return
        else:
            # Load existing project
            try:
                self.project = Project.load_from_file_sync(project_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load project: {e}\n\nThe project file may be corrupted. Try creating a new project.")
                import traceback
                traceback.print_exc()
                return

        if self.project:
            self.setWindowTitle(f"Game Engine Editor - {self.project.name}")
            self.status_label.setText("Project loaded")
            self.project_label.setText(f"📁 {self.project.name}")
            self.editor_interface.emit_plugin_event("project_loaded", self.project)

            # Create default scene if project has no scenes
            if not self.project.scenes:
                from engine.core.scene import Scene
                default_scene = Scene("Main Scene")
                self.project.add_scene(default_scene)
                print(f"[Editor] Created default scene for project")

            # Update docks with project data
            self.scene_tree_dock.set_project(self.project)
            self.file_system_dock.set_project(self.project)

            # Update scene editor with first scene
            if self.project.scenes:
                self.scene_editor.set_scene(self.project.scenes[0])
                print(f"[Editor] Loaded scene: {self.project.scenes[0].name}")
    
    def _load_last_project(self) -> None:
        """Load the last opened project."""
        # TODO: Implement last project loading from settings
        pass
    
    def _save_scene(self) -> None:
        """Save current scene."""
        # TODO: Implement scene saving
        self.status_label.setText("Scene saved")
    
    def _new_scene(self) -> None:
        """Create new scene."""
        # TODO: Implement new scene creation
        self.status_label.setText("New scene created")
    
    def _project_settings(self) -> None:
        """Open project settings."""
        # TODO: Implement project settings dialog
        self.status_label.setText("Project settings")
    
    def _play_scene(self) -> None:
        """Play current scene."""
        if self.editor_interface.is_playing_scene():
            self.editor_interface.stop_scene()
            self.status_label.setText("Scene stopped")
        else:
            self.editor_interface.play_scene()
            self.status_label.setText("Playing scene...")
    
    def _undo(self) -> None:
        """Perform undo."""
        # TODO: Implement undo system
        self.status_label.setText("Undo")
    
    def _redo(self) -> None:
        """Perform redo."""
        # TODO: Implement redo system
        self.status_label.setText("Redo")
    
    def _about(self) -> None:
        """Show about dialog."""
        QMessageBox.about(self, "About", "Game Engine Editor v1.0\n\nA modern game engine.")

    def _open_pixel_editor(self) -> None:
        """Open pixel art editor."""
        from engine.tools.pixel_art_editor.main_editor import PixelArtEditor

        dialog = QDialog(self)
        dialog.setWindowTitle("Pixel Art Editor")
        dialog.resize(1200, 800)

        # Apply modern styling like Project Manager
        dialog.setStyleSheet(f"""
            QDialog {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_PRIMARY)};
            }}
            QToolBar {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_SECONDARY)};
                border: none;
                padding: {EditorSpacing.SM}px;
            }}
            QPushButton {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BUTTON_SECONDARY_BG)};
                color: {EditorColors.to_stylesheet(EditorColors.TEXT_PRIMARY)};
                border: 1px solid {EditorColors.to_stylesheet(EditorColors.BORDER_DEFAULT)};
                padding: 6px 12px;
                border-radius: {EditorSpacing.RADIUS_SM}px;
            }}
            QPushButton:hover {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BUTTON_SECONDARY_HOVER)};
            }}
        """)

        # Create pixel art editor
        editor = PixelArtEditor(dialog, 64, 64)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(editor)

        dialog.exec()

    def closeEvent(self, event) -> None:
        """Handle window close event."""
        # Clean shutdown
        if self.project:
            # TODO: Prompt to save unsaved changes
            pass
        
        # Mark clean shutdown
        crash_handler.mark_clean_shutdown()
        
        # Accept close event
        event.accept()
    
    def __repr__(self) -> str:
        project_name = self.project.name if self.project else "No Project"
        return f"EditorNode(project='{project_name}')"
