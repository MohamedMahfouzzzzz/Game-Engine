"""Small project cache for editor/runtime acceleration."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict


class ProjectCache:
    """Persist lightweight project metadata under ``.engine_cache``."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.cache_dir = self.root / ".engine_cache"
        self.cache_file = self.cache_dir / "project_cache.json"
        self._data: Dict[str, Any] = {}

    def load(self) -> Dict[str, Any]:
        if self.cache_file.exists():
            try:
                self._data = json.loads(self.cache_file.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                self._data = {}
        return self._data

    def save(self) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        payload = {**self._data, "updated_at": time.time()}
        self.cache_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self._data = payload

    def update_project(self, project: Any, project_file: str | Path = "") -> None:
        active_scene = getattr(project, "active_scene", None)
        self._data.update({
            "project_name": getattr(project, "name", ""),
            "project_file": str(project_file),
            "scene_count": len(getattr(project, "scenes", {})),
            "active_scene": getattr(active_scene, "name", None),
            "asset_count": len(getattr(project, "assets", {})),
        })
        self.save()

    def invalidate(self) -> None:
        self._data.clear()
        if self.cache_file.exists():
            self.cache_file.unlink()
