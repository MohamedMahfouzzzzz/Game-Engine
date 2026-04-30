# /**************************************************************************/
# /*  editor_data.py                                                        */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Editor data management - Python port of Godot's EditorData.

Handles editor settings, recent projects, and persistent data.
"""

from typing import Dict, List, Any, Optional
import json
import os
from pathlib import Path


class EditorData:
    """Manages editor data and settings.
    
    Handles:
    - Editor configuration
    - Recent projects list
    - Plugin settings
    - Editor preferences
    """
    
    def __init__(self):
        self._settings: Dict[str, Any] = {}
        self._recent_projects: List[str] = []
        self._plugin_settings: Dict[str, Dict[str, Any]] = {}
        self._editor_preferences: Dict[str, Any] = {}
        
        self._config_path = Path.home() / ".game_engine" / "editor_settings.json"
        self._load_settings()
    
    def _load_settings(self) -> None:
        """Load settings from file."""
        try:
            if self._config_path.exists():
                with open(self._config_path, 'r') as f:
                    data = json.load(f)
                    self._settings = data.get('settings', {})
                    self._recent_projects = data.get('recent_projects', [])
                    self._plugin_settings = data.get('plugin_settings', {})
                    self._editor_preferences = data.get('editor_preferences', {})
        except Exception as e:
            print(f"Failed to load editor settings: {e}")
            self._reset_to_defaults()
    
    def _save_settings(self) -> None:
        """Save settings to file."""
        try:
            # Ensure config directory exists
            self._config_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'settings': self._settings,
                'recent_projects': self._recent_projects,
                'plugin_settings': self._plugin_settings,
                'editor_preferences': self._editor_preferences
            }
            
            with open(self._config_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Failed to save editor settings: {e}")
    
    def _reset_to_defaults(self) -> None:
        """Reset to default settings."""
        self._settings = {}
        self._recent_projects = []
        self._plugin_settings = {}
        self._editor_preferences = {
            'editor_scale': 1.0,
            'auto_save_interval': 300,  # 5 minutes
            'show_file_system_dock': True,
            'show_scene_tree_dock': True,
            'show_inspector_dock': True,
            'dock_layout': 'default'
        }
    
    # Settings management
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get editor setting value."""
        return self._settings.get(key, default)
    
    def set_setting(self, key: str, value: Any) -> None:
        """Set editor setting value."""
        self._settings[key] = value
        self._save_settings()
    
    def has_setting(self, key: str) -> bool:
        """Check if setting exists."""
        return key in self._settings
    
    # Recent projects
    def add_recent_project(self, project_path: str) -> None:
        """Add project to recent projects list."""
        if project_path in self._recent_projects:
            self._recent_projects.remove(project_path)
        
        self._recent_projects.insert(0, project_path)
        self._recent_projects = self._recent_projects[:10]  # Keep only 10
        self._save_settings()
    
    def get_recent_projects(self) -> List[str]:
        """Get recent projects list."""
        return list(self._recent_projects)
    
    def clear_recent_projects(self) -> None:
        """Clear recent projects list."""
        self._recent_projects.clear()
        self._save_settings()
    
    # Plugin settings
    def get_plugin_setting(self, plugin_name: str, key: str, default: Any = None) -> Any:
        """Get plugin-specific setting."""
        plugin_settings = self._plugin_settings.get(plugin_name, {})
        return plugin_settings.get(key, default)
    
    def set_plugin_setting(self, plugin_name: str, key: str, value: Any) -> None:
        """Set plugin-specific setting."""
        if plugin_name not in self._plugin_settings:
            self._plugin_settings[plugin_name] = {}
        
        self._plugin_settings[plugin_name][key] = value
        self._save_settings()
    
    # Editor preferences
    def get_editor_preference(self, key: str, default: Any = None) -> Any:
        """Get editor preference."""
        return self._editor_preferences.get(key, default)
    
    def set_editor_preference(self, key: str, value: Any) -> None:
        """Set editor preference."""
        self._editor_preferences[key] = value
        self._save_settings()
    
    def get_editor_scale(self) -> float:
        """Get editor UI scale."""
        return self.get_editor_preference('editor_scale', 1.0)
    
    def set_editor_scale(self, scale: float) -> None:
        """Set editor UI scale."""
        self.set_editor_preference('editor_scale', max(0.5, min(3.0, scale)))
    
    def get_auto_save_interval(self) -> int:
        """Get auto-save interval in seconds."""
        return self.get_editor_preference('auto_save_interval', 300)
    
    def set_auto_save_interval(self, seconds: int) -> None:
        """Set auto-save interval in seconds."""
        self.set_editor_preference('auto_save_interval', max(60, seconds))
    
    def is_dock_visible(self, dock_name: str) -> bool:
        """Check if dock should be visible."""
        return self.get_editor_preference(f'show_{dock_name}_dock', True)
    
    def set_dock_visible(self, dock_name: str, visible: bool) -> None:
        """Set dock visibility preference."""
        self.set_editor_preference(f'show_{dock_name}_dock', visible)
    
    # Utility methods
    def get_config_path(self) -> Path:
        """Get configuration file path."""
        return self._config_path
    
    def backup_settings(self, backup_path: str) -> bool:
        """Backup current settings to file."""
        try:
            with open(backup_path, 'w') as f:
                data = {
                    'settings': self._settings,
                    'recent_projects': self._recent_projects,
                    'plugin_settings': self._plugin_settings,
                    'editor_preferences': self._editor_preferences
                }
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Failed to backup settings: {e}")
            return False
    
    def restore_settings(self, backup_path: str) -> bool:
        """Restore settings from backup file."""
        try:
            with open(backup_path, 'r') as f:
                data = json.load(f)
                self._settings = data.get('settings', {})
                self._recent_projects = data.get('recent_projects', [])
                self._plugin_settings = data.get('plugin_settings', {})
                self._editor_preferences = data.get('editor_preferences', {})
                self._save_settings()
            return True
        except Exception as e:
            print(f"Failed to restore settings: {e}")
            return False
    
    def __repr__(self) -> str:
        return f"EditorData(recent_projects={len(self._recent_projects)}, settings={len(self._settings)})"
