# /**************************************************************************/
# /*  main_window.py                                                        */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Modern game engine UI inspired by Godot, Unity, and Unreal Engine."""

from __future__ import annotations

from typing import Optional
import sys
import os
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeySequence, QAction
from PySide6.QtWidgets import (
    QApplication, QFileDialog, QMainWindow, QWidget,
    QDockWidget, QTabWidget, QSplitter, QHBoxLayout,
    QVBoxLayout, QToolBar, QStatusBar, QMenuBar, QLabel
)

from engine.core.node_base import Node
from engine.core.project_secure import SecureProject as Project
from engine import crash_handler
from engine.session_manager import SessionManager
from engine.extensions.manager_secure import SecureExtensionManager as ExtensionManager
from engine.tools.pixel_art_editor.main_editor import PixelArtEditor
from ui.dialogs.welcome_dialog import WelcomeDialog
from ui.dialogs.new_project_dialog import NewProjectWizardDialog
from ui.widgets.console_panel import ConsolePanel
from ui.widgets.file_browser import ProjectFileBrowserWidget
from ui.widgets.inspector import InspectorWidget
from ui.widgets.scene_tree import SceneTreeWidget
from ui.widgets.viewport import ViewportWidget
from ui.widgets.kanban_board import KanbanBoardWidget
from ui.widgets.dialog_manager import DialogManagerWidget
from ui.widgets.profiler_panel import ProfilerPanel
from ui.controllers import PlayModeController, ProjectManager
from ui.action_registry import ActionRegistry, RegisteredAction


