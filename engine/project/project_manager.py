"""Project management and lifecycle."""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List


class ProjectMetadata:
    """Stores project metadata."""

    def __init__(self, name: str, path: str, version: str = "1.0.0"):
        self.name = name
        self.path = path
        self.version = version
        self.created = datetime.now().isoformat()
        self.modified = datetime.now().isoformat()
        self.last_opened: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            'name': self.name,
            'path': self.path,
            'version': self.version,
            'created': self.created,
            'modified': self.modified,
            'last_opened': self.last_opened
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectMetadata':
        """Create metadata from dictionary."""
        meta = cls(data['name'], data['path'], data['version'])
        meta.created = data['created']
        meta.modified = data['modified']
        meta.last_opened = data.get('last_opened')
        return meta


class ProjectManager:
    """Manages game projects: creation, loading, saving."""

    def __init__(self):
        self.current_project: Optional['GameProject'] = None
        self.recent_projects: List[str] = []

    def create_project(self, name: str, path: str) -> 'GameProject':
        """Create a new project."""
        from .project_initializer import ProjectInitializer

        project_path = Path(path) / name
        initializer = ProjectInitializer()
        initializer.create_project_structure(str(project_path), name)

        metadata = ProjectMetadata(name, str(project_path))
        project = GameProject(metadata)
        self.current_project = project
        self._add_to_recent(str(project_path))

        return project

    def open_project(self, path: str) -> 'GameProject':
        """Load an existing project."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Project not found: {path}")

        metadata_file = path / ".engine" / "metadata.json"
        if not metadata_file.exists():
            raise ValueError(f"Invalid project: {path}")

        with open(metadata_file, 'r') as f:
            data = json.load(f)

        metadata = ProjectMetadata.from_dict(data['metadata'])
        metadata.last_opened = datetime.now().isoformat()

        project = GameProject(metadata)
        self.current_project = project
        self._add_to_recent(str(path))

        return project

    def save_project(self, project: 'GameProject') -> None:
        """Save project metadata."""
        metadata_path = Path(project.path) / ".engine" / "metadata.json"
        metadata_path.parent.mkdir(parents=True, exist_ok=True)

        with open(metadata_path, 'w') as f:
            json.dump({'metadata': project.metadata.to_dict()}, f, indent=2)

    def _add_to_recent(self, path: str) -> None:
        """Add project to recent list."""
        if path in self.recent_projects:
            self.recent_projects.remove(path)
        self.recent_projects.insert(0, path)
        if len(self.recent_projects) > 10:
            self.recent_projects.pop()


class GameProject:
    """Represents a single game project."""

    def __init__(self, metadata: ProjectMetadata):
        self.metadata = metadata
        self.path = Path(metadata.path)
        self.config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load project configuration."""
        config_file = self.path / ".engine" / "config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                self.config = json.load(f)

    def save_config(self) -> None:
        """Save project configuration."""
        config_file = self.path / ".engine" / "config.json"
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def get_game_files_path(self) -> Path:
        """Get Game Files directory path."""
        return self.path / "Game Files"

    def get_kanban_path(self) -> Path:
        """Get .kanban directory path."""
        return self.path / ".kanban"

    def get_recovery_path(self) -> Path:
        """Get .recovery directory path."""
        return self.path / ".recovery"

    def get_logs_path(self) -> Path:
        """Get .logs directory path."""
        return self.path / ".logs"

    def get_engine_cache_path(self) -> Path:
        """Get .engine/cache directory path."""
        return self.path / ".engine" / "cache"
