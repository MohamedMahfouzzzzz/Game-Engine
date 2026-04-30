# /**************************************************************************/
# /*  test_threading.py                                                     */
# /**************************************************************************/

"""Unit tests for threading module."""

import unittest
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engine.threading import (
    ThreadPool, Task, TaskPriority,
    Worker, Future
)
from engine.threading.task import TaskStatus, TaskResult
from engine.threading.future import FutureState


class TestTask(unittest.TestCase):
    """Test Task class."""
    
    def test_task_creation(self):
        """Test task creation."""
        def func(x):
            return x * 2
        
        task = Task(func, args=(5,), name='test', priority=10)
        
        self.assertEqual(task.name, 'test')
        self.assertEqual(task.priority, 10)
        self.assertEqual(task.status, TaskStatus.PENDING)
    
    def test_task_execution(self):
        """Test task execution."""
        def func(x, y):
            return x + y
        
        task = Task(func, args=(3, 4))
        result = task.execute()
        
        self.assertEqual(task.status, TaskStatus.COMPLETED)
        self.assertTrue(result.success)
        self.assertEqual(result.result, 7)
    
    def test_task_failure(self):
        """Test task failure handling."""
        def failing_func():
            raise ValueError('Test error')
        
        task = Task(failing_func)
        result = task.execute()
        
        self.assertEqual(task.status, TaskStatus.FAILED)
        self.assertFalse(result.success)
        self.assertIsInstance(result.error, ValueError)
    
    def test_task_cancellation(self):
        """Test task cancellation."""
        def func():
            return 42
        
        task = Task(func)
        cancelled = task.cancel()
        
        self.assertTrue(cancelled)
        self.assertEqual(task.status, TaskStatus.CANCELLED)
        
        result = task.execute()
        self.assertFalse(result.success)


class TestFuture(unittest.TestCase):
    """Test Future class."""
    
    def test_future_states(self):
        """Test future state transitions."""
        future = Future(1)
        
        self.assertEqual(future.state, FutureState.PENDING)
        
        future.set_running()
        self.assertEqual(future.state, FutureState.RUNNING)
        
        future.set_result(100)
        self.assertEqual(future.state, FutureState.COMPLETED)
        self.assertTrue(future.done())
    
    def test_future_result(self):
        """Test getting future result."""
        future = Future(1)
        future.set_result(42)
        
        result = future.result()
        self.assertEqual(result, 42)
    
    def test_future_error(self):
        """Test future error."""
        future = Future(1)
        future.set_error(RuntimeError('Test error'))
        
        self.assertTrue(future.done())
        
        with self.assertRaises(RuntimeError):
            future.result()
    
    def test_future_wait(self):
        """Test future wait."""
        future = Future(1)
        
        # Not done, should timeout
        completed = future.wait(timeout=0.01)
        self.assertFalse(completed)
        
        # Set result
        future.set_result(1)
        completed = future.wait(timeout=0.01)
        self.assertTrue(completed)
    
    def test_future_callback(self):
        """Test future callback."""
        future = Future(1)
        called = [False]
        
        def callback(f):
            called[0] = True
        
        future.add_callback(callback)
        future.set_result(1)
        
        self.assertTrue(called[0])


class TestThreadPool(unittest.TestCase):
    """Test ThreadPool."""
    
    def setUp(self):
        self.pool = ThreadPool(max_workers=2)
    
    def tearDown(self):
        self.pool.shutdown(wait=True)
    
    def test_submit(self):
        """Test submitting a task."""
        def func(x):
            return x * x
        
        future = self.pool.submit(func, 5)
        result = future.result(timeout=2)
        
        self.assertEqual(result, 25)
    
    def test_submit_multiple(self):
        """Test submitting multiple tasks."""
        def func(x):
            return x + 1
        
        futures = [self.pool.submit(func, i) for i in range(5)]
        results = [f.result(timeout=2) for f in futures]
        
        self.assertEqual(results, [1, 2, 3, 4, 5])
    
    def test_submit_with_priority(self):
        """Test submitting with priority."""
        def func(n):
            time.sleep(0.01)
            return n
        
        future = self.pool.submit(func, 10, priority=5)
        result = future.result(timeout=2)
        
        self.assertEqual(result, 10)
    
    def test_stats(self):
        """Test pool statistics."""
        def func():
            time.sleep(0.01)
            return 1
        
        futures = [self.pool.submit(func) for _ in range(3)]
        results = [f.result(timeout=2) for f in futures]
        
        stats = self.pool.stats
        self.assertEqual(stats['submitted'], 3)
        self.assertEqual(stats['completed'], 3)
    
    def test_context_manager(self):
        """Test pool as context manager."""
        def func():
            return 42
        
        with ThreadPool(max_workers=2) as pool:
            future = pool.submit(func)
            result = future.result(timeout=2)
            self.assertEqual(result, 42)


class TestWorker(unittest.TestCase):
    """Test Worker class."""
    
    def test_worker_lifecycle(self):
        """Test worker start and stop."""
        from queue import Queue
        
        q = Queue()
        worker = Worker(q, name='TestWorker')
        
        worker.start()
        self.assertTrue(worker.is_running)
        
        worker.stop(wait=False)
        time.sleep(0.1)
        
        # Should eventually stop
        self.assertIn(worker.state.name, ['STOPPED', 'STOPPING', 'IDLE'])


if __name__ == '__main__':
    unittest.main()
