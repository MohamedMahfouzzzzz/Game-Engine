"""Export and build management."""

from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import shutil
from datetime import datetime


class Platform(Enum):
    """Export platforms."""

    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"
    WEB = "web"
    ANDROID = "android"
    IOS = "ios"


@dataclass
class ExportConfig:
    """Export configuration."""

    project_path: str
    export_path: str
    platform: Platform
    optimize: bool = True
    compress: bool = True
    include_debug_symbols: bool = False
    version: str = "1.0.0"
    name: str = "GameProject"


class ExportManager:
    """Manages game exports and builds."""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.exports_dir = self.project_path / "tmp_exports"
        self.exports_dir.mkdir(parents=True, exist_ok=True)
        self.build_log: List[str] = []

    def export(self, config: ExportConfig) -> bool:
        """Export game for platform."""
        self.build_log.clear()
        self._log(f"Starting export for {config.platform.value}...")

        try:
            # Validate project
            if not self._validate_project():
                self._log("Project validation failed!")
                return False

            self._log("Project validated successfully")

            # Create export directory
            export_dir = Path(config.export_path) / f"Export_{config.platform.value}"
            export_dir.mkdir(parents=True, exist_ok=True)
            self._log(f"Created export directory: {export_dir}")

            # Bundle game files
            if not self._bundle_game_files(export_dir, config):
                self._log("Failed to bundle game files")
                return False

            # Copy engine executable (placeholder)
            if not self._copy_engine_executable(export_dir, config.platform):
                self._log("Failed to copy engine executable")
                return False

            # Generate manifest
            self._generate_manifest(export_dir, config)
            self._log("Generated export manifest")

            # Compress if requested
            if config.compress:
                if not self._create_archive(export_dir, config):
                    self._log("Failed to create archive")
                    return False

            self._log(f"Export completed successfully: {export_dir}")
            return True

        except Exception as e:
            self._log(f"Export failed with error: {e}")
            return False

    def _validate_project(self) -> bool:
        """Validate project structure."""
        required_dirs = [
            self.project_path / "Game Files",
            self.project_path / ".engine"
        ]

        for req_dir in required_dirs:
            if not req_dir.exists():
                self._log(f"Missing required directory: {req_dir}")
                return False

        return True

    def _bundle_game_files(self, export_dir: Path, config: ExportConfig) -> bool:
        """Copy and bundle game files."""
        try:
            game_files_src = self.project_path / "Game Files"
            game_files_dst = export_dir / "Game Files"

            if game_files_src.exists():
                # Copy entire Game Files directory
                shutil.copytree(
                    game_files_src,
                    game_files_dst,
                    dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns('*.tmp', '__pycache__')
                )
                self._log(f"Bundled Game Files: {game_files_dst}")
            else:
                self._log("Warning: Game Files directory not found")

            # Copy engine config
            engine_config_src = self.project_path / ".engine" / "config.json"
            if engine_config_src.exists():
                engine_dir = export_dir / ".engine"
                engine_dir.mkdir(exist_ok=True)
                shutil.copy2(engine_config_src, engine_dir / "config.json")

            return True

        except Exception as e:
            self._log(f"Error bundling game files: {e}")
            return False

    def _copy_engine_executable(self, export_dir: Path, platform: Platform) -> bool:
        """Copy platform-specific engine executable."""
        try:
            # Platform executable mapping
            exec_names = {
                Platform.WINDOWS: "game_engine.exe",
                Platform.LINUX: "game_engine",
                Platform.MACOS: "game_engine.app/Contents/MacOS/game_engine",
                Platform.WEB: "game_engine.js",
                Platform.ANDROID: "game_engine.apk",
                Platform.IOS: "game_engine.ipa"
            }

            exec_name = exec_names.get(platform, "game_engine")
            self._log(f"Platform executable: {exec_name}")

            # Create placeholder
            exec_path = export_dir / exec_name
            exec_path.parent.mkdir(parents=True, exist_ok=True)

            if not exec_path.exists():
                # Placeholder executable creation
                if platform == Platform.WEB:
                    exec_path.write_text("// Game Engine Web Build\n")
                else:
                    exec_path.touch()

                self._log(f"Created executable: {exec_path}")

            return True

        except Exception as e:
            self._log(f"Error copying executable: {e}")
            return False

    def _generate_manifest(self, export_dir: Path, config: ExportConfig) -> None:
        """Generate build manifest."""
        import json

        manifest = {
            'name': config.name,
            'version': config.version,
            'platform': config.platform.value,
            'exported_at': datetime.now().isoformat(),
            'optimized': config.optimize,
            'compressed': config.compress,
            'debug_symbols': config.include_debug_symbols,
            'files': []
        }

        # List bundled files
        for file_path in export_dir.rglob('*'):
            if file_path.is_file():
                rel_path = file_path.relative_to(export_dir)
                manifest['files'].append(str(rel_path))

        manifest_path = export_dir / "manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)

    def _create_archive(self, export_dir: Path, config: ExportConfig) -> bool:
        """Create compressed archive of export."""
        try:
            import zipfile

            archive_name = f"{config.name}_v{config.version}_{config.platform.value}"
            archive_path = export_dir.parent / f"{archive_name}.zip"

            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in export_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(export_dir.parent)
                        zipf.write(file_path, arcname)

            self._log(f"Created archive: {archive_path}")
            return True

        except Exception as e:
            self._log(f"Error creating archive: {e}")
            return False

    def _log(self, message: str) -> None:
        """Log build message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        self.build_log.append(log_msg)
        print(log_msg)

    def get_build_log(self) -> str:
        """Get build log as string."""
        return "\n".join(self.build_log)

    def export_all_platforms(self, export_base_path: str) -> Dict[Platform, bool]:
        """Export to all platforms."""
        results = {}

        for platform in Platform:
            config = ExportConfig(
                project_path=str(self.project_path),
                export_path=export_base_path,
                platform=platform
            )
            results[platform] = self.export(config)

        return results
