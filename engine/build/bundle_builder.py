"""Game bundle builder."""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Optional
import json


class BundleBuilder:
    """Builds game bundles with engine and assets."""

    def __init__(self, project_path: str, output_dir: str):
        self.project_path = Path(project_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def build_bundle(self, bundle_name: str, include_sources: bool = False) -> Path:
        """Build game bundle."""
        bundle_path = self.output_dir / bundle_name
        bundle_path.mkdir(parents=True, exist_ok=True)

        # Copy Game Files
        game_files_src = self.project_path / "Game Files"
        game_files_dst = bundle_path / "Game Files"

        if game_files_src.exists():
            shutil.copytree(
                game_files_src,
                game_files_dst,
                dirs_exist_ok=True,
                ignore=shutil.ignore_patterns('*.tmp', '.DS_Store')
            )

        # Copy engine executable (placeholder)
        self._copy_engine(bundle_path)

        # Copy config
        self._copy_config(bundle_path)

        # Create bundle metadata
        self._create_bundle_metadata(bundle_path)

        return bundle_path

    def build_minimal_bundle(self, bundle_name: str) -> Path:
        """Build minimal bundle without debug files."""
        bundle_path = self.output_dir / bundle_name
        bundle_path.mkdir(parents=True, exist_ok=True)

        game_files_src = self.project_path / "Game Files"
        game_files_dst = bundle_path / "Game Files"

        if game_files_src.exists():
            # Only copy essential asset directories
            for asset_type in ['scenes', 'assets', 'scripts']:
                src = game_files_src / asset_type
                if src.exists():
                    dst = game_files_dst / asset_type
                    shutil.copytree(src, dst, dirs_exist_ok=True)

        self._copy_engine(bundle_path)
        self._create_bundle_metadata(bundle_path)

        return bundle_path

    def build_portable_bundle(self, bundle_name: str) -> Path:
        """Build portable bundle (no external dependencies)."""
        bundle_path = self.output_dir / bundle_name
        bundle_path.mkdir(parents=True, exist_ok=True)

        # Copy all game files
        game_files_src = self.project_path / "Game Files"
        game_files_dst = bundle_path / "Game Files"

        if game_files_src.exists():
            shutil.copytree(game_files_src, game_files_dst, dirs_exist_ok=True)

        # Copy engine with all dependencies
        self._copy_engine(bundle_path, include_deps=True)

        # Create portable manifest
        self._create_portable_manifest(bundle_path)

        return bundle_path

    def _copy_engine(self, bundle_path: Path, include_deps: bool = False) -> None:
        """Copy engine files to bundle."""
        engine_dir = bundle_path / ".engine"
        engine_dir.mkdir(parents=True, exist_ok=True)

        # Copy engine config
        config_src = self.project_path / ".engine" / "config.json"
        if config_src.exists():
            shutil.copy2(config_src, engine_dir / "config.json")

        # Create engine executable placeholder
        if hasattr(os, 'name'):
            if os.name == 'nt':
                exec_file = bundle_path / "game_engine.exe"
            else:
                exec_file = bundle_path / "game_engine"
            exec_file.touch()

    def _copy_config(self, bundle_path: Path) -> None:
        """Copy configuration files."""
        config_dir = self.project_path / ".engine"
        if config_dir.exists():
            engine_dir = bundle_path / ".engine"
            engine_dir.mkdir(parents=True, exist_ok=True)

            for config_file in config_dir.glob("*.json"):
                shutil.copy2(config_file, engine_dir / config_file.name)

    def _create_bundle_metadata(self, bundle_path: Path) -> None:
        """Create bundle metadata file."""
        from datetime import datetime

        metadata = {
            'created_at': datetime.now().isoformat(),
            'project': self.project_path.name,
            'bundle_type': 'full',
            'files': self._list_bundle_files(bundle_path)
        }

        meta_path = bundle_path / "bundle_metadata.json"
        with open(meta_path, 'w') as f:
            json.dump(metadata, f, indent=2)

    def _create_portable_manifest(self, bundle_path: Path) -> None:
        """Create portable bundle manifest."""
        from datetime import datetime

        manifest = {
            'created_at': datetime.now().isoformat(),
            'portable': True,
            'self_contained': True,
            'requires_external_deps': False,
            'files': self._list_bundle_files(bundle_path)
        }

        manifest_path = bundle_path / "portable_manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)

    def _list_bundle_files(self, bundle_path: Path) -> List[str]:
        """List all files in bundle."""
        files = []
        for file_path in bundle_path.rglob('*'):
            if file_path.is_file():
                rel_path = file_path.relative_to(bundle_path)
                files.append(str(rel_path))
        return sorted(files)

    def get_bundle_size(self, bundle_path: Path) -> int:
        """Get total size of bundle in bytes."""
        total = 0
        for file_path in bundle_path.rglob('*'):
            if file_path.is_file():
                total += file_path.stat().st_size
        return total

    def get_bundle_stats(self, bundle_path: Path) -> Dict[str, any]:
        """Get bundle statistics."""
        total_size = self.get_bundle_size(bundle_path)
        file_count = len(list(bundle_path.rglob('*')))

        return {
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'file_count': file_count,
            'created_at': bundle_path.stat().st_ctime
        }
