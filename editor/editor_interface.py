# /**************************************************************************/
# /*  editor_interface.py                                                   */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Editor interface - Main API for editor plugins and tools.

Python port of Godot's editor interface with PySide6 integration.
"""

from typing import Optional, List, Dict, Any, Callable
from pathlib import Path

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QWidget, QMainWindow


class EditorInterface(QObject):
    """Main editor interface for plugins and tools.
    
    Provides access to all editor functionality including:
    - Scene tree manipulation
    - Inspector access
    - Selection management
    - Plugin callbacks
    """
    
    # Signals
    scene_changed = Signal()
    selection_changed = Signal()
    
    _instance: Optional['EditorInterface'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        super().__init__()
        self._selection: List[Any] = []
        self._plugin_callbacks: Dict[str, List[Callable]] = {}
        self._main_window: Optional[QMainWindow] = None
        
        self._initialized = True
    
    def set_main_window(self, window: QMainWindow) -> None:
        """Set the main editor window reference."""
        self._main_window = window
    
    def get_main_window(self) -> Optional[QMainWindow]:
        """Get the main editor window."""
        return self._main_window
    
    # Selection management
    def get_selection(self) -> List[Any]:
        """Get currently selected objects."""
        return list(self._selection)
    
    def add_selection(self, obj: Any) -> None:
        """Add object to selection."""
        if obj not in self._selection:
            self._selection.append(obj)
            self.selection_changed.emit()
    
    def remove_selection(self, obj: Any) -> None:
        """Remove object from selection."""
        if obj in self._selection:
            self._selection.remove(obj)
            self.selection_changed.emit()
    
    def clear_selection(self) -> None:
        """Clear all selection."""
        if self._selection:
            self._selection.clear()
            self.selection_changed.emit()
    
    def select_object(self, obj: Any) -> None:
        """Select single object."""
        self.clear_selection()
        self.add_selection(obj)
    
    # Inspector access
    def inspect_object(self, obj: Any) -> None:
        """Show object in inspector."""
        # TODO: Connect to inspector dock
        self.select_object(obj)
    
    def get_inspector(self) -> Optional[QWidget]:
        """Get inspector dock widget."""
        if self._main_window:
            # TODO: Find inspector dock by name
            return None
        return None
    
    # Scene tree access
    def get_scene_tree(self) -> Optional[QWidget]:
        """Get scene tree dock widget."""
        if self._main_window:
            # TODO: Find scene tree dock by name
            return None
        return None
    
    def get_file_system_dock(self) -> Optional[QWidget]:
        """Get file system dock widget."""
        if self._main_window:
            # TODO: Find file system dock by name
            return None
        return None
    
    # Plugin callbacks
    def add_plugin_callback(self, event: str, callback: Callable) -> None:
        """Add callback for plugin events."""
        if event not in self._plugin_callbacks:
            self._plugin_callbacks[event] = []
        self._plugin_callbacks[event].append(callback)
    
    def remove_plugin_callback(self, event: str, callback: Callable) -> None:
        """Remove plugin callback."""
        if event in self._plugin_callbacks:
            if callback in self._plugin_callbacks[event]:
                self._plugin_callbacks[event].remove(callback)
    
    def emit_plugin_event(self, event: str, *args, **kwargs) -> None:
        """Emit plugin event."""
        if event in self._plugin_callbacks:
            for callback in self._plugin_callbacks[event]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    print(f"Plugin callback error: {e}")
    
    # Resource management
    def get_edited_scene_root(self) -> Optional[Any]:
        """Get root node of currently edited scene."""
        # TODO: Connect to scene editor
        return None
    
    def open_scene_from_path(self, path: str) -> None:
        """Open scene from file path."""
        # TODO: Implement scene loading
        pass
    
    def save_scene_as(self, path: str) -> None:
        """Save current scene to path."""
        # TODO: Implement scene saving
        pass
    
    # Editor state
    def get_editor_scale(self) -> float:
        """Get current editor UI scale."""
        # TODO: Implement scale detection
        return 1.0
    
    def set_editor_scale(self, scale: float) -> None:
        """Set editor UI scale."""
        # TODO: Implement scale setting
        pass
    
    def is_playing_scene(self) -> bool:
        """Check if scene is currently playing."""
        # TODO: Connect to scene runner
        return False
    
    def play_scene(self) -> None:
        """Start playing current scene."""
        # TODO: Implement scene playback
        pass
    
    def stop_scene(self) -> None:
        """Stop scene playback."""
        # TODO: Implement scene stopping
        pass
    
    # Utility methods
    def get_resource_path(self) -> str:
        """Get current project resource path."""
        # TODO: Get from project settings
        return ""
    
    def get_selected_paths(self) -> List[str]:
        """Get file paths of selected items in file system dock."""
        # TODO: Connect to file system selection
        return []
    
    def import_file(self, path: str) -> None:
        """Import file into project."""
        # TODO: Connect to import system
        pass
    
    def __repr__(self) -> str:
        return f"EditorInterface(selection_count={len(self._selection)})"


# Global instance
_editor_interface: Optional[EditorInterface] = None


def get_editor_interface() -> EditorInterface:
    """Get the global editor interface instance."""
    global _editor_interface
    if _editor_interface is None:
        _editor_interface = EditorInterface()
    return _editor_interface
