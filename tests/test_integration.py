# /**************************************************************************/
# /*  test_integration.py                                                   */
# /**************************************************************************/

"""Integration tests for the complete system."""

import unittest
import sys
import os
import tempfile
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engine.tools.pixel_art_editor.core import (
    Document, Layer, BlendMode, ColorMode
)
from engine.io import BinaryFormat
from engine.signals import SignalManager
from engine.threading import ThreadPool
from engine.core.commands import CommandHistory
from engine.tools.pixel_art_editor.brushes import BrushManager, BrushPresets
from engine.tools.pixel_art_editor.algorithms import line_points, flood_fill_simple


class TestDocumentWorkflow(unittest.TestCase):
    """Test complete document workflow."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, 'integration_test.ges')
    
    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        os.rmdir(self.temp_dir)
    
    def test_complete_workflow(self):
        """Test create -> edit -> save -> load workflow."""
        # 1. Create document
        doc = Document(64, 64, 'IntegrationTest')
        self.assertEqual(doc.width, 64)
        self.assertEqual(doc.height, 64)
        
        # 2. Add layers
        bg_layer = doc.sprite.add_layer('Background')
        bg_layer.is_background = True
        
        main_layer = doc.sprite.add_layer('Main')
        main_layer.opacity = 255
        
        # 3. Draw on layers
        # Draw background
        for y in range(64):
            for x in range(64):
                bg_layer.set_pixel(x, y, (64, 64, 64, 255))
        
        # Draw pattern on main layer
        for i in range(0, 64, 8):
            for j in range(0, 64, 8):
                main_layer.set_pixel(i, j, (255, 255, 255, 255))
        
        # 4. Add frames for animation
        doc.sprite.add_frame(100)
        doc.sprite.add_frame(100)
        
        # Draw on frame 1
        frame1_layer = doc.sprite.get_layer('Main', 1)
        for i in range(16, 48):
            frame1_layer.set_pixel(i, 32, (255, 0, 0, 255))
        
        # 5. Save document
        success = BinaryFormat.save(doc, self.test_file)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(self.test_file))
        
        # 6. Load document
        loaded = BinaryFormat.load(self.test_file)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.name, 'IntegrationTest')
        self.assertEqual(loaded.width, 64)
        self.assertEqual(loaded.height, 64)
        self.assertEqual(loaded.sprite.layer_count, 2)
        self.assertEqual(loaded.sprite.frame_count, 3)
        
        # 7. Verify content
        bg_loaded = loaded.sprite.get_layer('Background')
        self.assertEqual(bg_loaded.get_pixel(0, 0), (64, 64, 64, 255))
        
        main_loaded = loaded.sprite.get_layer('Main')
        self.assertEqual(main_loaded.get_pixel(0, 0), (255, 255, 255, 255))
        self.assertEqual(main_loaded.get_pixel(1, 0), (64, 64, 64, 255))
        
        frame1_loaded = loaded.sprite.get_layer('Main', 1)
        self.assertEqual(frame1_loaded.get_pixel(16, 32), (255, 0, 0, 255))


class TestBrushSystemIntegration(unittest.TestCase):
    """Test brush system integration with drawing."""
    
    def setUp(self):
        self.doc = Document(32, 32, 'BrushTest')
        self.layer = self.doc.sprite.layers[0]
        self.manager = BrushManager()
        BrushPresets.register_all_to_manager(self.manager)
    
    def test_brush_drawing_workflow(self):
        """Test complete brush drawing workflow."""
        # 1. Get brush
        brush = self.manager.get_brush('Pencil')
        self.assertIsNotNone(brush)
        
        # 2. Draw line with brush
        points = line_points(5, 5, 25, 25)
        for x, y in points:
            if 0 <= x < 32 and 0 <= y < 32:
                self.layer.set_pixel(x, y, (255, 0, 0, 255))
        
        # 3. Verify drawing
        self.assertEqual(self.layer.get_pixel(5, 5), (255, 0, 0, 255))
        self.assertEqual(self.layer.get_pixel(25, 25), (255, 0, 0, 255))
        
        # 4. Use flood fill
        filled = flood_fill_simple(
            10, 10,
            lambda x, y: self.layer.get_pixel(x, y),
            lambda x, y, c: self.layer.set_pixel(x, y, c),
            (64, 64, 64, 255),  # Background
            (0, 255, 0, 255),  # Fill with green
            (0, 0, 32, 32)
        )
        
        # 5. Verify fill
        self.assertGreater(filled, 0)
        self.assertEqual(self.layer.get_pixel(10, 10), (0, 255, 0, 255))


class TestSignalThreadingIntegration(unittest.TestCase):
    """Test signals and threading integration."""
    
    def setUp(self):
        self.manager = SignalManager()
        self.pool = ThreadPool(max_workers=2)
        self.results = []
    
    def tearDown(self):
        self.pool.shutdown()
    
    def test_async_signal_emission(self):
        """Test emitting signals from threads."""
        self.manager.add_signal('task_complete', Signal(str, int))
        
        def handle_task_complete(name, result):
            self.results.append((name, result))
        
        self.manager.connect('task_complete', handle_task_complete)
        
        def compute_task(name, n):
            """Compute task in thread."""
            total = sum(i * i for i in range(n))
            # Emit signal from thread
            self.manager.emit('task_complete', name, total)
            return total
        
        # Submit tasks
        futures = []
        for i in range(4):
            future = self.pool.submit(compute_task, f'Task{i}', 1000)
            futures.append(future)
        
        # Wait for completion
        for future in futures:
            future.result(timeout=5)
        
        # Verify signals were emitted
        self.assertEqual(len(self.results), 4)
        self.assertIn(('Task0', 332833500), self.results)
        self.assertIn(('Task1', 332833500), self.results)
        self.assertIn(('Task2', 332833500), self.results)
        self.assertIn(('Task3', 332833500), self.results)


class TestCommandSystemIntegration(unittest.TestCase):
    """Test command system integration."""
    
    def setUp(self):
        self.doc = Document(16, 16, 'CommandTest')
        self.layer = self.doc.sprite.layers[0]
        self.history = CommandHistory()
    
    def test_command_workflow(self):
        """Test complete command workflow."""
        from engine.core.commands import Command, CommandResult, Transaction
        
        class DrawPixelCommand(Command):
            def __init__(self, layer, x, y, color):
                super().__init__('DrawPixel')
                self.layer = layer
                self.x = x
                self.y = y
                self.color = color
                self._old_color = None
            
            def execute(self):
                self._old_color = self.layer.get_pixel(self.x, self.y)
                self.layer.set_pixel(self.x, self.y, self.color)
                self._mark_executed()
                return CommandResult.SUCCESS
            
            def undo(self):
                self.layer.set_pixel(self.x, self.y, self._old_color)
                self._mark_undone()
                return CommandResult.SUCCESS
        
        # 1. Execute commands
        cmd1 = DrawPixelCommand(self.layer, 5, 5, (255, 0, 0, 255))
        cmd2 = DrawPixelCommand(self.layer, 10, 10, (0, 255, 0, 255))
        
        self.history.execute(cmd1)
        self.history.execute(cmd2)
        
        # 2. Verify changes
        self.assertEqual(self.layer.get_pixel(5, 5), (255, 0, 0, 255))
        self.assertEqual(self.layer.get_pixel(10, 10), (0, 255, 0, 255))
        
        # 3. Undo
        self.history.undo()
        self.assertEqual(self.layer.get_pixel(10, 10), (0, 0, 0, 0))
        self.assertEqual(self.layer.get_pixel(5, 5), (255, 0, 0, 255))
        
        # 4. Redo
        self.history.redo()
        self.assertEqual(self.layer.get_pixel(10, 10), (0, 255, 0, 255))
        
        # 5. Test transaction
        with Transaction(self.history, 'BatchDraw'):
            for i in range(3):
                cmd = DrawPixelCommand(self.layer, i, i, (0, 0, 255, 255))
                self.history.execute(cmd)
        
        # Verify all pixels drawn
        for i in range(3):
            self.assertEqual(self.layer.get_pixel(i, i), (0, 0, 255, 255))
        
        # Undo should remove all at once
        self.history.undo()
        for i in range(3):
            self.assertEqual(self.layer.get_pixel(i, i), (0, 0, 0, 0))


class TestPerformanceIntegration(unittest.TestCase):
    """Test performance with integrated system."""
    
    def test_large_document_performance(self):
        """Test performance with large documents."""
        # Create large document
        doc = Document(512, 512, 'PerfTest')
        layer = doc.sprite.layers[0]
        
        # Measure drawing performance
        start = time.time()
        
        # Draw pattern
        for y in range(0, 512, 8):
            for x in range(0, 512, 8):
                layer.set_pixel(x, y, (255, 255, 255, 255))
        
        draw_time = time.time() - start
        
        # Should complete in reasonable time
        self.assertLess(draw_time, 1.0, f"Drawing took {draw_time:.3f}s")
        
        # Test is_empty performance
        start = time.time()
        is_empty = layer.is_empty()
        empty_time = time.time() - start
        
        self.assertFalse(is_empty)
        self.assertLess(empty_time, 0.1, f"is_empty took {empty_time:.3f}s")
        
        # Test clear performance
        start = time.time()
        layer.clear((0, 0, 0, 0))
        clear_time = time.time() - start
        
        self.assertLess(clear_time, 0.1, f"Clear took {clear_time:.3f}s")
        self.assertTrue(layer.is_empty())
    
    def test_thread_pool_scaling(self):
        """Test thread pool scaling with CPU tasks."""
        pool = ThreadPool(max_workers=4)
        
        def cpu_task(n):
            """CPU-intensive task."""
            total = 0
            for i in range(n):
                total += i * i
            return total
        
        # Single thread baseline
        start = time.time()
        single_results = [cpu_task(10000) for _ in range(8)]
        single_time = time.time() - start
        
        # Multi-threaded
        start = time.time()
        futures = [pool.submit(cpu_task, 10000) for _ in range(8)]
        multi_results = [f.result() for f in futures]
        multi_time = time.time() - start
        
        pool.shutdown()
        
        # Verify results match
        self.assertEqual(single_results, multi_results)
        
        # Multi-threaded should be faster (though maybe not 4x due to GIL)
        speedup = single_time / multi_time if multi_time > 0 else 0
        self.assertGreater(speedup, 0.5, f"Speedup only {speedup:.2f}x")


class TestErrorHandlingIntegration(unittest.TestCase):
    """Test error handling across integrated components."""
    
    def test_corrupted_file_handling(self):
        """Test handling of corrupted files."""
        # Create corrupted file
        with tempfile.NamedTemporaryFile(suffix='.ges', delete=False) as f:
            f.write(b'CORRUPTED_DATA')
            corrupted_file = f.name
        
        try:
            # Should handle gracefully
            loaded = BinaryFormat.load(corrupted_file)
            self.assertIsNone(loaded)
        finally:
            os.unlink(corrupted_file)
    
    def test_invalid_operations(self):
        """Test handling of invalid operations."""
        doc = Document(16, 16, 'ErrorTest')
        layer = doc.sprite.layers[0]
        
        # Out of bounds should return transparent
        color = layer.get_pixel(-1, -1)
        self.assertEqual(color, (0, 0, 0, 0))
        
        color = layer.get_pixel(100, 100)
        self.assertEqual(color, (0, 0, 0, 0))
        
        # Setting out of bounds should be ignored
        layer.set_pixel(-1, -1, (255, 0, 0, 255))
        self.assertEqual(layer.get_pixel(0, 0), (0, 0, 0, 0))


if __name__ == '__main__':
    unittest.main()