class MainEditorWindow(QMainWindow):
    """Modern game engine UI inspired by Godot, Unity, and Unreal Engine."""

    def __init__(self):
        super().__init__()
        self.project: Optional[Project] = None
        self.selected_node: Optional[Node] = None
        self.project_root: str = os.getcwd()
        self.last_project_path: str = ""
        self.recent_projects: list[str] = []
        self.extension_manager = ExtensionManager(
            os.path.join(self.project_root, "extensions_store")
        )
        self.pixel_editor_window: Optional[QMainWindow] = None
        self.kanban_window: Optional[QMainWindow] = None
        self.dialog_manager_window: Optional[QMainWindow] = None
        self.action_registry = ActionRegistry()

        # Controllers
        self._console_callback = lambda msg: self.console_panel.log(msg) if hasattr(self, 'console_panel') else None
        self._project_mgr = ProjectManager(self._console_callback)
        self._play_mode_ctrl = PlayModeController(self._console_callback)

        # Session manager
        self._session_mgr = SessionManager(interval=60)
        self._session_mgr.set_snapshot_provider(self._build_session_snapshot)

        # Crash handler
        crash_handler.install(session_saver=self._build_session_snapshot)

        self.init_ui()
        self._register_context_actions()
        self.setWindowTitle("Game Engine Studio 2D")
        self.setGeometry(50, 50, 1600, 1000)
        self.show_welcome_dialog()

        # Start auto-save
        self._session_mgr.start()

    def init_ui(self) -> None:
        """Initialize modern UI layout with Neumorphism theme."""
        # Load Neumorphism stylesheet
        self._load_stylesheet()
        
    def _load_stylesheet(self) -> None:
        """Load the Neumorphism QSS stylesheet."""
        style_path = os.path.join(
            os.path.dirname(__file__), "styles", "neumorphism.qss"
        )
        try:
            if os.path.exists(style_path):
                with open(style_path, "r", encoding="utf-8") as f:
                    self.setStyleSheet(f.read())
            else:
                print(f"Warning: Stylesheet not found at {style_path}")
        except Exception as e:
            print(f"Error loading stylesheet: {e}")

        # Create central tabbed viewport (Unity-style)
        self._create_central_area()

        # Create dock widgets
        self._create_left_dock()
        self._create_right_dock()
        self._create_bottom_dock_with_tabs()

        # Create menu bar
        self._create_menu_bar()

        # Create toolbar
        self._create_toolbar()

        # Create status bar
        self._create_status_bar()

    def _register_context_actions(self) -> None:
        """Register context-aware shortcuts for editor-wide actions."""
        self.action_registry.register(
            RegisteredAction(
                name="save_project",
                shortcut="Ctrl+S",
                callback=self.save_project,
                context="global",
            )
        )

    def _create_central_area(self) -> None:
        """Create central tabbed viewport area (Unity-style Scene/Game/Animation tabs)."""
        self._viewport_tabs = QTabWidget()
        self._viewport_tabs.setTabPosition(QTabWidget.TabPosition.North)
        self._viewport_tabs.setDocumentMode(True)
        self._viewport_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #1a1a1a;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #888;
                padding: 10px 20px;
                border: 1px solid #444;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: #1a1a1a;
                color: #fff;
                border: 1px solid #555;
                border-bottom: none;
            }
        """)

        # Scene view tab
        self.viewport = ViewportWidget()
        self._viewport_tabs.addTab(self.viewport, "Scene")

        # Game view tab
        self._game_view = QLabel("Game View\nPress ▶️ Play to start")
        self._game_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._game_view.setStyleSheet("color: #666; font-size: 18px; font-weight: bold;")
        self._viewport_tabs.addTab(self._game_view, "Game")

        # Animation tab
        self._animation_view = QLabel("Animation Editor")
        self._animation_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._animation_view.setStyleSheet("color: #666; font-size: 18px; font-weight: bold;")
        self._viewport_tabs.addTab(self._animation_view, "Animation")

        self.setCentralWidget(self._viewport_tabs)

    def _create_left_dock(self) -> None:
        """Create left dock with Scene Tree and Asset Browser (Godot-style)."""
        left_dock = QDockWidget("Scene & Assets", self)
        left_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable |
                            QDockWidget.DockWidgetFeature.DockWidgetFloatable)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        # Tab widget for Scene Tree and Asset Browser
        left_tabs = QTabWidget()
        left_tabs.setDocumentMode(True)

        # Scene Tree tab
        self.scene_tree = SceneTreeWidget()
        self.scene_tree.node_selected.connect(self.on_node_selected)
        left_tabs.addTab(self.scene_tree, "Scene")

        # Asset Browser tab
        self.file_browser = ProjectFileBrowserWidget()
        self.file_browser.file_activated.connect(self.open_file_from_browser)
        left_tabs.addTab(self.file_browser, "Assets")

        left_layout.addWidget(left_tabs)
        left_dock.setWidget(left_widget)

        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, left_dock)

    def _create_right_dock(self) -> None:
        """Create right dock with Inspector (Godot/Unity-style)."""
        right_dock = QDockWidget("Inspector", self)
        right_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable |
                             QDockWidget.DockWidgetFeature.DockWidgetFloatable)

        self.inspector = InspectorWidget()
        right_dock.setWidget(self.inspector)

        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, right_dock)

    def _create_bottom_dock_with_tabs(self) -> None:
        """Create bottom dock with Console and Profiler as tabs."""
        # Create console dock
        console_dock = QDockWidget("Console", self)
        console_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable |
                                QDockWidget.DockWidgetFeature.DockWidgetFloatable)

        self.console_panel = ConsolePanel(self)
        self.console_panel.command_submitted.connect(self.handle_console_command)
        console_dock.setWidget(self.console_panel)

        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, console_dock)
        self.console_panel.log("Console ready. Type 'help' for commands.")

        # Create profiler dock
        profiler_dock = QDockWidget("Profiler", self)
        profiler_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable |
                                 QDockWidget.DockWidgetFeature.DockWidgetFloatable)

        self.profiler_panel = ProfilerPanel(self)
        profiler_dock.setWidget(self.profiler_panel)

        # Add to bottom dock area and tabify with console
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, profiler_dock)
        self.tabifyDockWidget(console_dock, profiler_dock)

    def _create_menu_bar(self) -> None:
        """Create menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        new_action = QAction("New Project", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)

        open_action = QAction("Open Project", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)

        save_action = QAction("Save Project", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(lambda: self.action_registry.trigger("Ctrl+S"))
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        import_action = QAction("Import Godot", self)
        import_action.triggered.connect(self.import_godot)
        file_menu.addAction(import_action)

        export_action = QAction("Export Godot", self)
        export_action.triggered.connect(self.export_godot)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        undo_action = QAction("Undo", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(lambda: self.action_registry.trigger("Ctrl+Z"))
        edit_menu.addAction(undo_action)

        redo_action = QAction("Redo", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(lambda: self.action_registry.trigger("Ctrl+Y"))
        edit_menu.addAction(redo_action)

        # View menu
        view_menu = menubar.addMenu("View")
        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.setShortcut(QKeySequence.StandardKey.ZoomIn)
        zoom_in_action.triggered.connect(self._zoom_in)
        view_menu.addAction(zoom_in_action)

        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.setShortcut(QKeySequence.StandardKey.ZoomOut)
        zoom_out_action.triggered.connect(self._zoom_out)
        view_menu.addAction(zoom_out_action)

        reset_view_action = QAction("Reset View", self)
        reset_view_action.triggered.connect(self._reset_view)
        view_menu.addAction(reset_view_action)

        scene_menu = menubar.addMenu("Scene")
        add_node_action = QAction("Add Node2D", self)
        add_node_action.triggered.connect(lambda: self._add_node_from_ui("Node2D"))
        scene_menu.addAction(add_node_action)

        add_sprite_action = QAction("Add Sprite2D", self)
        add_sprite_action.triggered.connect(lambda: self._add_node_from_ui("Sprite2D"))
        scene_menu.addAction(add_sprite_action)

        new_scene_action = QAction("New Scene", self)
        new_scene_action.triggered.connect(self._new_scene_from_ui)
        scene_menu.addAction(new_scene_action)

        # Tools menu
        tools_menu = menubar.addMenu("Tools")

        pixel_action = QAction("Pixel Art Editor", self)
        pixel_action.triggered.connect(self.open_pixel_editor)
        tools_menu.addAction(pixel_action)

        remap_action = QAction("Add Remapping Scene", self)
        remap_action.triggered.connect(self.add_remapping_scene)
        tools_menu.addAction(remap_action)

        tools_menu.addSeparator()

        ext_action = QAction("Extension Manager", self)
        ext_action.triggered.connect(self.open_extension_manager)
        tools_menu.addAction(ext_action)

        kanban_action = QAction("Kanban Board", self)
        kanban_action.triggered.connect(self.open_kanban_board)
        tools_menu.addAction(kanban_action)

        dialog_action = QAction("Dialog Manager", self)
        dialog_action.triggered.connect(self.open_dialog_manager)
        tools_menu.addAction(dialog_action)

        # Help menu
        help_menu = menubar.addMenu("Help")
        help_menu.addAction("About")

    def _create_toolbar(self) -> None:
        """Create toolbar (standard game engine layout)."""
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #3d3d3d;
                spacing: 4px;
                padding: 4px;
            }
            QToolBar QToolButton {
                background-color: #4d4d4d;
                color: #fff;
                border: 1px solid #555;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QToolBar QToolButton:hover {
                background-color: #5d5d5d;
            }
            QToolBar QToolButton:pressed {
                background-color: #4a6fa5;
            }
        """)

        new_action = QAction("New", self)
        new_action.triggered.connect(self.new_project)
        toolbar.addAction(new_action)

        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_project)
        toolbar.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.triggered.connect(lambda: self.action_registry.trigger("Ctrl+S"))
        toolbar.addAction(save_action)

        toolbar.addSeparator()

        add_node_action = QAction("Add Node2D", self)
        add_node_action.triggered.connect(lambda: self._add_node_from_ui("Node2D"))
        toolbar.addAction(add_node_action)

        add_sprite_action = QAction("Add Sprite2D", self)
        add_sprite_action.triggered.connect(lambda: self._add_node_from_ui("Sprite2D"))
        toolbar.addAction(add_sprite_action)

        new_scene_action = QAction("New Scene", self)
        new_scene_action.triggered.connect(self._new_scene_from_ui)
        toolbar.addAction(new_scene_action)

        toolbar.addSeparator()

        # Play/Stop actions
        self.play_action = QAction("▶️ Play", self)
        self.play_action.triggered.connect(self.on_play)
        toolbar.addAction(self.play_action)

        self.pause_action = QAction("⏸️ Pause", self)
        self.pause_action.triggered.connect(self.on_pause)
        toolbar.addAction(self.pause_action)

        self.stop_action = QAction("⏹️ Stop", self)
        self.stop_action.triggered.connect(self.on_stop)
        toolbar.addAction(self.stop_action)

        self.pause_action.setEnabled(False)
        self.stop_action.setEnabled(False)

    def _create_status_bar(self) -> None:
        """Create status bar."""
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #3d3d3d;
                color: #fff;
                border-top: 1px solid #555;
            }
        """)
        self.status_bar.showMessage("Ready")
        self.setStatusBar(self.status_bar)

    def _zoom_in(self) -> None:
        self.viewport.zoom = min(self.viewport.zoom * 1.1, 10.0)
        self.viewport.update()

    def _zoom_out(self) -> None:
        self.viewport.zoom = max(self.viewport.zoom / 1.1, 0.1)
        self.viewport.update()

    def _reset_view(self) -> None:
        self.viewport.zoom = 1.0
        self.viewport.pan_x = 0.0
        self.viewport.pan_y = 0.0
        self.viewport.update()

    def _add_node_from_ui(self, node_type: str) -> None:
        if not self.project or not self.project.active_scene:
            self.console_panel.log("No active scene. Create or open a project first.")
            return
        self.scene_tree._add_node_of_type(node_type)
        self.viewport.update()
        self._project_mgr._update_cache()

    def _new_scene_from_ui(self) -> None:
        if not self.project:
            self.console_panel.log("No project loaded.")
            return
        scene_name = f"Scene{len(self.project.scenes) + 1}"
        scene = self.project.create_scene(scene_name)
        self.project.active_scene = scene
        self.scene_tree.set_scene(scene)
        self.viewport.set_scene(scene)
        self._project_mgr._update_cache()
        self.console_panel.log(f"Created scene: {scene_name}")

    # ==================== Project Operations ====================

    def new_project(self) -> None:
        """Create new project via Wizard"""
        dialog = NewProjectWizardDialog(self)
        if not dialog.exec():
            return

        name = dialog.project_name
        path = dialog.project_path

        # Delegate to ProjectManager controller
        if self._project_mgr.new_project(
            name=name,
            path=path,
            features=dialog.features,
            scene_tree_widget=self.scene_tree,
            viewport_widget=self.viewport,
            file_browser_widget=self.file_browser
        ):
            # Sync project from controller to view
            self.project = self._project_mgr.project
            self.project_root = self._project_mgr.project_root
            self.last_project_path = self._project_mgr.last_project_path
            self.recent_projects = self._project_mgr.recent_projects
            self._push_recent_project(self.last_project_path)

    def open_project(self) -> None:
        """Open existing project via ProjectManager."""
        if self._project_mgr.open_project(
            parent_widget=self,
            scene_tree_widget=self.scene_tree,
            viewport_widget=self.viewport,
            file_browser_widget=self.file_browser
        ):
            # Sync state from controller to view
            self.project = self._project_mgr.project
            self.project_root = self._project_mgr.project_root
            self.last_project_path = self._project_mgr.last_project_path
            self.recent_projects = self._project_mgr.recent_projects

    def save_project(self) -> None:
        """Save current project via ProjectManager."""
        if self._project_mgr.save_project(self):
            # Sync state from controller to view
            self.last_project_path = self._project_mgr.last_project_path
            self.recent_projects = self._project_mgr.recent_projects

    def on_node_selected(self, node: Node) -> None:
        """Handle node selection"""
        self.selected_node = node
        self.inspector.set_node(node)
        self.viewport.select_node(node)

    # ==================== Play Mode ====================

    def on_play(self) -> None:
        """Start play mode via PlayModeController."""
        if self._play_mode_ctrl.start_play(
            project=self.project,
            viewport_widget=self.viewport,
            scene_tree_widget=self.scene_tree
        ):
            # Update UI
            self.play_action.setEnabled(False)
            self.pause_action.setEnabled(True)
            self.stop_action.setEnabled(True)

    def on_pause(self) -> None:
        """Pause/unpause play mode via PlayModeController."""
        self._play_mode_ctrl.pause_play()
        # Update UI based on pause state
        if self._play_mode_ctrl.is_paused:
            self.pause_action.setText("▶️ Resume")
        else:
            self.pause_action.setText("⏸️ Pause")

    def on_stop(self) -> None:
        """Stop play mode via PlayModeController."""
        self._play_mode_ctrl.stop_play(
            project=self.project,
            viewport_widget=self.viewport,
            scene_tree_widget=self.scene_tree
        )
        # Update UI
        self.play_action.setEnabled(True)
        self.pause_action.setEnabled(False)
        self.stop_action.setEnabled(False)
        self.pause_action.setText("⏸️ Pause")

    # ==================== Tools ====================

    def open_pixel_editor(self) -> None:
        """Open Pixel Art Editor in separate window."""
        if self.pixel_editor_window is None or not self.pixel_editor_window.isVisible():
            from PySide6.QtWidgets import QMainWindow

            self.pixel_editor_window = QMainWindow(self)
            self.pixel_editor_window.setWindowTitle("Pixel Art Editor")
            self.pixel_editor_window.setGeometry(150, 150, 1000, 700)

            # Create pixel art editor
            editor = PixelArtEditor(width=64, height=64)
            editor.image_saved.connect(self._on_pixel_saved)

            self.pixel_editor_window.setCentralWidget(editor)
            self.pixel_editor_window.show()

            self.console_panel.log("Pixel Art Editor opened")
        else:
            self.pixel_editor_window.raise_()
            self.pixel_editor_window.activateWindow()

    def _on_pixel_saved(self, path: str) -> None:
        """Handle pixel art saved."""
        self.console_panel.log(f"Pixel art saved to: {path}")
        # If project exists, copy to Game Files folder
        if self.project_root:
            import shutil
            from pathlib import Path
            dest = Path(self.project_root) / "Game Files" / Path(path).name
            shutil.copy2(path, dest)
            self.console_panel.log(f"Pixel art copied to project: {dest}")

    def add_remapping_scene(self) -> None:
        """Add Remapping Scene to current project."""
        if self._project_mgr.add_remapping_scene(self.scene_tree):
            # Sync state
            self.project = self._project_mgr.project
            self.console_panel.log("Remapping Scene added successfully")

    def import_godot(self) -> None:
        """Import Godot project via ProjectManager."""
        if self._project_mgr.import_godot(
            parent_widget=self,
            scene_tree_widget=self.scene_tree,
            viewport_widget=self.viewport,
            file_browser_widget=self.file_browser
        ):
            # Sync state from controller to view
            self.project = self._project_mgr.project
            self.project_root = self._project_mgr.project_root

    def export_godot(self) -> None:
        """Export project to Godot format via ProjectManager."""
        self._project_mgr.export_godot(self)

    def open_file_from_browser(self, file_path: str) -> None:
        """Open file from browser via ProjectManager."""
        if self._project_mgr.open_file_from_browser(
            file_path=file_path,
            scene_tree_widget=self.scene_tree,
            viewport_widget=self.viewport,
            file_browser_widget=self.file_browser
        ):
            # Sync state from controller to view
            self.project = self._project_mgr.project
            self.project_root = self._project_mgr.project_root
            self.last_project_path = self._project_mgr.last_project_path
            self.recent_projects = self._project_mgr.recent_projects

    def open_extension_manager(self) -> None:
        from ui.dialogs.extension_manager_dialog import ExtensionManagerDialog
        dialog = ExtensionManagerDialog(self.extension_manager, self)
        dialog.exec()
        self.console_panel.log(f"Extensions installed: {', '.join(self.extension_manager.list_extensions()) or 'none'}")

    def open_kanban_board(self) -> None:
        if not self.project:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Tools", "Please open a project first.")
            return

        if self.kanban_window is None:
            from PySide6.QtWidgets import QMainWindow
            self.kanban_window = QMainWindow(self)
            self.kanban_window.setWindowTitle("Kanban Board")
            self.kanban_window.setCentralWidget(KanbanBoardWidget(self.project_root, self.kanban_window))
            self.kanban_window.resize(900, 600)
        self.kanban_window.show()
        self.kanban_window.raise_()

    def open_dialog_manager(self) -> None:
        if not self.project:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Tools", "Please open a project first.")
            return

        if self.dialog_manager_window is None:
            from PySide6.QtWidgets import QMainWindow
            from ui.widgets.dialogue_editor import DialogueEditor
            self.dialog_manager_window = QMainWindow(self)
            self.dialog_manager_window.setWindowTitle("Dialogue Manager (Advanced)")
            self.dialog_editor = DialogueEditor()
            self.dialog_manager_window.setCentralWidget(self.dialog_editor)
            self.dialog_manager_window.resize(1000, 700)
        self.dialog_manager_window.show()
        self.dialog_manager_window.raise_()

    # ==================== Dialogs ====================

    def show_welcome_dialog(self) -> None:
        dialog = WelcomeDialog(self.recent_projects, self)
        if not dialog.exec():
            return
        if dialog.selected_action == "new":
            self.new_project()
        elif dialog.selected_action == "create_sample" and dialog.selected_path:
            self.create_sample_project(dialog.selected_path)
        elif dialog.selected_action == "open":
            self.open_project()
        elif dialog.selected_action == "import_godot":
            self.import_godot()
        elif dialog.selected_action == "open_recent" and dialog.selected_path:
            self.open_file_from_browser(dialog.selected_path)
        elif dialog.selected_action == "recover_session":
            self.recover_session()

    def create_sample_project(self, path: str) -> None:
        """Quick create a sample project at the given path."""
        name = os.path.basename(path)

        # Create directories
        os.makedirs(path, exist_ok=True)
        os.makedirs(os.path.join(path, "scenes"), exist_ok=True)
        os.makedirs(os.path.join(path, "Game Files"), exist_ok=True)
        os.makedirs(os.path.join(path, "scripts"), exist_ok=True)
        os.makedirs(os.path.join(path, ".Kanban"), exist_ok=True)

        self.project = Project(name)
        scene = self.project.create_scene("MainScene")
        self.scene_tree.set_scene(scene)
        self.viewport.set_scene(scene)

        self.project_root = path
        self.file_browser.set_root_path(self.project_root)

        self.last_project_path = os.path.join(path, f"{name}.Game")
        self._project_mgr.current_project = self.project
        self._project_mgr.project_root = self.project_root
        self._project_mgr.last_project_path = self.last_project_path
        self._project_mgr._attach_project_services(self.project_root)
        from ui.actions.project_io import save_project
        save_project(self.last_project_path, self.project)
        self._project_mgr._update_cache()
        self._project_mgr._git_snapshot("Initial sample project")
        self._push_recent_project(self.last_project_path)

        self.console_panel.log(f"Created sample project '{name}' at {path}.")
        self.console_panel.log(f"Saved project file: {self.last_project_path}")

    def recover_session(self) -> None:
        """Recover session from crash."""
        from engine.crash_handler import clear_recovery, get_recovery_path
        from ui.actions.project_io import load_project

        recovery_path = get_recovery_path()
        if not recovery_path:
            self.console_panel.log("No recovery file found.")
            return

        try:
            self.project = load_project(recovery_path)
            self.project_root = str(recovery_path.parent.parent)
            self.file_browser.set_root_path(self.project_root)
            self.last_project_path = str(recovery_path)
            self._project_mgr.current_project = self.project
            self._project_mgr.project_root = self.project_root
            self._project_mgr.last_project_path = self.last_project_path
            self._project_mgr._attach_project_services(self.project_root)

            if self.project.active_scene:
                self.scene_tree.set_scene(self.project.active_scene)
                self.viewport.set_scene(self.project.active_scene)

            clear_recovery()
            self.console_panel.log(f"Recovered session from: {recovery_path}")
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Recovery Success", "Session recovered successfully!")
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Recovery Error", f"Failed to recover session: {str(e)}")
            self.console_panel.log(f"Recovery failed: {e}")

    # ==================== Console ====================

    def handle_console_command(self, command: str) -> None:
        self.console_panel.log(f"> {command}")
        parts = command.split()
        if not parts:
            return
        cmd = parts[0].lower()
        try:
            # System commands
            if cmd == "cls" or cmd == "clear":
                self.console_panel.clear()
            elif cmd == "mkdir" and len(parts) >= 2:
                path = " ".join(parts[1:])
                os.makedirs(path, exist_ok=True)
                self.console_panel.log(f"Created directory: {path}")
            elif cmd == "cd" and len(parts) >= 2:
                path = " ".join(parts[1:])
                if os.path.isdir(path):
                    os.chdir(path)
                    self.console_panel.log(f"Changed to: {os.getcwd()}")
                else:
                    self.console_panel.log(f"Directory not found: {path}")
            elif cmd == "ls" or cmd == "dir":
                for item in os.listdir():
                    self.console_panel.log(item)
            elif cmd == "pwd":
                self.console_panel.log(os.getcwd())

            # Engine commands
            elif cmd == "help":
                self._show_help()
            elif cmd == "save":
                if self.last_project_path and self.project:
                    from ui.actions.project_io import save_project
                    save_project(self.last_project_path, self.project)
                    self._project_mgr._update_cache()
                    self._project_mgr._git_snapshot("Console save")
                    self.console_panel.log(f"Saved: {self.last_project_path}")
                else:
                    self.console_panel.log("No known project path. Use GUI Save first.")
            elif cmd == "open" and len(parts) >= 2:
                self.open_file_from_browser(" ".join(parts[1:]))
            elif cmd == "project_info":
                self._show_project_info()
            elif cmd == "add_node" and len(parts) >= 2:
                self._console_add_node(parts[1])
            elif cmd == "delete" and len(parts) >= 2:
                self._console_delete_node(parts[1])
            elif cmd == "list_nodes":
                self._console_list_nodes()
            elif cmd == "select" and len(parts) >= 2:
                self._console_select_node(parts[1])
            elif cmd == "create_scene" and len(parts) >= 2:
                self._console_create_scene(parts[1])
            elif cmd == "list_scenes":
                self._console_list_scenes()
            elif cmd == "switch_scene" and len(parts) >= 2:
                self._console_switch_scene(parts[1])
            elif cmd == "fps":
                self.console_panel.log(f"Current FPS: Check Profiler panel")
            elif cmd == "mem" or cmd == "memory":
                self.console_panel.log(f"Memory usage: Check Profiler panel")
            else:
                self.console_panel.log(f"Unknown command: {cmd}. Type 'help' for available commands.")
        except Exception as e:
            self.console_panel.log(f"ERROR: {e}")

    def _show_help(self) -> None:
        """Show console help."""
        self.console_panel.log("=== System Commands ===")
        self.console_panel.log("  cls, clear          - Clear console")
        self.console_panel.log("  mkdir <path>        - Create directory")
        self.console_panel.log("  cd <path>           - Change directory")
        self.console_panel.log("  ls, dir             - List directory contents")
        self.console_panel.log("  pwd                 - Print working directory")
        self.console_panel.log("")
        self.console_panel.log("=== Engine Commands ===")
        self.console_panel.log("  help                - Show this help")
        self.console_panel.log("  save                - Save current project")
        self.console_panel.log("  open <path>         - Open project file")
        self.console_panel.log("  project_info        - Show project information")
        self.console_panel.log("  add_node <type>     - Add node to scene (e.g., Node2D, Sprite)")
        self.console_panel.log("  delete <node_id>     - Delete node from scene")
        self.console_panel.log("  list_nodes          - List all nodes in scene")
        self.console_panel.log("  select <node_id>     - Select node by ID")
        self.console_panel.log("  create_scene <name> - Create new scene")
        self.console_panel.log("  list_scenes         - List all scenes")
        self.console_panel.log("  switch_scene <name>  - Switch to scene")
        self.console_panel.log("  fps                 - Show FPS (check Profiler)")
        self.console_panel.log("  mem, memory         - Show memory (check Profiler)")

    def _show_project_info(self) -> None:
        """Show project information."""
        if not self.project:
            self.console_panel.log("No project loaded.")
        else:
            import json
            data = {
                "name": self.project.name,
                "scenes": len(self.project.scenes),
                "active_scene": self.project.active_scene.name if self.project.active_scene else None,
                "scene_count": len(self.project.scenes),
            }
            self.console_panel.log(json.dumps(data, indent=2))

    def _console_add_node(self, node_type: str) -> None:
        """Add node to scene via console."""
        if not self.project or not self.project.active_scene:
            self.console_panel.log("No active scene. Create or load a project first.")
            return

        from engine.core.nodes import Node2D, Sprite, Label as EngineLabel

        node_map = {
            "node2d": Node2D,
            "sprite": Sprite,
            "label": EngineLabel,
        }

        if node_type.lower() not in node_map:
            self.console_panel.log(f"Unknown node type: {node_type}. Available: {', '.join(node_map.keys())}")
            return

        node_class = node_map[node_type.lower()]
        new_node = node_class()
        new_node.name = f"{node_type}_{len(self.project.active_scene.root.children)}"
        self.project.active_scene.add_node(new_node, parent=self.project.active_scene.root)
        self.scene_tree.set_scene(self.project.active_scene)
        self.viewport.update()
        self._project_mgr._update_cache()
        self.console_panel.log(f"Added {node_type} node: {new_node.name} (ID: {new_node.uid})")

    def _console_delete_node(self, node_id: str) -> None:
        """Delete node from scene via console."""
        if not self.project or not self.project.active_scene:
            self.console_panel.log("No active scene.")
            return

        node = self.project.active_scene.get_node(node_id)
        if node:
            self.project.active_scene.remove_node(node)
            self.scene_tree.set_scene(self.project.active_scene)
            self.viewport.update()
            self._project_mgr._update_cache()
            self.console_panel.log(f"Deleted node: {node_id}")
        else:
            self.console_panel.log(f"Node not found: {node_id}")

    def _console_list_nodes(self) -> None:
        """List all nodes in scene."""
        if not self.project or not self.project.active_scene:
            self.console_panel.log("No active scene.")
            return

        def list_recursive(node: Node, depth: int = 0) -> None:
            indent = "  " * depth
            self.console_panel.log(f"{indent}- {node.name} ({node.__class__.__name__}) [ID: {node.uid[:8]}]")
            for child in node.children:
                list_recursive(child, depth + 1)

        self.console_panel.log("=== Scene Nodes ===")
        list_recursive(self.project.active_scene.root)

    def _console_select_node(self, node_id: str) -> None:
        """Select node by ID via console."""
        if not self.project or not self.project.active_scene:
            self.console_panel.log("No active scene.")
            return

        node = self.project.active_scene.get_node(node_id)
        if node:
            self.on_node_selected(node)
            self.console_panel.log(f"Selected node: {node.name}")
        else:
            self.console_panel.log(f"Node not found: {node_id}")

    def _console_create_scene(self, name: str) -> None:
        """Create new scene via console."""
        if not self.project:
            self.console_panel.log("No project loaded.")
            return

        scene = self.project.create_scene(name)
        self.project.active_scene = scene
        self.scene_tree.set_scene(scene)
        self.viewport.set_scene(scene)
        self._project_mgr._update_cache()
        self.console_panel.log(f"Created scene: {name} (ID: {scene.id})")

    def _console_list_scenes(self) -> None:
        """List all scenes."""
        if not self.project:
            self.console_panel.log("No project loaded.")
            return

        self.console_panel.log("=== Scenes ===")
        for scene_id, scene in self.project.scenes.items():
            marker = " [ACTIVE]" if scene == self.project.active_scene else ""
            self.console_panel.log(f"- {scene.name} (ID: {scene_id[:8]}){marker}")

    def _console_switch_scene(self, name: str) -> None:
        """Switch to scene by name."""
        if not self.project:
            self.console_panel.log("No project loaded.")
            return

        for scene_id, scene in self.project.scenes.items():
            if scene.name == name:
                self.project.set_active_scene(scene_id)
                active_scene = self.project.active_scene or scene
                self.scene_tree.set_scene(active_scene)
                self.viewport.set_scene(active_scene)
                self._project_mgr._update_cache()
                self.console_panel.log(f"Switched to scene: {name}")
                return

        self.console_panel.log(f"Scene not found: {name}")

    # ==================== Session Management ====================

    def _push_recent_project(self, path: str) -> None:
        if path in self.recent_projects:
            self.recent_projects.remove(path)
        self.recent_projects.insert(0, path)
        self.recent_projects = self.recent_projects[:15]

    def _build_session_snapshot(self):
        """Return a JSON-serialisable dict of the current session state."""
        if self.project is None:
            return None
        try:
            return {
                "project": self.project.to_dict(),
                "last_project_path": self.last_project_path,
                "recent_projects": self.recent_projects,
            }
        except Exception:
            return None

    def closeEvent(self, event) -> None:  # type: ignore[override]
        """Clean shutdown: stop session manager and mark crash handler."""
        self._session_mgr.stop(clean=True)
        crash_handler.mark_clean_shutdown()
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    window = MainEditorWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
