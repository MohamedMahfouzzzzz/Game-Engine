# /**************************************************************************/
# /*  settings.py                                                           */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Settings manager for the game engine."""

import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, Optional

import logging

logger = logging.getLogger(__name__)


@dataclass
class KeyBindings:
    """Keyboard shortcuts configuration."""
    new_project: str = "Ctrl+N"
    open_project: str = "Ctrl+O"
    save_project: str = "Ctrl+S"
    undo: str = "Ctrl+Z"
    redo: str = "Ctrl+Y"
    play: str = "F5"
    pause: str = "F6"
    stop: str = "F7"
    delete: str = "Delete"
    duplicate: str = "Ctrl+D"


@dataclass
class ThemeSettings:
    """Theme configuration."""
    name: str = "dark"
    accent_color: str = "#00bcd4"
    background_color: str = "#2a2a2a"
    foreground_color: str = "#ffffff"
    grid_color: str = "#505050"
    selection_color: str = "#00ffff"


@dataclass
class EditorSettings:
    """Editor-specific settings."""
    auto_save: bool = True
    auto_save_interval: int = 300  # seconds
    show_grid: bool = True
    grid_size: int = 32
    snap_to_grid: bool = False
    default_zoom: float = 1.0
    max_console_lines: int = 10000
    show_gizmos: bool = True


@dataclass
class RuntimeSettings:
    """Runtime/game settings."""
    target_fps: int = 60
    vsync: bool = True
    fixed_timestep: bool = True
    max_physics_steps: int = 8


@dataclass
class Settings:
    """Main settings container."""
    version: str = "1.0.0"
    key_bindings: KeyBindings = field(default_factory=KeyBindings)
    theme: ThemeSettings = field(default_factory=ThemeSettings)
    editor: EditorSettings = field(default_factory=EditorSettings)
    runtime: RuntimeSettings = field(default_factory=RuntimeSettings)
    custom: Dict[str, Any] = field(default_factory=dict)

    _instance: Optional["Settings"] = None
    _config_path: Optional[Path] = None

    @classmethod
    def get_instance(cls) -> "Settings":
        """Get singleton settings instance."""
        if cls._instance is None:
            cls._instance = cls.load()
        return cls._instance

    @classmethod
    def load(cls, path: Optional[Path] = None) -> "Settings":
        """Load settings from file."""
        if path is None:
            path = cls._get_default_path()

        cls._config_path = path

        if not path.exists():
            return cls()  # Return defaults

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls._from_dict(data)
        except (json.JSONDecodeError, KeyError, TypeError):
            return cls()  # Return defaults on error

    def save(self, path: Optional[Path] = None) -> None:
        """Save settings to file."""
        if path is None:
            path = self._config_path or self._get_default_path()

        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2)

    @classmethod
    def _get_default_path(cls) -> Path:
        """Get default configuration file path."""
        # Use user config directory
        config_dir = Path.home() / ".config" / "game_engine_studio"
        if os.name == "nt":  # Windows
            config_dir = Path(os.environ.get("APPDATA", Path.home() / "AppData/Roaming")) / "GameEngineStudio"
        return config_dir / "settings.json"

    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> "Settings":
        """Create Settings from dictionary."""
        settings = cls(version=data.get("version", "1.0.0"))

        if "key_bindings" in data:
            settings.key_bindings = KeyBindings(**data["key_bindings"])
        if "theme" in data:
            settings.theme = ThemeSettings(**data["theme"])
        if "editor" in data:
            settings.editor = EditorSettings(**data["editor"])
        if "runtime" in data:
            settings.runtime = RuntimeSettings(**data["runtime"])
        if "custom" in data:
            settings.custom = data["custom"]

        return settings

    def get(self, key: str, default: Any = None) -> Any:
        """Get a custom setting value."""
        return self.custom.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a custom setting value."""
        self.custom[key] = value

    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults."""
        self.key_bindings = KeyBindings()
        self.theme = ThemeSettings()
        self.editor = EditorSettings()
        self.runtime = RuntimeSettings()
        self.custom = {}


def get_settings() -> Settings:
    """Get the global settings instance."""
    return Settings.get_instance()
