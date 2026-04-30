# /**************************************************************************/
# /*  play_mode_controller.py                                                */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Controller for play mode functionality."""

from typing import Optional, Callable

from PySide6.QtWidgets import QMessageBox

from engine.core.node_base import Node
from engine.core.project_secure import SecureProject as Project


class PlayModeController:
    """Manages play mode state and game runtime."""

    def __init__(self, console_callback: Callable[[str], None]):
        """Initialize the play mode controller.

        Args:
            console_callback: Function to log messages to console.
        """
        self._console_log = console_callback
        self.runtime: Optional[object] = None
        self._is_playing: bool = False
        self._is_paused: bool = False

    @property
    def is_playing(self) -> bool:
        return self._is_playing

    @property
    def is_paused(self) -> bool:
        return self._is_paused

    def start_play(self, project: Project, viewport_widget, scene_tree_widget) -> bool:
        """Start play mode.

        Args:
            project: The active project.
            viewport_widget: The viewport widget to update.
            scene_tree_widget: The scene tree widget to update.

        Returns:
            True if play mode started successfully.
        """
        if not project or not project.active_scene:
            QMessageBox.warning(None, "Play", "No project/scene to play.")
            return False

        try:
            from engine.runtime.game_loop import GameRuntime
            self.runtime = GameRuntime(project)
            self.runtime._run_init()

            self._is_playing = True
            self._is_paused = False

            viewport_widget.set_play_mode(True)
            scene_tree_widget.set_scene(project.active_scene)

            self._console_log("▶️ Play mode started")
            self._console_log(f"   Scene: {project.active_scene.name}")
            self._console_log(f"   Nodes: {len(project.active_scene.root.children)}")

            return True
        except Exception as e:
            self._console_log(f"Failed to start play mode: {e}")
            return False

    def pause_play(self) -> None:
        """Pause/unpause play mode."""
        if not self._is_playing:
            return

        self._is_paused = not self._is_paused
        if self._is_paused:
            self._console_log("⏸️ Game paused")
        else:
            self._console_log("▶️ Game resumed")

    def stop_play(self, project: Optional[Project], viewport_widget, scene_tree_widget) -> None:
        """Stop play mode and reset the scene.

        Args:
            project: The active project.
            viewport_widget: The viewport widget to update.
            scene_tree_widget: The scene tree widget to update.
        """
        self._is_playing = False
        self._is_paused = False

        viewport_widget.set_play_mode(False)

        if project and project.active_scene:
            scene_tree_widget.set_scene(project.active_scene)
            viewport_widget.set_scene(project.active_scene)

        self._console_log("⏹️ Play mode stopped")

        if hasattr(self, 'runtime'):
            del self.runtime
            self.runtime = None
