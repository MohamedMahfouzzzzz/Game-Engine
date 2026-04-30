# /**************************************************************************/
# /*  profiler_backend.py                                                   */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Performance profiler backend for telemetry."""

import time
from collections import defaultdict
from contextlib import contextmanager
from typing import Dict, List, Optional, Callable

import logging

logger = logging.getLogger(__name__)


class ProfileSection:
    """Profile data for a code section."""

    def __init__(self, name: str):
        self.name = name
        self.total_time: float = 0.0
        self.call_count: int = 0
        self.min_time: float = float('inf')
        self.max_time: float = 0.0
        self._start_time: Optional[float] = None

    def start(self) -> None:
        """Start timing."""
        self._start_time = time.perf_counter()

    def stop(self) -> None:
        """Stop timing and record."""
        if self._start_time is not None:
            elapsed = time.perf_counter() - self._start_time
            self.total_time += elapsed
            self.call_count += 1
            self.min_time = min(self.min_time, elapsed)
            self.max_time = max(self.max_time, elapsed)
            self._start_time = None

    @property
    def average_time(self) -> float:
        """Calculate average time per call."""
        if self.call_count == 0:
            return 0.0
        return self.total_time / self.call_count


class ProfilerBackend:
    """Backend profiler for telemetry data collection."""

    def __init__(self):
        self.sections: Dict[str, ProfileSection] = {}
        self._active_stack: List[str] = []
        self._enabled: bool = False
        self._frame_times: List[float] = []
        self._max_frame_history = 1000

    def enable(self) -> None:
        """Enable profiling."""
        self._enabled = True

    def disable(self) -> None:
        """Disable profiling."""
        self._enabled = False

    @contextmanager
    def profile(self, section_name: str):
        """Context manager for profiling a code section."""
        self.begin_section(section_name)
        try:
            yield
        finally:
            self.end_section(section_name)

    def begin_section(self, name: str) -> None:
        """Begin profiling a section."""
        if not self._enabled:
            return

        if name not in self.sections:
            self.sections[name] = ProfileSection(name)

        self.sections[name].start()
        self._active_stack.append(name)

    def end_section(self, name: str) -> None:
        """End profiling a section."""
        if not self._enabled:
            return

        if name in self.sections:
            self.sections[name].stop()

        if self._active_stack and self._active_stack[-1] == name:
            self._active_stack.pop()

    def record_frame_time(self, delta_time: float) -> None:
        """Record a frame time."""
        if not self._enabled:
            return

        self._frame_times.append(delta_time)
        if len(self._frame_times) > self._max_frame_history:
            self._frame_times.pop(0)

    def get_fps(self) -> float:
        """Calculate current FPS from recent frame times."""
        if not self._frame_times:
            return 0.0

        avg_time = sum(self._frame_times[-60:]) / min(len(self._frame_times), 60)
        return 1.0 / avg_time if avg_time > 0 else 0.0

    def get_report(self) -> Dict:
        """Generate profiling report."""
        return {
            "sections": {
                name: {
                    "total_time": section.total_time,
                    "call_count": section.call_count,
                    "average_time": section.average_time,
                    "min_time": section.min_time if section.min_time != float('inf') else 0,
                    "max_time": section.max_time
                }
                for name, section in self.sections.items()
            },
            "fps": {
                "current": self.get_fps(),
                "average": len(self._frame_times) / sum(self._frame_times) if self._frame_times else 0,
                "min": 1.0 / max(self._frame_times) if self._frame_times else 0,
                "max": 1.0 / min(self._frame_times) if self._frame_times else 0
            }
        }

    def reset(self) -> None:
        """Reset all profiling data."""
        self.sections.clear()
        self._frame_times.clear()
        self._active_stack.clear()


# Global profiler instance
global_profiler = ProfilerBackend()
