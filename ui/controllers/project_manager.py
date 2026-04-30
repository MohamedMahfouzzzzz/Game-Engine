# /**************************************************************************/
# /*  project_manager.py                                                   */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Controller for project I/O operations."""

from typing import Optional, Callable, List
from pathlib import Path

from PySide6.QtWidgets import QMessageBox, QFileDialog

from engine.core.project_secure import SecureProject as Project
from engine.core.project_cache import ProjectCache
from engine.core.project_git import ProjectGit
from engine.interop.godot_importer import GodotImporter
from engine.interop.godot_exporter import GodotExporter

from ui.actions.project_io import load_project, save_project


class ProjectManager:
    """Manages project loading, saving, and import/export operations."""

    def __init__(self, console_callback: Callable[[str], None]):
        """Initialize the project manager.

        Args:
            console_callback: Function to log messages to console.
        """
        self._console_log = console_callback
        self.current_project: Optional[Project] = None
        self.project_root: str = ""
        self.last_project_path: str = ""
        self.recent_projects: List[str] = []
        self.cache: Optional[ProjectCache] = None
        self.git: Optional[ProjectGit] = None

    @property
    def project(self) -> Optional[Project]:
        return self.current_project

    def new_project(
        self,
        name: str,
        path: str,
        features: dict,
        scene_tree_widget,
        viewport_widget,
        file_browser_widget
    ) -> bool:
        """Create a new project.

        Args:
            name: Project name.
            path: Project directory path.
            features: Optional features to include (kanban, dialog, etc.).
            scene_tree_widget: Scene tree widget to update.
            viewport_widget: Viewport widget to update.
            file_browser_widget: File browser widget to update.

        Returns:
            True if project created successfully.
        """
        import os

        try:
            # Create directories
            os.makedirs(path, exist_ok=True)
            os.makedirs(os.path.join(path, "scenes"), exist_ok=True)
            
            # Create GameFiles as the resources folder (res)
            game_files = os.path.join(path, "GameFiles")
            os.makedirs(game_files, exist_ok=True)
            legacy_game_files = os.path.join(path, "Game Files")
            os.makedirs(legacy_game_files, exist_ok=True)
            
            # Create resource subfolders
            os.makedirs(os.path.join(game_files, "sprites"), exist_ok=True)
            os.makedirs(os.path.join(game_files, "sounds"), exist_ok=True)
            os.makedirs(os.path.join(game_files, "music"), exist_ok=True)
            os.makedirs(os.path.join(game_files, "fonts"), exist_ok=True)
            os.makedirs(os.path.join(game_files, "tilesets"), exist_ok=True)
            os.makedirs(os.path.join(game_files, "palettes"), exist_ok=True)
            
            os.makedirs(os.path.join(path, "scripts"), exist_ok=True)
            os.makedirs(os.path.join(path, ".Kanban"), exist_ok=True)

            self.current_project = Project(name)
            scene = self.current_project.create_scene("MainScene")
            scene_tree_widget.set_scene(scene)
            viewport_widget.set_scene(scene)

            self.project_root = path
            file_browser_widget.set_root_path(self.project_root)

            self.last_project_path = os.path.join(path, f"{name}.Game")
            self._attach_project_services(path)
            save_project(self.last_project_path, self.current_project)
            self._update_cache()
            self._git_snapshot("Initial project")
            self._push_recent_project(self.last_project_path)

            features_msg = []
            if features.get("kanban"):
                features_msg.append("Kanban Board")
            if features.get("dialog"):
                features_msg.append("Dialog Manager")

            msg = f"Created new project '{name}' at {path}."
            if features_msg:
                msg += f" Features added: {', '.join(features_msg)}."
            self._console_log(msg)

            return True
        except Exception as e:
            self._console_log(f"Failed to create project: {e}")
            return False

    def open_project(
        self,
        parent_widget,
        scene_tree_widget,
        viewport_widget,
        file_browser_widget
    ) -> bool:
        """Open an existing project.

        Args:
            parent_widget: Parent widget for dialogs.
            scene_tree_widget: Scene tree widget to update.
            viewport_widget: Viewport widget to update.
            file_browser_widget: File browser widget to update.

        Returns:
            True if project opened successfully.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            parent_widget, "Open Project", "", "Project Files (*.Game)"
        )
        if not file_path:
            return False

        try:
            self.current_project = load_project(file_path)
            self.project_root = str(Path(file_path).parent)
            self._attach_project_services(self.project_root)
            file_browser_widget.set_root_path(self.project_root)
            self.last_project_path = file_path
            self._update_cache()
            self._push_recent_project(file_path)

            if self.current_project.active_scene:
                scene_tree_widget.set_scene(self.current_project.active_scene)
                viewport_widget.set_scene(self.current_project.active_scene)

            self._console_log(f"Opened project: {file_path}")
            return True
        except Exception as e:
            QMessageBox.critical(parent_widget, "Error", f"Failed to open project: {str(e)}")
            return False

    def save_project(self, parent_widget) -> bool:
        """Save the current project.

        Args:
            parent_widget: Parent widget for dialogs.

        Returns:
            True if project saved successfully.
        """
        if not self.current_project:
            QMessageBox.warning(parent_widget, "Warning", "No project to save")
            return False

        file_path = self.last_project_path
        if not file_path:
            file_path, _ = QFileDialog.getSaveFileName(
                parent_widget, "Save Project", "", "Project Files (*.Game)"
            )
            if not file_path:
                return False

        try:
            save_project(file_path, self.current_project)
            self.last_project_path = file_path
            self.project_root = str(Path(file_path).parent)
            self._attach_project_services(self.project_root)
            self._update_cache()
            self._git_snapshot("Save project")
            self._push_recent_project(file_path)
            self._console_log(f"Saved project: {file_path}")
            return True
        except Exception as e:
            QMessageBox.critical(parent_widget, "Error", f"Failed to save project: {str(e)}")
            return False

    def import_godot(
        self,
        parent_widget,
        scene_tree_widget,
        viewport_widget,
        file_browser_widget
    ) -> bool:
        """Import a Godot project or scene.

        Args:
            parent_widget: Parent widget for dialogs.
            scene_tree_widget: Scene tree widget to update.
            viewport_widget: Viewport widget to update.
            file_browser_widget: File browser widget to update.

        Returns:
            True if import successful.
        """
        import os

        file_path, _ = QFileDialog.getOpenFileName(
            parent_widget,
            "Import Godot",
            "",
            "Godot Project/Scene (project.godot *.tscn);;All Files (*)",
        )
        if not file_path:
            return False

        try:
            imported = GodotImporter().import_project(file_path)
            self.current_project = imported
            self.project_root = os.path.dirname(file_path)
            self._attach_project_services(self.project_root)
            file_browser_widget.set_root_path(self.project_root)
            if imported.active_scene:
                scene_tree_widget.set_scene(imported.active_scene)
                viewport_widget.set_scene(imported.active_scene)
                # Use current working directory for texture loading (assets are copied there)
                viewport_widget.set_project_root(os.getcwd())
            QMessageBox.information(
                parent_widget,
                "Import Success",
                f"Imported '{imported.name}' with {len(imported.scenes)} scene(s)."
            )
            self._console_log(f"Imported Godot: {file_path}")
            self._update_cache()
            return True
        except Exception as e:
            QMessageBox.critical(parent_widget, "Import Error", str(e))
            return False

    def export_godot(self, parent_widget) -> bool:
        """Export active scene to Godot format.

        Args:
            parent_widget: Parent widget for dialogs.

        Returns:
            True if export successful.
        """
        if not self.current_project or not self.current_project.active_scene:
            QMessageBox.warning(parent_widget, "Export", "No active project/scene to export.")
            return False

        file_path, _ = QFileDialog.getSaveFileName(
            parent_widget, "Export Godot Scene", "", "Godot Scene (*.tscn)"
        )
        if not file_path:
            return False

        try:
            out = GodotExporter().export_project(self.current_project, file_path)
            QMessageBox.information(parent_widget, "Export Success", f"Exported to {out}")
            self._console_log(f"Exported Godot scene: {out}")
            return True
        except Exception as e:
            QMessageBox.critical(parent_widget, "Export Error", str(e))
            return False

    def open_file_from_browser(
        self,
        file_path: str,
        scene_tree_widget,
        viewport_widget,
        file_browser_widget
    ) -> bool:
        """Open a file from the file browser.

        Args:
            file_path: Path to the file to open.
            scene_tree_widget: Scene tree widget to update.
            viewport_widget: Viewport widget to update.
            file_browser_widget: File browser widget to update.

        Returns:
            True if file opened successfully.
        """
        import os

        lower = file_path.lower()
        try:
            if lower.endswith(".Game"):
                self.current_project = load_project(file_path)
                self.project_root = os.path.dirname(file_path)
                self._attach_project_services(self.project_root)
                file_browser_widget.set_root_path(self.project_root)
                self.last_project_path = file_path
                self._update_cache()
                self._push_recent_project(file_path)
            elif lower.endswith(".tscn") or os.path.basename(lower) == "project.godot":
                self.current_project = GodotImporter().import_project(file_path)
                self.project_root = os.path.dirname(file_path)
                self._attach_project_services(self.project_root)
                file_browser_widget.set_root_path(self.project_root)
                self._update_cache()
            else:
                return False

            if self.current_project and self.current_project.active_scene:
                scene_tree_widget.set_scene(self.current_project.active_scene)
                viewport_widget.set_scene(self.current_project.active_scene)
                self._console_log(f"Opened from file browser: {file_path}")
            return True
        except Exception as e:
            QMessageBox.critical(None, "Open File Error", str(e))
            return False

    def add_remapping_scene(self, scene_tree_widget) -> bool:
        """Add Remapping Scene to current project."""
        if not self.current_project:
            QMessageBox.warning(None, "No Project", "No project loaded.")
            return False

        try:
            from engine.core.templates import RemappingScene

            # Create remapping scene
            remapping_scene = RemappingScene()
            remapping_scene.create_scene_structure()

            # Add to project
            self.current_project.add_scene(remapping_scene)
            self.current_project.active_scene = remapping_scene
            self._update_cache()

            # Update UI
            scene_tree_widget.set_scene(remapping_scene)

            self._console_log("Remapping Scene added to project")
            return True
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to add Remapping Scene: {str(e)}")
            return False

    def _push_recent_project(self, path: str) -> None:
        """Add project path to recent projects list."""
        if path in self.recent_projects:
            self.recent_projects.remove(path)
        self.recent_projects.insert(0, path)
        self.recent_projects = self.recent_projects[:15]

    def get_recent_projects(self) -> List[str]:
        """Return list of recent projects."""
        return self.recent_projects

    def _attach_project_services(self, root: str) -> None:
        self.cache = ProjectCache(root)
        self.cache.load()
        self.git = ProjectGit(root)
        try:
            if self.git.init():
                self._console_log("Git repository ready.")
        except Exception as exc:
            self._console_log(f"Git unavailable: {exc}")

    def _update_cache(self) -> None:
        if self.cache and self.current_project:
            self.cache.update_project(self.current_project, self.last_project_path)

    def _git_snapshot(self, message: str) -> None:
        if not self.git:
            return
        try:
            if self.git.snapshot(message):
                self._console_log(f"Git snapshot: {message}")
        except Exception as exc:
            self._console_log(f"Git snapshot skipped: {exc}")
