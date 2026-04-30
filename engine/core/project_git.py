"""Git integration for engine projects."""

from __future__ import annotations

import subprocess
from pathlib import Path


class ProjectGit:
    """Best-effort Git wrapper used by project creation/saves."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    def is_available(self) -> bool:
        try:
            subprocess.run(["git", "--version"], check=True, capture_output=True, text=True)
            return True
        except (OSError, subprocess.CalledProcessError):
            return False

    def is_repo(self) -> bool:
        return (self.root / ".git").exists()

    def init(self) -> bool:
        if not self.is_available():
            return False
        self.root.mkdir(parents=True, exist_ok=True)
        if not self.is_repo():
            subprocess.run(["git", "init"], cwd=self.root, check=True, capture_output=True, text=True)
        self._ensure_gitignore()
        return True

    def snapshot(self, message: str) -> bool:
        if not self.is_available() or not self.is_repo():
            return False
        subprocess.run(["git", "add", "."], cwd=self.root, check=True, capture_output=True, text=True)
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
        )
        if not status.stdout.strip():
            return False
        subprocess.run(
            ["git", "-c", "user.name=Game Engine Studio", "-c", "user.email=engine.local@example.invalid", "commit", "-m", message],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
        )
        return True

    def _ensure_gitignore(self) -> None:
        ignore_path = self.root / ".gitignore"
        entries = {".engine_cache/", "__pycache__/", "*.pyc", ".backups/", "*.tmp"}
        existing = set()
        if ignore_path.exists():
            existing = {line.strip() for line in ignore_path.read_text(encoding="utf-8").splitlines()}
        missing = [entry for entry in sorted(entries) if entry not in existing]
        if missing:
            with open(ignore_path, "a", encoding="utf-8") as handle:
                if existing:
                    handle.write("\n")
                handle.write("\n".join(missing) + "\n")
