"""Asset packaging and optimization."""

from pathlib import Path
from typing import List, Dict, Optional
import json


class AssetPackager:
    """Packages and optimizes game assets."""

    # Asset type configurations
    ASSET_TYPES = {
        'images': {
            'extensions': ['.png', '.jpg', '.jpeg', '.webp'],
            'compress': True
        },
        'audio': {
            'extensions': ['.wav', '.mp3', '.ogg'],
            'compress': True
        },
        'scripts': {
            'extensions': ['.py', '.gd', '.js'],
            'compress': False
        },
        'data': {
            'extensions': ['.json', '.yaml', '.xml'],
            'compress': True
        }
    }

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.assets_dir = self.project_path / "Game Files" / "assets"

    def scan_assets(self) -> Dict[str, List[Path]]:
        """Scan and categorize all assets."""
        assets = {}

        for asset_type, config in self.ASSET_TYPES.items():
            assets[asset_type] = []

            for ext in config['extensions']:
                for asset in self.assets_dir.rglob(f"*{ext}"):
                    assets[asset_type].append(asset)

        return assets

    def get_asset_sizes(self) -> Dict[str, Dict[str, int]]:
        """Get sizes of all assets."""
        assets = self.scan_assets()
        sizes = {}

        for asset_type, files in assets.items():
            type_size = 0
            file_sizes = {}

            for file_path in files:
                try:
                    file_size = file_path.stat().st_size
                    type_size += file_size
                    file_sizes[str(file_path.relative_to(self.project_path))] = file_size
                except OSError:
                    pass

            sizes[asset_type] = {
                'total_bytes': type_size,
                'total_mb': type_size / (1024 * 1024),
                'files': file_sizes
            }

        return sizes

    def find_unused_assets(self) -> List[Path]:
        """Find assets not referenced in scripts."""
        unused = []
        assets = self.scan_assets()

        # Get all file references
        referenced_files = self._find_referenced_files()

        for asset_type, files in assets.items():
            for file_path in files:
                if str(file_path) not in referenced_files:
                    unused.append(file_path)

        return unused

    def _find_referenced_files(self) -> set:
        """Find all referenced asset files in scripts."""
        referenced = set()
        scripts_dir = self.project_path / "Game Files" / "scripts"

        if not scripts_dir.exists():
            return referenced

        for script in scripts_dir.rglob("*.py"):
            try:
                with open(script, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # Simple pattern matching for asset references
                    for asset_type, files in self.scan_assets().items():
                        for asset in files:
                            if asset.name in content:
                                referenced.add(str(asset))
            except OSError:
                pass

        return referenced

    def generate_asset_manifest(self, output_path: str) -> None:
        """Generate asset manifest file."""
        assets = self.scan_assets()
        sizes = self.get_asset_sizes()

        manifest = {
            'assets': {},
            'statistics': {}
        }

        for asset_type, files in assets.items():
            manifest['assets'][asset_type] = [
                str(f.relative_to(self.project_path)) for f in files
            ]
            manifest['statistics'][asset_type] = sizes[asset_type]

        with open(output_path, 'w') as f:
            json.dump(manifest, f, indent=2)

    def get_largest_assets(self, limit: int = 10) -> List[tuple]:
        """Get largest assets by file size."""
        assets = self.scan_assets()
        all_assets = []

        for asset_type, files in assets.items():
            for file_path in files:
                try:
                    size = file_path.stat().st_size
                    all_assets.append((file_path, size, asset_type))
                except OSError:
                    pass

        # Sort by size descending
        all_assets.sort(key=lambda x: x[1], reverse=True)
        return all_assets[:limit]

    def estimate_download_time(self, bandwidth_mbps: float = 5.0) -> Dict[str, float]:
        """Estimate download times at given bandwidth."""
        sizes = self.get_asset_sizes()
        times = {}

        for asset_type, size_info in sizes.items():
            bytes_total = size_info['total_bytes']
            # Calculate time in seconds
            time_seconds = (bytes_total * 8) / (bandwidth_mbps * 1_000_000)
            times[asset_type] = time_seconds

        return times

    def optimize_asset_list(self, target_size_mb: float) -> List[Path]:
        """Find assets to optimize to reach target size."""
        current_size = sum(info['total_bytes'] for info in self.get_asset_sizes().values())
        current_size_mb = current_size / (1024 * 1024)

        if current_size_mb <= target_size_mb:
            return []

        # Find removable unused assets first
        removable = self.find_unused_assets()
        if removable:
            return removable

        # Otherwise suggest largest assets for optimization
        largest = self.get_largest_assets()
        to_optimize = []
        removed_size = 0

        for asset, size, _ in largest:
            if removed_size >= (current_size_mb - target_size_mb) * (1024 * 1024):
                break
            to_optimize.append(asset)
            removed_size += size

        return to_optimize
