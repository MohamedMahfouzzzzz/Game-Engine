"""Automated project creation and structure setup."""

import json
from pathlib import Path
from typing import Dict, Any


class ProjectInitializer:
    """Handles automated project creation workflow."""

    # Default project template structure
    DEFAULT_TEMPLATE = {
        'directories': [
            '.kanban',
            '.engine/cache',
            '.engine/migrations',
            'Game Files/scenes',
            'Game Files/assets',
            'Game Files/scripts',
            'Game Files/data',
            '.recovery',
            '.logs'
        ],
        'files': {
            '.kanban/boards.json': {'boards': []},
            '.kanban/tasks.json': {'tasks': []},
            '.engine/metadata.json': {
                'metadata': {
                    'name': '',
                    'path': '',
                    'version': '1.0.0',
                    'created': '',
                    'modified': '',
                    'last_opened': None
                }
            },
            '.engine/config.json': {
                'engine': {
                    'target_fps': 60,
                    'vsync': True,
                    'window_width': 1024,
                    'window_height': 768
                },
                'features': {
                    'enable_encryption': True,
                    'enable_database': True,
                    'enable_telemetry': True,
                    'auto_save_interval': 300
                }
            },
            '.engine/schema.sql': '',
            'Game Files/.gitkeep': '',
            '.logs/.gitkeep': '',
            '.recovery/.gitkeep': ''
        }
    }

    def create_project_structure(self, project_path: str, project_name: str) -> None:
        """Create a new project with standard folder structure."""
        base_path = Path(project_path)
        base_path.mkdir(parents=True, exist_ok=True)

        # Create directories
        for directory in self.DEFAULT_TEMPLATE['directories']:
            dir_path = base_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)

        # Create files
        for file_path, content in self.DEFAULT_TEMPLATE['files'].items():
            full_path = base_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)

            if content:
                # Update metadata with actual values
                if 'metadata' in file_path:
                    from datetime import datetime
                    content['metadata']['name'] = project_name
                    content['metadata']['path'] = str(base_path)
                    content['metadata']['created'] = datetime.now().isoformat()
                    content['metadata']['modified'] = datetime.now().isoformat()

                # Write JSON files
                if file_path.endswith('.json'):
                    with open(full_path, 'w') as f:
                        json.dump(content, f, indent=2)
            else:
                # Create empty files (like .gitkeep)
                full_path.touch()

        # Create initial database schema
        self._create_initial_schema(base_path)

    def _create_initial_schema(self, project_path: Path) -> None:
        """Create initial database schema file."""
        schema_file = project_path / ".engine" / "schema.sql"

        schema_sql = """-- Game Engine Database Schema

CREATE TABLE IF NOT EXISTS games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS save_slots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER NOT NULL,
    slot_number INTEGER NOT NULL,
    save_data BLOB NOT NULL,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
    UNIQUE(game_id, slot_number)
);

CREATE TABLE IF NOT EXISTS entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER NOT NULL,
    entity_id TEXT NOT NULL,
    entity_type TEXT,
    data BLOB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS telemetry_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER,
    event_type TEXT NOT NULL,
    event_data TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    severity TEXT DEFAULT 'INFO'
);

CREATE TABLE IF NOT EXISTS performance_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER,
    metric_name TEXT NOT NULL,
    metric_value REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_save_slots_game ON save_slots(game_id);
CREATE INDEX IF NOT EXISTS idx_entities_game ON entities(game_id);
CREATE INDEX IF NOT EXISTS idx_telemetry_game ON telemetry_events(game_id);
CREATE INDEX IF NOT EXISTS idx_telemetry_type ON telemetry_events(event_type);
CREATE INDEX IF NOT EXISTS idx_metrics_game ON performance_metrics(game_id);
"""

        with open(schema_file, 'w') as f:
            f.write(schema_sql)

    def update_project_structure(self, project_path: str) -> None:
        """Update existing project with new structure components."""
        base_path = Path(project_path)

        # Add missing directories
        for directory in self.DEFAULT_TEMPLATE['directories']:
            dir_path = base_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)

        # Add missing files
        for file_path, content in self.DEFAULT_TEMPLATE['files'].items():
            full_path = base_path / file_path
            if not full_path.exists():
                full_path.parent.mkdir(parents=True, exist_ok=True)
                if content and file_path.endswith('.json'):
                    with open(full_path, 'w') as f:
                        json.dump(content, f, indent=2)
                else:
                    full_path.touch()
