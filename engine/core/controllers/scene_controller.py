# /**************************************************************************/
# /*  scene_controller.py                                                   */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Native scene controller for engine."""

from typing import Dict, Optional, List, Callable
from engine.core.scene import Scene
from engine.core.node_base import Node

class SceneController:
    """Native engine scene controller for managing scene transitions and lifecycle."""

    def __init__(self):
        self._scenes: Dict[str, Scene] = {}
        self._current_scene: Optional[str] = None
        self._previous_scene: Optional[str] = None
        self._scene_stack: List[str] = []
        self._transition_callbacks: Dict[str, List[Callable]] = {}

    def add_scene(self, name: str, scene: Scene) -> None:
        """Add a scene to the controller."""
        self._scenes[name] = scene

    def remove_scene(self, name: str) -> bool:
        """Remove a scene."""
        if name in self._scenes:
            del self._scenes[name]
            return True
        return False

    def get_scene(self, name: str) -> Optional[Scene]:
        """Get a scene by name."""
        return self._scenes.get(name)

    def get_current_scene(self) -> Optional[Scene]:
        """Get the currently active scene."""
        if self._current_scene:
            return self._scenes.get(self._current_scene)
        return None

    def switch_to_scene(self, name: str) -> bool:
        """Switch to a scene by name."""
        if name not in self._scenes:
            return False

        self._previous_scene = self._current_scene
        self._current_scene = name

        # Trigger transition callbacks
        self._trigger_transition(name)

        return True

    def push_scene(self, name: str) -> bool:
        """Push scene onto stack (for sub-scenes)."""
        if name not in self._scenes:
            return False

        if self._current_scene:
            self._scene_stack.append(self._current_scene)

        self._current_scene = name
        self._trigger_transition(name)
        return True

    def pop_scene(self) -> bool:
        """Pop scene from stack."""
        if not self._scene_stack:
            return False

        previous = self._scene_stack.pop()
        self._current_scene = previous
        self._trigger_transition(previous)
        return True

    def on_scene_transition(self, scene_name: str, callback: Callable) -> None:
        """Register callback for scene transition."""
        if scene_name not in self._transition_callbacks:
            self._transition_callbacks[scene_name] = []
        self._transition_callbacks[scene_name].append(callback)

    def _trigger_transition(self, scene_name: str) -> None:
        """Trigger scene transition callbacks."""
        if scene_name in self._transition_callbacks:
            for callback in self._transition_callbacks[scene_name]:
                callback()

    def get_scene_count(self) -> int:
        """Get total number of scenes."""
        return len(self._scenes)

    def get_scene_names(self) -> List[str]:
        """Get all scene names."""
        return list(self._scenes.keys())

    def has_scene(self, name: str) -> bool:
        """Check if scene exists."""
        return name in self._scenes

    def reload_current_scene(self) -> bool:
        """Reload the current scene."""
        if not self._current_scene:
            return False

        # In a real implementation, this would reload the scene from disk
        self._trigger_transition(self._current_scene)
        return True

    def get_previous_scene(self) -> Optional[Scene]:
        """Get the previous scene."""
        if self._previous_scene:
            return self._scenes.get(self._previous_scene)
        return None

    def get_stack_depth(self) -> int:
        """Get current scene stack depth."""
        return len(self._scene_stack)
