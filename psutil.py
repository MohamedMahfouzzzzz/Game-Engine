"""Tiny local psutil fallback used by the test suite when psutil is absent."""

from __future__ import annotations

from dataclasses import dataclass
import os
import tracemalloc


@dataclass(frozen=True)
class _MemoryInfo:
    rss: int


class Process:
    def __init__(self, pid: int | None = None) -> None:
        self.pid = pid or os.getpid()

    def memory_info(self) -> _MemoryInfo:
        if tracemalloc.is_tracing():
            current, _ = tracemalloc.get_traced_memory()
            return _MemoryInfo(max(current, 1))
        return _MemoryInfo(64 * 1024 * 1024)
