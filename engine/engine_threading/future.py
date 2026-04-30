# /**************************************************************************/
# /*  threading/future.py                                                   */
# /**************************************************************************/

"""Future for async operation results.

Similar to concurrent.futures.Future, allows getting results
from async operations and waiting for completion.
"""

from typing import Any, Optional, Callable, List
from enum import Enum, auto
from threading import Event, RLock
import time


class FutureState(Enum):
    """Future state."""
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


class Future:
    """Handle for an asynchronous operation result.
    
    A Future represents a result that will be available in the future.
    Allows waiting, checking status, and getting results.
    
    Example:
        future = thread_pool.submit(some_function)
        
        # Wait for result
        result = future.result()  # Blocks until done
        
        # Or check status
        if future.done():
            result = future.result()
    """
    
    def __init__(self, task_id: int):
        self._task_id = task_id
        self._state = FutureState.PENDING
        self._result: Any = None
        self._error: Optional[Exception] = None
        
        self._event = Event()
        self._lock = RLock()
        
        self._callbacks: List[Callable[[Future], None]] = []
        self._done_callbacks: List[Callable[[Future], None]] = []
    
    @property
    def task_id(self) -> int:
        """Task ID this future represents."""
        return self._task_id
    
    @property
    def state(self) -> FutureState:
        """Current state."""
        with self._lock:
            return self._state
    
    def done(self) -> bool:
        """Check if operation is complete."""
        with self._lock:
            return self._state in (FutureState.COMPLETED, FutureState.FAILED, FutureState.CANCELLED)
    
    def running(self) -> bool:
        """Check if operation is running."""
        with self._lock:
            return self._state == FutureState.RUNNING
    
    def cancelled(self) -> bool:
        """Check if operation was cancelled."""
        with self._lock:
            return self._state == FutureState.CANCELLED
    
    def set_running(self) -> None:
        """Mark as running (called by worker)."""
        with self._lock:
            if self._state == FutureState.PENDING:
                self._state = FutureState.RUNNING
    
    def set_result(self, result: Any) -> None:
        """Set the result (called by worker)."""
        with self._lock:
            if self._state == FutureState.CANCELLED:
                return
            self._result = result
            self._state = FutureState.COMPLETED
        
        self._event.set()
        self._invoke_callbacks()
        self._invoke_done_callbacks()
    
    def set_error(self, error: Exception) -> None:
        """Set error (called by worker)."""
        with self._lock:
            if self._state == FutureState.CANCELLED:
                return
            self._error = error
            self._state = FutureState.FAILED
        
        self._event.set()
        self._invoke_callbacks()
        self._invoke_done_callbacks()
    
    def set_cancelled(self) -> None:
        """Mark as cancelled."""
        with self._lock:
            self._state = FutureState.CANCELLED
        
        self._event.set()
        self._invoke_done_callbacks()
    
    def cancel(self) -> bool:
        """Attempt to cancel the operation.
        
        Returns:
            True if cancelled, False if already running/done
        """
        with self._lock:
            if self._state in (FutureState.PENDING, FutureState.RUNNING):
                self._state = FutureState.CANCELLED
                self._event.set()
                return True
            return False
    
    def result(self, timeout: Optional[float] = None) -> Any:
        """Get the result, waiting if necessary.
        
        Args:
            timeout: Maximum time to wait (None = infinite)
        
        Returns:
            The result value
        
        Raises:
            TimeoutError: If timeout expires
            Exception: If the operation failed (re-raises the original error)
            CancelledError: If the operation was cancelled
        """
        if not self._event.wait(timeout):
            raise TimeoutError(f"Future did not complete within {timeout}s")
        
        with self._lock:
            if self._state == FutureState.CANCELLED:
                raise CancelledError("Future was cancelled")
            if self._state == FutureState.FAILED:
                raise self._error
            return self._result
    
    def exception(self, timeout: Optional[float] = None) -> Optional[Exception]:
        """Get the exception if one occurred.
        
        Args:
            timeout: Maximum time to wait
        
        Returns:
            The exception, or None if no error
        """
        if not self._event.wait(timeout):
            raise TimeoutError(f"Future did not complete within {timeout}s")
        
        with self._lock:
            return self._error
    
    def add_callback(self, callback: "Callable[[Future], None]") -> None:
        """Add a callback to be invoked when result is ready.
        
        The callback is called with this Future as its argument.
        """
        with self._lock:
            if self._state in (FutureState.COMPLETED, FutureState.FAILED, FutureState.CANCELLED):
                callback(self)
            else:
                self._callbacks.append(callback)
    
    def add_done_callback(self, callback: "Callable[[Future], None]") -> None:
        """Add a callback to be invoked when done (success or failure).
        
        Similar to add_callback but called even on error/cancellation.
        """
        with self._lock:
            if self._state in (FutureState.COMPLETED, FutureState.FAILED, FutureState.CANCELLED):
                callback(self)
            else:
                self._done_callbacks.append(callback)
    
    def _invoke_callbacks(self) -> None:
        """Invoke result callbacks."""
        for callback in self._callbacks:
            try:
                callback(self)
            except Exception as e:
                print(f"Error in future callback: {e}")
        self._callbacks.clear()
    
    def _invoke_done_callbacks(self) -> None:
        """Invoke done callbacks."""
        for callback in self._done_callbacks:
            try:
                callback(self)
            except Exception as e:
                print(f"Error in future done callback: {e}")
        self._done_callbacks.clear()
    
    def wait(self, timeout: Optional[float] = None) -> bool:
        """Wait for completion without getting result.
        
        Args:
            timeout: Maximum time to wait
        
        Returns:
            True if completed, False if timeout
        """
        return self._event.wait(timeout)
    
    def __repr__(self) -> str:
        return f"Future({self._task_id}, {self._state.name})"


class CancelledError(Exception):
    """Raised when a future is cancelled."""
    pass
