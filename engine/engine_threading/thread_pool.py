# /**************************************************************************/
# /*  threading/thread_pool.py                                              */
# /**************************************************************************/

"""Thread pool for managing worker threads.

Manages a pool of worker threads for executing tasks concurrently.
"""

from typing import Callable, Any, Optional, List, Dict
from queue import PriorityQueue, Queue
from threading import Lock, Event
from enum import IntEnum
import time

from .task import Task, TaskResult
from .future import Future
from .worker import Worker


class TaskPriority(IntEnum):
    """Standard task priorities."""
    LOW = 0
    NORMAL = 5
    HIGH = 10
    CRITICAL = 20


class ThreadPool:
    """A pool of worker threads for executing tasks.
    
    Manages worker threads, task queue, and result handling.
    
    Example:
        pool = ThreadPool(max_workers=4)
        pool.start()
        
        # Submit work
        future = pool.submit(my_function, arg1, arg2)
        result = future.result()  # Wait and get result
        
        # Or submit with priority
        task = Task(heavy_work, priority=10)
        future = pool.submit_task(task)
        
        pool.shutdown()
    """
    
    def __init__(self,
                 max_workers: int = 4,
                 max_queue_size: int = 0,
                 name: str = "ThreadPool"):
        """Create a thread pool.
        
        Args:
            max_workers: Maximum number of worker threads
            max_queue_size: Maximum task queue size (0 = unlimited)
            name: Pool name for debugging
        """
        self._name = name
        self._max_workers = max_workers
        self._max_queue_size = max_queue_size
        
        # Task queue (priority-based)
        if max_queue_size > 0:
            self._task_queue: Queue = Queue(maxsize=max_queue_size)
        else:
            self._task_queue = Queue()
        
        # Workers
        self._workers: List[Worker] = []
        self._worker_lock = Lock()
        
        # State
        self._started = False
        self._shutdown = False
        self._shutdown_event = Event()
        
        # Statistics
        self._tasks_submitted = 0
        self._tasks_completed = 0
        self._tasks_failed = 0
        self._stats_lock = Lock()
        
        # Futures tracking
        self._futures: Dict[int, Future] = {}
        self._futures_lock = Lock()
    
    @property
    def name(self) -> str:
        """Pool name."""
        return self._name
    
    @property
    def max_workers(self) -> int:
        """Maximum number of workers."""
        return self._max_workers
    
    @property
    def worker_count(self) -> int:
        """Current number of workers."""
        with self._worker_lock:
            return len(self._workers)
    
    @property
    def is_running(self) -> bool:
        """Check if pool is running."""
        return self._started and not self._shutdown
    
    @property
    def queue_size(self) -> int:
        """Current task queue size."""
        return self._task_queue.qsize()
    
    @property
    def stats(self) -> Dict[str, int]:
        """Pool statistics."""
        with self._stats_lock:
            return {
                'submitted': self._tasks_submitted,
                'completed': self._tasks_completed,
                'failed': self._tasks_failed,
                'pending': self._tasks_submitted - self._tasks_completed - self._tasks_failed,
            }
    
    def start(self) -> None:
        """Start the thread pool and create workers."""
        if self._started:
            return
        
        with self._worker_lock:
            for i in range(self._max_workers):
                worker = Worker(
                    self._task_queue,
                    result_callback=self._on_task_complete,
                    name=f"{self._name}-Worker-{i+1}"
                )
                worker.start()
                self._workers.append(worker)
        
        self._started = True
        self._shutdown = False
    
    def submit(self, func: Callable, *args: Any, **kwargs: Any) -> Future:
        """Submit a function for execution.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments (excluding priority/timeout)
        
        Returns:
            Future for getting the result
        """
        # Extract special kwargs
        priority = kwargs.pop('priority', TaskPriority.NORMAL)
        timeout = kwargs.pop('timeout', None)
        task_name = kwargs.pop('task_name', func.__name__)
        
        task = Task(
            func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            timeout=timeout,
            name=task_name
        )
        
        return self.submit_task(task)
    
    def submit_task(self, task: Task) -> Future:
        """Submit a Task object for execution.
        
        Args:
            task: The task to execute
        
        Returns:
            Future for getting the result
        """
        if self._shutdown:
            raise RuntimeError("Cannot submit to shut down pool")
        
        if not self._started:
            self.start()
        
        # Create future
        future = Future(task.id)
        
        with self._futures_lock:
            self._futures[task.id] = future
        
        with self._stats_lock:
            self._tasks_submitted += 1
        
        # Add to queue
        self._task_queue.put(task)
        
        return future
    
    def map(self, func: Callable, iterable: List[Any], 
            chunksize: int = 1) -> List[Any]:
        """Apply function to all items in parallel.
        
        Similar to multiprocessing.Pool.map().
        
        Args:
            func: Function to apply
            iterable: Items to process
            chunksize: Not used (for compatibility)
        
        Returns:
            List of results (in original order)
        """
        # Submit all tasks
        futures = []
        for item in iterable:
            future = self.submit(func, item)
            futures.append(future)
        
        # Wait for all results
        results = []
        for future in futures:
            results.append(future.result())
        
        return results
    
    def shutdown(self, wait: bool = True, timeout: Optional[float] = None) -> None:
        """Shutdown the thread pool.
        
        Args:
            wait: If True, wait for workers to finish
            timeout: Maximum time to wait
        """
        self._shutdown = True
        
        # Signal workers to stop
        with self._worker_lock:
            for worker in self._workers:
                worker.stop(wait=False)
        
        # Clear remaining tasks
        while not self._task_queue.empty():
            try:
                task = self._task_queue.get_nowait()
                if isinstance(task, Task) and task.is_pending:
                    task.cancel()
                self._task_queue.task_done()
            except:
                break
        
        # Wait for workers
        if wait:
            with self._worker_lock:
                for worker in self._workers:
                    worker.join(timeout)
        
        self._started = False
    
    def _on_task_complete(self, task: Task, result: TaskResult) -> None:
        """Handle task completion."""
        # Update stats
        with self._stats_lock:
            if result.success:
                self._tasks_completed += 1
            else:
                self._tasks_failed += 1
        
        # Update future
        with self._futures_lock:
            future = self._futures.pop(task.id, None)
        
        if future:
            if result.success:
                future.set_result(result.result)
            elif result.error:
                future.set_error(result.error)
            else:
                future.set_cancelled()
    
    def get_active_workers(self) -> List[Worker]:
        """Get list of currently busy workers."""
        with self._worker_lock:
            return [w for w in self._workers if not w.is_idle]
    
    def wait_for_all(self, timeout: Optional[float] = None) -> bool:
        """Wait for all submitted tasks to complete.
        
        Args:
            timeout: Maximum time to wait
        
        Returns:
            True if all tasks completed, False if timeout
        """
        start = time.time()
        while True:
            stats = self.stats
            if stats['pending'] == 0:
                return True
            
            if timeout and (time.time() - start) > timeout:
                return False
            
            time.sleep(0.01)
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown(wait=True)
    
    def __repr__(self) -> str:
        stats = self.stats
        return f"ThreadPool({self._name}, workers={self.worker_count}, pending={stats['pending']})"
