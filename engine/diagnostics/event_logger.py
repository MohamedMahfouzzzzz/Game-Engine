"""Event logging system."""

import logging
import json
from pathlib import Path
from typing import Optional
from datetime import datetime


class EventLogger:
    """Logs engine events to file."""

    def __init__(self, project_path: str, log_level: int = logging.INFO):
        self.project_path = Path(project_path)
        self.logs_dir = self.project_path / ".logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Setup file logger
        self.logger = logging.getLogger("GameEngine")
        self.logger.setLevel(log_level)

        # Error log file
        error_handler = logging.FileHandler(
            self.logs_dir / "errors.log"
        )
        error_handler.setLevel(logging.ERROR)
        error_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        error_handler.setFormatter(error_formatter)
        self.logger.addHandler(error_handler)

        # Event log file
        event_handler = logging.FileHandler(
            self.logs_dir / "events.log"
        )
        event_handler.setLevel(log_level)
        event_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        event_handler.setFormatter(event_formatter)
        self.logger.addHandler(event_handler)

    def info(self, message: str, data: Optional[dict] = None) -> None:
        """Log info event."""
        msg = message
        if data:
            msg += f" | {json.dumps(data)}"
        self.logger.info(msg)

    def warning(self, message: str, data: Optional[dict] = None) -> None:
        """Log warning event."""
        msg = message
        if data:
            msg += f" | {json.dumps(data)}"
        self.logger.warning(msg)

    def error(self, message: str, data: Optional[dict] = None) -> None:
        """Log error event."""
        msg = message
        if data:
            msg += f" | {json.dumps(data)}"
        self.logger.error(msg)

    def critical(self, message: str, data: Optional[dict] = None) -> None:
        """Log critical event."""
        msg = message
        if data:
            msg += f" | {json.dumps(data)}"
        self.logger.critical(msg)

    def debug(self, message: str, data: Optional[dict] = None) -> None:
        """Log debug event."""
        msg = message
        if data:
            msg += f" | {json.dumps(data)}"
        self.logger.debug(msg)

    def log_scene_load(self, scene_name: str, load_time_ms: float) -> None:
        """Log scene load event."""
        self.info("Scene loaded", {
            'scene': scene_name,
            'load_time_ms': load_time_ms,
            'timestamp': datetime.now().isoformat()
        })

    def log_entity_spawn(self, entity_id: str, entity_type: str,
                        position: tuple = (0, 0)) -> None:
        """Log entity spawn event."""
        self.info("Entity spawned", {
            'entity_id': entity_id,
            'entity_type': entity_type,
            'position': position,
            'timestamp': datetime.now().isoformat()
        })

    def log_error(self, error_type: str, error_msg: str,
                  context: Optional[dict] = None) -> None:
        """Log error with context."""
        data = {
            'error_type': error_type,
            'error_message': error_msg,
            'timestamp': datetime.now().isoformat()
        }
        if context:
            data['context'] = context

        self.error("Error occurred", data)

    def log_performance_warning(self, metric_name: str, value: float,
                               threshold: float) -> None:
        """Log performance warning."""
        self.warning("Performance warning", {
            'metric': metric_name,
            'value': value,
            'threshold': threshold,
            'timestamp': datetime.now().isoformat()
        })

    def clear_old_logs(self, days: int = 7) -> None:
        """Clear logs older than specified days."""
        import time
        cutoff_time = time.time() - (days * 24 * 60 * 60)

        for log_file in self.logs_dir.glob("*.log"):
            if log_file.stat().st_mtime < cutoff_time:
                log_file.unlink()

    def get_error_count(self) -> int:
        """Get count of logged errors."""
        error_file = self.logs_dir / "errors.log"
        if not error_file.exists():
            return 0

        with open(error_file, 'r') as f:
            return sum(1 for _ in f)

    def get_recent_errors(self, count: int = 10) -> list[str]:
        """Get most recent errors."""
        error_file = self.logs_dir / "errors.log"
        if not error_file.exists():
            return []

        with open(error_file, 'r') as f:
            lines = f.readlines()
            return lines[-count:]
