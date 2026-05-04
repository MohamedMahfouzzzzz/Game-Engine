"""Global debugger for project-wide validation."""

import json
from enum import Enum
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime


class ErrorLevel(Enum):
    """Error severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class DebugMessage:
    """Single debug message."""

    level: ErrorLevel
    category: str
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    suggested_fix: Optional[str] = None
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'level': self.level.value,
            'category': self.category,
            'message': self.message,
            'file_path': self.file_path,
            'line_number': self.line_number,
            'suggested_fix': self.suggested_fix,
            'timestamp': self.timestamp
        }


class DebugReport:
    """Comprehensive debug report."""

    def __init__(self, project_name: str):
        self.project_name = project_name
        self.created_at = datetime.now().isoformat()
        self.messages: List[DebugMessage] = []
        self.summary = {
            'total': 0,
            'info': 0,
            'warning': 0,
            'error': 0,
            'critical': 0
        }

    def add_message(self, message: DebugMessage) -> None:
        """Add debug message."""
        self.messages.append(message)
        self.summary['total'] += 1
        self.summary[message.level.value] += 1

    def has_errors(self) -> bool:
        """Check if report has errors."""
        return self.summary['error'] > 0 or self.summary['critical'] > 0

    def has_critical(self) -> bool:
        """Check if report has critical errors."""
        return self.summary['critical'] > 0

    def get_messages_by_level(self, level: ErrorLevel) -> List[DebugMessage]:
        """Get messages by level."""
        return [m for m in self.messages if m.level == level]

    def get_messages_by_category(self, category: str) -> List[DebugMessage]:
        """Get messages by category."""
        return [m for m in self.messages if m.category == category]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'project_name': self.project_name,
            'created_at': self.created_at,
            'summary': self.summary,
            'messages': [m.to_dict() for m in self.messages]
        }

    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps(self.to_dict(), indent=2)

    def print_summary(self) -> None:
        """Print report summary."""
        print(f"\n{'=' * 60}")
        print(f"Debug Report: {self.project_name}")
        print(f"{'=' * 60}")
        print(f"Total Issues: {self.summary['total']}")
        print(f"  Info:     {self.summary['info']}")
        print(f"  Warning:  {self.summary['warning']}")
        print(f"  Error:    {self.summary['error']}")
        print(f"  Critical: {self.summary['critical']}")
        print(f"{'=' * 60}\n")

    def print_details(self) -> None:
        """Print detailed report."""
        self.print_summary()

        for level in [ErrorLevel.CRITICAL, ErrorLevel.ERROR, ErrorLevel.WARNING]:
            messages = self.get_messages_by_level(level)
            if messages:
                print(f"\n{level.value.upper()}S:")
                for msg in messages:
                    print(f"  [{msg.category}] {msg.message}")
                    if msg.file_path:
                        print(f"    File: {msg.file_path}:{msg.line_number or 'N/A'}")
                    if msg.suggested_fix:
                        print(f"    Suggestion: {msg.suggested_fix}")


class GlobalDebugger:
    """Global project debugger."""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.report: Optional[DebugReport] = None

    def debug_project(self) -> DebugReport:
        """Run comprehensive project debug."""
        self.report = DebugReport(self.project_path.name)

        # Run all checks
        self._check_project_structure()
        self._check_scripts()
        self._check_assets()
        self._check_config()
        self._check_scenes()
        self._check_dependencies()

        return self.report

    def _check_project_structure(self) -> None:
        """Check project structure."""
        required_dirs = [
            "Game Files",
            ".engine",
            ".kanban",
            ".recovery",
            ".logs"
        ]

        for dir_name in required_dirs:
            dir_path = self.project_path / dir_name
            if not dir_path.exists():
                self.report.add_message(DebugMessage(
                    level=ErrorLevel.WARNING,
                    category="structure",
                    message=f"Missing directory: {dir_name}",
                    file_path=str(self.project_path),
                    suggested_fix=f"Create {dir_name} directory"
                ))

    def _check_scripts(self) -> None:
        """Check script files for errors."""
        scripts_dir = self.project_path / "Game Files" / "scripts"
        if not scripts_dir.exists():
            self.report.add_message(DebugMessage(
                level=ErrorLevel.WARNING,
                category="scripts",
                message="No scripts directory found"
            ))
            return

        for script in scripts_dir.rglob("*.py"):
            try:
                with open(script, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self._check_python_syntax(script, content)
            except Exception as e:
                self.report.add_message(DebugMessage(
                    level=ErrorLevel.ERROR,
                    category="scripts",
                    message=f"Error reading script: {e}",
                    file_path=str(script)
                ))

    def _check_python_syntax(self, file_path: Path, content: str) -> None:
        """Check Python file syntax."""
        try:
            compile(content, str(file_path), 'exec')
        except SyntaxError as e:
            self.report.add_message(DebugMessage(
                level=ErrorLevel.ERROR,
                category="scripts",
                message=f"Syntax error: {e.msg}",
                file_path=str(file_path),
                line_number=e.lineno,
                suggested_fix=f"Fix syntax error on line {e.lineno}"
            ))

    def _check_assets(self) -> None:
        """Check asset files."""
        assets_dir = self.project_path / "Game Files" / "assets"
        if not assets_dir.exists():
            self.report.add_message(DebugMessage(
                level=ErrorLevel.INFO,
                category="assets",
                message="No assets directory found"
            ))
            return

        # Check for broken references
        for asset in assets_dir.rglob("*"):
            if asset.is_file():
                if not asset.stat().st_size:
                    self.report.add_message(DebugMessage(
                        level=ErrorLevel.WARNING,
                        category="assets",
                        message=f"Empty asset file: {asset.name}",
                        file_path=str(asset),
                        suggested_fix="Delete or replace empty file"
                    ))

    def _check_config(self) -> None:
        """Check configuration files."""
        config_file = self.project_path / ".engine" / "config.json"
        if not config_file.exists():
            self.report.add_message(DebugMessage(
                level=ErrorLevel.ERROR,
                category="config",
                message="Missing engine config.json",
                file_path=str(config_file),
                suggested_fix="Run project initializer"
            ))
            return

        try:
            with open(config_file, 'r') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            self.report.add_message(DebugMessage(
                level=ErrorLevel.ERROR,
                category="config",
                message=f"Invalid JSON in config: {e}",
                file_path=str(config_file),
                suggested_fix="Fix JSON syntax"
            ))

    def _check_scenes(self) -> None:
        """Check scene files."""
        scenes_dir = self.project_path / "Game Files" / "scenes"
        if not scenes_dir.exists():
            self.report.add_message(DebugMessage(
                level=ErrorLevel.INFO,
                category="scenes",
                message="No scenes directory found"
            ))
            return

        scene_files = list(scenes_dir.glob("*.json"))
        if not scene_files:
            self.report.add_message(DebugMessage(
                level=ErrorLevel.WARNING,
                category="scenes",
                message="No scene files found",
                suggested_fix="Create at least one scene"
            ))

    def _check_dependencies(self) -> None:
        """Check project dependencies."""
        requirements_file = self.project_path / "requirements.txt"
        if not requirements_file.exists():
            self.report.add_message(DebugMessage(
                level=ErrorLevel.INFO,
                category="dependencies",
                message="No requirements.txt found"
            ))

    def can_build(self) -> bool:
        """Check if project can build."""
        report = self.debug_project()
        return not report.has_critical()

    def get_report(self) -> Optional[DebugReport]:
        """Get last debug report."""
        return self.report
