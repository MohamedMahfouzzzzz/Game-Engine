"""Performance metrics collection and monitoring."""

import time
import psutil
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from collections import deque


@dataclass
class FrameMetrics:
    """Metrics for a single frame."""

    timestamp: float
    fps: float
    delta_time: float
    memory_usage_mb: float
    cpu_percent: float
    active_entities: int
    draw_calls: int


class PerformanceMetrics:
    """Collects and analyzes performance metrics."""

    def __init__(self, max_history: int = 300):
        self.max_history = max_history
        self.frame_history: deque = deque(maxlen=max_history)
        self.last_frame_time = time.time()
        self.frame_count = 0
        self.process = psutil.Process(os.getpid())

    def record_frame(self, active_entities: int = 0, draw_calls: int = 0) -> FrameMetrics:
        """Record metrics for current frame."""
        now = time.time()
        delta_time = now - self.last_frame_time
        self.last_frame_time = now
        self.frame_count += 1

        # Calculate FPS
        fps = 1.0 / delta_time if delta_time > 0 else 0.0

        # Get memory usage
        memory_mb = self.process.memory_info().rss / (1024 * 1024)

        # Get CPU usage
        cpu_percent = self.process.cpu_percent(interval=None)

        metrics = FrameMetrics(
            timestamp=now,
            fps=fps,
            delta_time=delta_time,
            memory_usage_mb=memory_mb,
            cpu_percent=cpu_percent,
            active_entities=active_entities,
            draw_calls=draw_calls
        )

        self.frame_history.append(metrics)
        return metrics

    def get_average_fps(self) -> float:
        """Get average FPS over history."""
        if not self.frame_history:
            return 0.0
        return sum(m.fps for m in self.frame_history) / len(self.frame_history)

    def get_average_delta_time(self) -> float:
        """Get average delta time."""
        if not self.frame_history:
            return 0.0
        return sum(m.delta_time for m in self.frame_history) / len(self.frame_history)

    def get_average_memory(self) -> float:
        """Get average memory usage."""
        if not self.frame_history:
            return 0.0
        return sum(m.memory_usage_mb for m in self.frame_history) / len(self.frame_history)

    def get_peak_memory(self) -> float:
        """Get peak memory usage."""
        if not self.frame_history:
            return 0.0
        return max(m.memory_usage_mb for m in self.frame_history)

    def get_average_cpu(self) -> float:
        """Get average CPU usage."""
        if not self.frame_history:
            return 0.0
        return sum(m.cpu_percent for m in self.frame_history) / len(self.frame_history)

    def get_min_fps(self) -> float:
        """Get minimum FPS."""
        if not self.frame_history:
            return 0.0
        return min(m.fps for m in self.frame_history)

    def get_max_fps(self) -> float:
        """Get maximum FPS."""
        if not self.frame_history:
            return 0.0
        return max(m.fps for m in self.frame_history)

    def detect_stutters(self, threshold: float = 30.0) -> List[float]:
        """Detect frame time spikes."""
        spikes = []
        for metrics in self.frame_history:
            if metrics.delta_time > (1.0 / threshold):
                spikes.append(metrics.delta_time)
        return spikes

    def detect_memory_leaks(self, window: int = 60) -> bool:
        """Detect potential memory leaks."""
        if len(self.frame_history) < window:
            return False

        recent = list(self.frame_history)[-window:]
        first_half = sum(m.memory_usage_mb for m in recent[:window//2]) / (window//2)
        second_half = sum(m.memory_usage_mb for m in recent[window//2:]) / (window//2)

        # If memory is consistently increasing
        return second_half > first_half * 1.1

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            'frames_recorded': len(self.frame_history),
            'average_fps': self.get_average_fps(),
            'min_fps': self.get_min_fps(),
            'max_fps': self.get_max_fps(),
            'average_delta_ms': self.get_average_delta_time() * 1000,
            'average_memory_mb': self.get_average_memory(),
            'peak_memory_mb': self.get_peak_memory(),
            'average_cpu_percent': self.get_average_cpu(),
            'potential_leak': self.detect_memory_leaks()
        }

    def reset(self) -> None:
        """Reset metrics."""
        self.frame_history.clear()
        self.frame_count = 0
        self.last_frame_time = time.time()

    def get_latest_metrics(self) -> Optional[FrameMetrics]:
        """Get latest frame metrics."""
        return self.frame_history[-1] if self.frame_history else None
