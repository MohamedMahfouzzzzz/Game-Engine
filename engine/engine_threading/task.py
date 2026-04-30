# /**************************************************************************/
# /*  threading/task.py                                                     */
# /**************************************************************************/

"""Task definition for thread pool.

A Task represents a unit of work to be executed by a worker thread.
"""

from typing import Callable, Any, Optional, Dict
from dataclasses import dataclass, field
from enum import Enum, auto
from uuid import uuid4
import time


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = auto()      # Waiting in queue
    RUNNING = auto()      # Currently executing
    COMPLETED = auto()   # Finished successfully
    FAILED = auto()       # Finished with error
    CANCELLED = auto()    # Cancelled before execution


@dataclass
class TaskResult:
    """Result of a task execution."""
    success: bool
    result: Any = None
    error: Optional[Exception] = None
    execution_time: float = 0.0


class Task:
    """A unit of work for the thread pool.
    
    Tasks wrap a callable with metadata and result handling.
    
    Example:
        def heavy_computation(data):
            return process(data)
        
        task = Task(heavy_computation, args=(data,), priority=5)
        future = thread_pool.submit_task(task)
    """
    
    _id_counter = 0
    
    def __init__(self,
                 func: Callable,
                 args: tuple = (),
                 kwargs: Optional[Dict] = None,
                 priority: int = 0,
                 timeout: Optional[float] = None,
                 name: str = ""):
        """Create a task.
        
        Args:
            func: The function to execute
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function
            priority: Higher = executed first
            timeout: Maximum execution time in seconds
            name: Task name for debugging
        """
        Task._id_counter += 1
        self._id = Task._id_counter
        self._uuid = uuid4()
        
        self._func = func
        self._args = args
        self._kwargs = kwargs or {}
        self._priority = priority
        self._timeout = timeout
        self._name = name or f"Task_{self._id}"
        
        self._status = TaskStatus.PENDING
        self._result: Optional[TaskResult] = None
        self._created_at = time.time()
        self._started_at: Optional[float] = None
        self._completed_at: Optional[float] = None
        
        self._cancelled = False
    
    @property
    def id(self) -> int:
        """Task ID."""
        return self._id
    
    @property
    def uuid(self):
        """Task UUID."""
        return self._uuid
    
    @property
    def name(self) -> str:
        """Task name."""
        return self._name
    
    @property
    def priority(self) -> int:
        """Task priority."""
        return self._priority
    
    @property
    def status(self) -> TaskStatus:
        """Current status."""
        return self._status
    
    @property
    def result(self) -> Optional[TaskResult]:
        """Execution result (if completed)."""
        return self._result
    
    @property
    def is_pending(self) -> bool:
        """Check if task is pending."""
        return self._status == TaskStatus.PENDING
    
    @property
    def is_running(self) -> bool:
        """Check if task is running."""
        return self._status == TaskStatus.RUNNING
    
    @property
    def is_completed(self) -> bool:
        """Check if task is completed (success or failure)."""
        return self._status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED)
    
    @property
    def is_cancelled(self) -> bool:
        """Check if task was cancelled."""
        return self._status == TaskStatus.CANCELLED
    
    @property
    def age(self) -> float:
        """Time since task creation."""
        return time.time() - self._created_at
    
    @property
    def wait_time(self) -> Optional[float]:
        """Time spent waiting before execution."""
        if self._started_at:
            return self._started_at - self._created_at
        return None
    
    @property
    def execution_time(self) -> Optional[float]:
        """Time spent executing."""
        if self._completed_at and self._started_at:
            return self._completed_at - self._started_at
        return None
    
    def cancel(self) -> bool:
        """Cancel the task if still pending.
        
        Returns:
            True if cancelled, False if already running/completed
        """
        if self._status == TaskStatus.PENDING:
            self._status = TaskStatus.CANCELLED
            self._cancelled = True
            return True
        return False
    
    def execute(self) -> TaskResult:
        """Execute the task.
        
        This is called by the worker thread.
        
        Returns:
            TaskResult with success/failure info
        """
        if self._status == TaskStatus.CANCELLED:
            return TaskResult(False, error=Exception("Task was cancelled"))
        
        self._status = TaskStatus.RUNNING
        self._started_at = time.time()
        
        try:
            # Execute with timeout if specified
            if self._timeout:
                import signal
                
                def timeout_handler(signum, frame):
                    raise TimeoutError(f"Task exceeded {self._timeout}s timeout")
                
                old_handler = signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(int(self._timeout))
                
                try:
                    result = self._func(*self._args, **self._kwargs)
                finally:
                    signal.alarm(0)
                    signal.signal(signal.SIGALRM, old_handler)
            else:
                result = self._func(*self._args, **self._kwargs)
            
            self._status = TaskStatus.COMPLETED
            self._result = TaskResult(True, result=result)
            
        except Exception as e:
            self._status = TaskStatus.FAILED
            self._result = TaskResult(False, error=e)
        
        self._completed_at = time.time()
        if self._result:
            self._result.execution_time = self.execution_time or 0.0
        
        return self._result
    
    def __lt__(self, other: 'Task') -> bool:
        """Compare for priority queue (higher priority = less than)."""
        return self._priority > other._priority
    
    def __repr__(self) -> str:
        return f"Task({self._name}, {self._status.name}, priority={self._priority})"
