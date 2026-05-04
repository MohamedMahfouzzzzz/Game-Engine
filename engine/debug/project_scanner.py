"""Project scanning and analysis."""

from pathlib import Path
from typing import Dict, List, Set, Optional
import json


class ProjectScanner:
    """Scans and analyzes project structure."""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)

    def scan_all_files(self) -> Dict[str, List[Path]]:
        """Scan all project files by type."""
        files = {
            'scripts': [],
            'assets': [],
            'scenes': [],
            'data': [],
            'config': [],
            'other': []
        }

        for file_path in self.project_path.rglob('*'):
            if file_path.is_file():
                suffix = file_path.suffix.lower()

                if suffix == '.py':
                    files['scripts'].append(file_path)
                elif suffix in ['.png', '.jpg', '.jpeg', '.webp', '.gif']:
                    files['assets'].append(file_path)
                elif suffix == '.json' and 'scenes' in str(file_path):
                    files['scenes'].append(file_path)
                elif suffix in ['.json', '.yaml', '.xml']:
                    files['data'].append(file_path)
                elif suffix in ['.json', '.yml']:
                    files['config'].append(file_path)
                else:
                    files['other'].append(file_path)

        return files

    def find_broken_references(self) -> List[Dict[str, str]]:
        """Find broken file references."""
        broken = []
        files = self.scan_all_files()

        # Check references in scripts
        for script in files['scripts']:
            try:
                with open(script, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # Simple reference pattern matching
                    import re
                    refs = re.findall(r'["\'](.*?)["\']', content)

                    for ref in refs:
                        ref_path = self.project_path / ref
                        if not ref_path.exists() and '/' in ref:
                            broken.append({
                                'file': str(script),
                                'broken_ref': ref,
                                'type': 'asset_reference'
                            })
            except Exception:
                pass

        return broken

    def get_statistics(self) -> Dict[str, any]:
        """Get project statistics."""
        files = self.scan_all_files()

        total_files = sum(len(f) for f in files.values())
        total_size = sum(
            sum(f.stat().st_size for f in file_list if f.exists())
            for file_list in files.values()
        )

        return {
            'total_files': total_files,
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'by_type': {k: len(v) for k, v in files.items()},
            'broken_references': len(self.find_broken_references())
        }

    def find_duplicate_files(self) -> List[tuple]:
        """Find duplicate files by content hash."""
        import hashlib

        hashes = {}
        duplicates = []

        for file_path in self.project_path.rglob('*'):
            if file_path.is_file():
                try:
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()

                    if file_hash in hashes:
                        duplicates.append((hashes[file_hash], file_path))
                    else:
                        hashes[file_hash] = file_path
                except Exception:
                    pass

        return duplicates

    def find_large_files(self, min_size_mb: float = 10.0) -> List[tuple]:
        """Find large files in project."""
        large_files = []
        min_bytes = int(min_size_mb * 1024 * 1024)

        for file_path in self.project_path.rglob('*'):
            if file_path.is_file():
                size = file_path.stat().st_size
                if size > min_bytes:
                    size_mb = size / (1024 * 1024)
                    large_files.append((file_path, size_mb))

        return sorted(large_files, key=lambda x: x[1], reverse=True)

    def find_empty_directories(self) -> List[Path]:
        """Find empty directories."""
        empty_dirs = []

        for dir_path in self.project_path.rglob('*'):
            if dir_path.is_dir():
                if not any(dir_path.iterdir()):
                    empty_dirs.append(dir_path)

        return empty_dirs

    def get_file_report(self) -> str:
        """Generate file report."""
        stats = self.get_statistics()

        report = [
            "=== PROJECT FILE REPORT ===",
            f"Total Files: {stats['total_files']}",
            f"Total Size: {stats['total_size_mb']:.2f} MB",
            "",
            "Files by Type:",
        ]

        for file_type, count in stats['by_type'].items():
            report.append(f"  {file_type}: {count}")

        report.append(f"\nBroken References: {stats['broken_references']}")

        large_files = self.find_large_files(5.0)
        if large_files:
            report.append("\nLarge Files (> 5MB):")
            for file_path, size_mb in large_files[:10]:
                rel_path = file_path.relative_to(self.project_path)
                report.append(f"  {rel_path}: {size_mb:.2f} MB")

        return "\n".join(report)
