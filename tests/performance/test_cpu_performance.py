# /**************************************************************************/
# /*  test_cpu_performance.py                                               */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""CPU performance and optimization tests.

Tests algorithmic complexity, cache efficiency, and computational performance.
"""

import time
import pytest

from engine.core.node_base import Node
from engine.core.uid_registry import UIDRegistry
from engine.tools.pixel_art_editor.scripting.api.sprite import Sprite


class TestAlgorithmicComplexity:
    """Test Big-O performance characteristics."""
    
    def test_node_lookup_o1(self):
        """Node lookup should be O(1) with proper indexing."""
        # Create hierarchy
        root = Node("Root")
        children = [Node(f"Child{i}") for i in range(1000)]
        for child in children:
            root.add_child(child)
        
        # Time lookups
        start = time.time()
        for i in range(100):
            _ = root.get_child(f"Child{i % 1000}")
        elapsed = time.time() - start
        
        # Should be fast (O(1) average case)
        assert elapsed < 0.01, f"Node lookup too slow: {elapsed:.4f}s"
    
    def test_uid_generation_performance(self):
        """UID generation scales well."""
        start = time.time()
        
        uids = [UIDRegistry.generate("Node2D") for _ in range(10000)]
        
        elapsed = time.time() - start
        
        # Should generate 10k UIDs quickly
        assert elapsed < 1.0, f"UID generation too slow: {elapsed:.2f}s"
        
        # All should be unique
        assert len(set(uids)) == len(uids)
    
    def test_sprite_layer_operations_scale(self):
        """Layer operations scale linearly."""
        sprite = Sprite(32, 32)
        
        # Add many layers
        start = time.time()
        layers = [sprite.newLayer(f"Layer{i}") for i in range(100)]
        add_time = time.time() - start
        
        # Delete all layers
        start = time.time()
        for layer in layers[1:]:  # Keep at least one
            sprite.deleteLayer(layer)
        delete_time = time.time() - start
        
        # Both should be reasonably fast
        assert add_time < 0.5, f"Layer addition too slow: {add_time:.2f}s"
        assert delete_time < 0.5, f"Layer deletion too slow: {delete_time:.2f}s"


class TestCacheEfficiency:
    """Test caching and memoization performance."""
    
    def test_repeated_accesses_are_fast(self):
        """Repeated property accesses are cached."""
        sprite = Sprite(64, 64)
        
        # First access
        start = time.time()
        _ = sprite.layers
        first = time.time() - start
        
        # Repeated access
        start = time.time()
        for _ in range(1000):
            _ = sprite.layers
        repeated = time.time() - start
        
        # Repeated should be fast (uses cached wrapper)
        assert repeated < 0.1, f"Repeated access too slow: {repeated:.4f}s"


class TestStartupPerformance:
    """Test application startup times."""
    
    def test_project_creation_is_fast(self):
        """Project creation should be instant."""
        from engine.core.project_secure import SecureProject, ProjectConfig
        
        start = time.time()
        config = ProjectConfig(lazy_loading=True)
        project = SecureProject("Quick Start", config)
        elapsed = time.time() - start
        
        assert elapsed < 0.1, f"Project creation too slow: {elapsed:.3f}s"


class TestFrameRateStability:
    """Test frame rate stability under load."""
    
    def test_consistent_frametime(self):
        """Frame processing time should be consistent."""
        import statistics
        
        sprite = Sprite(128, 128)
        
        # Simulate frame processing
        times = []
        for _ in range(100):
            start = time.perf_counter()
            # Simulate some work
            _ = sprite.newLayer()
            elapsed = time.perf_counter() - start
            times.append(elapsed * 1000)  # Convert to ms
        
        # Check consistency
        mean_time = statistics.mean(times)
        stdev = statistics.stdev(times)
        
        # Standard deviation should be low (consistent)
        assert stdev / mean_time < 0.5, f"Frame times too variable: stdev={stdev:.2f}ms"


@pytest.mark.slow
class TestHeavyComputation:
    """Tests for heavy computational tasks."""
    
    def test_large_batch_operations(self):
        """Batch operations remain performant."""
        sprites = [Sprite(32, 32) for _ in range(100)]
        
        start = time.time()
        for sprite in sprites:
            for _ in range(10):
                sprite.newLayer()
        elapsed = time.time() - start
        
        # 100 sprites * 10 layers = 1000 layers
        assert elapsed < 2.0, f"Batch operations too slow: {elapsed:.2f}s"
