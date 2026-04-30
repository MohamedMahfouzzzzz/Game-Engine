# /**************************************************************************/
# /*  build_pipeline.py                                                     */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set
import json
import shutil
import zipfile
import hashlib
from datetime import datetime, timezone

import logging


logger = logging.getLogger(__name__)



@dataclass
class ExportProfile:
    target: str
    output_name: str
    optimize_assets: bool = True


class BuildPipeline:
    """Unified export pipeline for all targets."""

    # Files and directories to exclude from distribution
    EXCLUDE_PATTERNS: Set[str] = {
        # Development tools
        "tools/dev_ide",
        "tools/pixel_art_editor",  # Optional: keep if needed in runtime
        
        # Tests
        "tests",
        "test",
        "*_test.py",
        "test_*.py",
        "conftest.py",
        "pytest.ini",
        
        # Documentation (MD files)
        "*.md",
        "docs",
        "documentation",
        "README*",
        "CHANGELOG*",
        "LICENSE*",
        "CONTRIBUTING*",
        
        # Config files for development
        ".github",
        ".gitignore",
        ".gitattributes",
        ".editorconfig",
        "pyproject.toml",
        "setup.py",
        "requirements-dev.txt",
        
        # Cache and temp
        "__pycache__",
        "*.pyc",
        "*.pyo",
        "*.egg-info",
        ".pytest_cache",
        ".mypy_cache",
        ".coverage",
        "*.log",
        
        # IDE files
        ".vscode",
        ".idea",
        "*.swp",
        "*.swo",
        ".windsurf",
        
        # Other dev files
        "plans",
        "notes",
        "todo.txt",
    }

    def _should_exclude(self, path: Path, root: Path) -> bool:
        """Check if a file should be excluded from distribution."""
        relative = path.relative_to(root)
        path_str = str(relative).replace("\\", "/")
        
        for pattern in self.EXCLUDE_PATTERNS:
            # Check if path matches pattern
            if pattern in path_str:
                return True
            # Check filename for glob patterns
            if pattern.startswith("*") and path.name.endswith(pattern[1:]):
                return True
            if pattern.endswith("*") and path.name.startswith(pattern[:-1]):
                return True
            # Exact filename match
            if path.name == pattern or path.name.lower() == pattern.lower():
                return True
        
        return False

    def build(self, project_name: str, output_dir: str, profile: ExportProfile, project_file: Optional[str] = None) -> str:
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        bundle_dir = out_dir / profile.output_name
        bundle_dir.mkdir(parents=True, exist_ok=True)

        runtime_dir = bundle_dir / "runtime"
        data_dir = bundle_dir / "data"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        data_dir.mkdir(parents=True, exist_ok=True)

        # Minimal runtime entrypoint (python-based for now)
        (runtime_dir / "run_game.py").write_text(
            "from runtime.game_loop import GameRuntime\n"
            "from ui.actions.project_io import load_project\n"
            "import sys\n\n"
            "def main():\n"
            "    project_path = sys.argv[1] if len(sys.argv) > 1 else 'data/project.gep'\n"
            "    project = load_project(project_path)\n"
            "    GameRuntime(project).run()\n\n"
            "if __name__ == '__main__':\n"
            "    main()\n",
            encoding="utf-8",
        )
        (bundle_dir / "run_windows.bat").write_text(
            "@echo off\npython runtime\\run_game.py data\\project.gep\n",
            encoding="utf-8",
        )
        (bundle_dir / "run_unix.sh").write_text(
            "#!/usr/bin/env sh\npython3 runtime/run_game.py data/project.gep\n",
            encoding="utf-8",
        )

        if project_file:
            shutil.copy2(project_file, data_dir / "project.gep")

        manifest = {
            "project": project_name,
            "target": profile.target,
            "output_name": profile.output_name,
            "assets_optimized": profile.optimize_assets,
            "bundle_dir": str(bundle_dir),
            "runtime_entry": str(runtime_dir / "run_game.py"),
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
        }
        manifest_path = bundle_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        self._write_checksums(bundle_dir)

        zip_path = out_dir / f"{profile.output_name}.zip"
        self._zip_dir(bundle_dir, zip_path)
        return str(zip_path)

    def build_all(self, project_name: str, output_dir: str, targets: List[str]) -> Dict[str, str]:
        return {
            target: self.build(project_name, output_dir, ExportProfile(target=target, output_name=f"{project_name}_{target}"))
            for target in targets
        }

    def _zip_dir(self, folder: Path, zip_path: Path, source_root: Optional[Path] = None) -> None:
        """Zip directory with exclusion filtering."""
        if zip_path.exists():
            zip_path.unlink()
        
        root = source_root or folder
        
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for path in folder.rglob("*"):
                if path.is_file() and not self._should_exclude(path, root):
                    zf.write(path, arcname=path.relative_to(folder))

    def _write_checksums(self, folder: Path) -> None:
        lines: List[str] = []
        for path in sorted(folder.rglob("*")):
            if path.is_file():
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                lines.append(f"{digest}  {path.relative_to(folder).as_posix()}")
        (folder / "checksums.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")
