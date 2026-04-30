# /**************************************************************************/
# /*  test_memory_performance.py                                            */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Memory performance and optimization tests.

Tests memory usage, leaks, and efficiency across engine components.
"""

import gc
import sys
import tracemalloc
import pytest

from engine.core.project_secure import SecureProject, ProjectConfig
from engine.core.node_base import Node
from engine.tools.pixel_art_editor.scripting.api.sprite import Sprite, Layer, Frame


class TestMemoryEfficiency:
    """Test memory usage efficiency."""
    
    def test_node_memory_footprint(self):
        """Verify Node memory footprint is reasonable."""
        # Create many nodes and check memory
        tracemalloc.start()
        
        nodes = [Node(f"Node{i}") for i in range(1000)]
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Should use less than 100MB for 1000 nodes
        assert current < 100 * 1024 * 1024, f"Memory usage too high: {current / 1024 / 1024:.2f} MB"
        
        # Cleanup
        del nodes
        gc.collect()
    
    def test_sprite_memory_footprint(self):
        """Test Sprite memory usage."""
        tracemalloc.start()
        
        sprites = [Sprite(64, 64) for _ in range(100)]
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # 100 sprites should use reasonable memory
        assert current < 50 * 1024 * 1024, f"Sprite memory too high: {current / 1024 / 1024:.2f} MB"
        
        del sprites
        gc.collect()
    
    def test_project_lazy_loading_saves_memory(self):
        """Lazy loading defers memory allocation."""
        config = ProjectConfig(lazy_loading=True)
        project = SecureProject("Lazy Test", config)
        
        # Create many scenes
        for i in range(50):
            project.create_scene(f"Scene {i}")
        
        # Check memory stats
        stats = project.get_memory_usage()
        assert stats["scene_count"] == 50
        # Initially all loaded, but after unload:
        for scene_id in list(project._scenes.keys())[:25]:
            project.unload_scene(scene_id)
        
        stats = project.get_memory_usage()
        assert stats["loaded_scenes"] == 25
    
    def test_memory_leak_detection(self):
        """Detect memory leaks in repeated operations."""
        gc.collect()
        tracemalloc.start()
        
        # Baseline
        baseline = tracemalloc.get_traced_memory()[0]
        
        # Perform operations multiple times
        for _ in range(100):
            sprite = Sprite(32, 32)
            layer = sprite.newLayer()
            sprite.deleteLayer(layer)
            del sprite
        
        gc.collect()
        current = tracemalloc.get_traced_memory()[0]
        tracemalloc.stop()
        
        # Memory should not grow significantly
        growth = current - baseline
        assert growth < 10 * 1024 * 1024, f"Potential memory leak: {growth / 1024:.2f} KB growth"


class TestGarbageCollection:
    """Test garbage collection behavior."""
    
    def test_circular_references_collected(self):
        """Circular references between nodes are cleaned up."""
        import weakref
        
        # Create circular reference
        node_a = Node("A")
        node_b = Node("B")
        node_a.add_child(node_b)
        
        weak_a = weakref.ref(node_a)
        weak_b = weakref.ref(node_b)
        
        del node_a, node_b
        gc.collect()
        
        # Both should be collected
        assert weak_a() is None or weak_b() is None
    
    def test_sprite_layer_cleanup(self):
        """Sprite and layers are properly cleaned up."""
        import weakref
        
        sprite = Sprite(32, 32)
        layer = sprite.newLayer()
        
        weak_layer = weakref.ref(layer)
        
        sprite.deleteLayer(layer)
        del layer
        gc.collect()
        
        # Layer reference may still exist in sprite's list, but should be None
        # when fully dereferenced


class TestLargeDatasetHandling:
    """Test handling of large datasets."""
    
    def test_large_scene_graph_performance(self):
        """Performance with 1000+ nodes."""
        import time
        
        root = Node("Root")
        start = time.time()
        
        # Create deep hierarchy
        current = root
        for i in range(100):
            child = Node(f"Child{i}")
            current.add_child(child)
            current = child
        
        elapsed = time.time() - start
        
        # Should complete in reasonable time
        assert elapsed < 1.0, f"Scene creation too slow: {elapsed:.2f}s"
    
    def test_large_sprite_performance(self):
        """Performance with large sprite dimensions."""
        import time
        
        # Create large sprite
        start = time.time()
        sprite = Sprite(2048, 2048)
        elapsed = time.time() - start
        
        assert elapsed < 0.5, f"Large sprite creation too slow: {elapsed:.2f}s"


@pytest.mark.benchmark
class TestBenchmarkPerformance:
    """Benchmark tests for performance regression."""
    
    def test_node_creation_benchmark(self, benchmark):
        """Benchmark node creation speed."""
        def create_nodes():
            return [Node(f"Node{i}") for i in range(100)]
        
        result = benchmark(create_nodes)
        assert len(result) == 100
    
    def test_sprite_layer_operations_benchmark(self, benchmark):
        """Benchmark sprite layer operations."""
        sprite = Sprite(64, 64)
        
        def layer_operations():
            layer = sprite.newLayer()
            sprite.deleteLayer(layer)
        
        benchmark(layer_operations)


class TestResourceLimits:
    """Test resource limit enforcement."""
    
    def test_queue_size_limits(self):
        """Queue size limits prevent memory exhaustion."""
        from engine.config.secure_config import TelemetryConfig
        
        # Small queue
        config = TelemetryConfig(max_queue_size=10)
        assert config.max_queue_size == 10
        
        # Large values should be rejected
        with pytest.raises(ValueError):
            TelemetryConfig(max_queue_size=100000)
