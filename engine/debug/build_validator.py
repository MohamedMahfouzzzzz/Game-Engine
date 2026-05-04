"""Build validation before export."""

from pathlib import Path
from typing import List, Dict, Tuple
from .global_debugger import GlobalDebugger, DebugReport, ErrorLevel


class BuildValidator:
    """Validates project before building."""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.debugger = GlobalDebugger(str(project_path))
        self.validation_results: List[Tuple[str, bool]] = []

    def validate_for_build(self) -> Tuple[bool, DebugReport]:
        """Run all build validation checks."""
        report = self.debugger.debug_project()

        # Perform additional build-specific checks
        self._check_build_requirements(report)
        self._check_export_readiness(report)

        return not report.has_critical(), report

    def _check_build_requirements(self, report: DebugReport) -> None:
        """Check build requirements."""
        # Check for main entry point
        main_script = self.project_path / "Game Files" / "scripts" / "main.py"
        if not main_script.exists():
            report.add_message({
                'level': ErrorLevel.WARNING,
                'category': 'build',
                'message': 'No main.py entry point found',
                'file_path': str(main_script),
                'suggested_fix': 'Create main.py in Game Files/scripts'
            })

    def _check_export_readiness(self, report: DebugReport) -> None:
        """Check if project is ready for export."""
        # Check game files directory has content
        game_files = self.project_path / "Game Files"
        if game_files.exists():
            children = list(game_files.iterdir())
            if len(children) < 2:
                report.add_message({
                    'level': ErrorLevel.INFO,
                    'category': 'export',
                    'message': 'Game Files directory has minimal content',
                    'suggested_fix': 'Add scenes, assets, and scripts'
                })

    def check_build_errors_only(self) -> bool:
        """Quick check for build-blocking errors."""
        report = self.debugger.debug_project()
        return not report.has_errors()

    def get_build_blockers(self) -> List[str]:
        """Get list of build-blocking issues."""
        _, report = self.validate_for_build()
        blockers = []

        for msg in report.get_messages_by_level(ErrorLevel.CRITICAL):
            blockers.append(f"[{msg.category.upper()}] {msg.message}")

        for msg in report.get_messages_by_level(ErrorLevel.ERROR):
            blockers.append(f"[{msg.category.upper()}] {msg.message}")

        return blockers

    def print_validation_report(self) -> None:
        """Print validation report."""
        can_build, report = self.validate_for_build()

        report.print_details()

        print("\n" + "=" * 60)
        if can_build:
            print("✓ Project is ready to build!")
        else:
            blockers = self.get_build_blockers()
            print("✗ Project has build-blocking issues:")
            for blocker in blockers:
                print(f"  - {blocker}")
        print("=" * 60 + "\n")
