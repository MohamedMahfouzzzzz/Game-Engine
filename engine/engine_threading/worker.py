# /**************************************************************************/
# /*  threading/worker.py                                                   */
# /**************************************************************************/

"""Worker thread for executing tasks.

Individual worker that pulls tasks from a queue and executes them.
"""

from threading import Thread, Event
from enum import Enum, auto
from queue import Queue, Empty
from typing import Optional, Callable, Any
import time


class WorkerState(Enum):
    """Worker thread state."""
    IDLE = auto()       # Waiting for work
    RUNNING = auto()    # Executing a task
    STOPPING = auto()   # Being asked to stop
    STOPPED = auto()    # Thread has stopped


class Worker:
    """A worker thread that executes tasks from a queue.
    
    Workers are managed by a ThreadPool and execute tasks
    until told to stop.
    
    Example:
        worker = Worker(task_queue, worker_id=1)
        worker.start()
        # Worker runs until stop() is called
        worker.stop()
        worker.join()
    """
    
    _id_counter = 0
    
    def __init__(self,
                 task_queue: Queue,
                 result_callback: Optional[Callable] = None,
                 name: str = ""):
        """Create a worker.
        
        Args:
            task_queue: Queue to pull tasks from
            result_callback: Called with (task, result) after execution
            name: Worker name for debugging
        """
        Worker._id_counter += 1
        self._id = Worker._id_counter
        self._name = name or f"Worker-{self._id}"
        
        self._task_queue = task_queue
        self._result_callback = result_callback
        
        self._state = WorkerState.IDLE
        self._thread: Optional[Thread] = None
        self._stop_event = Event()
        
        self._tasks_completed = 0
        self._tasks_failed = 0
        
        self._current_task = None
    
    @property
    def id(self) -> int:
        """Worker ID."""
        return self._id
    
    @property
    def name(self) -> str:
        """Worker name."""
        return self._name
    
    @property
    def state(self) -> WorkerState:
        """Current state."""
        return self._state
    
    @property
    def is_running(self) -> bool:
        """Check if worker thread is running."""
        return self._thread is not None and self._thread.is_alive()
    
    @property
    def is_idle(self) -> bool:
        """Check if worker is idle (waiting for work)."""
        return self._state == WorkerState.IDLE
    
    @property
    def tasks_completed(self) -> int:
        """Number of tasks completed."""
        return self._tasks_completed
    
    @property
    def tasks_failed(self) -> int:
        """Number of tasks failed."""
        return self._tasks_failed
    
    @property
    def current_task(self) -> Optional[Any]:
        """Currently executing task (if any)."""
        return self._current_task
    
    def start(self) -> None:
        """Start the worker thread."""
        if self._thread is not None and self._thread.is_alive():
            return
        
        self._stop_event.clear()
        self._thread = Thread(target=self._run, name=self._name, daemon=True)
        self._thread.start()
    
    def stop(self, wait: bool = False, timeout: Optional[float] = None) -> None:
        """Signal the worker to stop.
        
        Args:
            wait: If True, wait for thread to finish
            timeout: Maximum time to wait
        """
        self._state = WorkerState.STOPPING
        self._stop_event.set()
        
        if wait and self._thread:
            self._thread.join(timeout)
    
    def join(self, timeout: Optional[float] = None) -> bool:
        """Wait for worker thread to finish.
        
        Args:
            timeout: Maximum time to wait
        
        Returns:
            True if thread finished, False if timeout
        """
        if self._thread:
            self._thread.join(timeout)
            return not self._thread.is_alive()
        return True
    
    def _run(self) -> None:
        """Main worker loop."""
        while not self._stop_event.is_set():
            try:
                # Wait for a task (with timeout to check stop_event)
                self._state = WorkerState.IDLE
                task = self._task_queue.get(timeout=0.5)
            except Empty:
                continue
            
            if task is None:
                # Poison pill - stop worker
                break
            
            if task.is_cancelled:
                continue
            
            # Execute task
            self._state = WorkerState.RUNNING
            self._current_task = task
            
            try:
                result = task.execute()
                
                if result.success:
                    self._tasks_completed += 1
                else:
                    self._tasks_failed += 1
                
                # Notify result callback
                if self._result_callback:
                    try:
                        self._result_callback(task, result)
                    except Exception as e:
                        print(f"Error in result callback: {e}")
                
            except Exception as e:
                self._tasks_failed += 1
                print(f"Error executing task {task.name}: {e}")
            
            finally:
                self._current_task = None
                self._task_queue.task_done()
        
        self._state = WorkerState.STOPPED
    
    def __repr__(self) -> str:
        return f"Worker({self._name}, {self._state.name}, completed={self._tasks_completed})"
