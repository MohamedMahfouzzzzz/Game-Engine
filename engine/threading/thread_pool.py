"""Compatibility exports for ``engine.threading.thread_pool``."""

from engine.engine_threading.thread_pool import TaskPriority, ThreadPool

__all__ = ["ThreadPool", "TaskPriority"]
