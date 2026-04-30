# /**************************************************************************/
# /*  test_stress_load.py                                                   */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Stress and heavy load testing.

Tests system behavior under extreme load conditions.
"""

import pytest
import asyncio
import time
import gc
import psutil
import os

from engine.core.node_base import Node
from engine.core.project_secure import SecureProject, ProjectConfig
from engine.tools.pixel_art_editor.scripting.api.sprite import Sprite


class TestNodeStress:
    """Stress tests for node system."""
    
    def test_massive_node_creation(self):
        """Create 10,000 nodes."""
        count = 10000
        
        start = time.time()
        nodes = [Node(f"Node{i}") for i in range(count)]
        elapsed = time.time() - start
        
        print(f"\nCreated {count} nodes in {elapsed:.2f}s")
        print(f"Rate: {count/elapsed:.0f} nodes/sec")
        
        assert len(nodes) == count
        assert elapsed < 10, "Node creation too slow"
        
        del nodes
        gc.collect()
    
    def test_deep_hierarchy(self):
        """Create extremely deep hierarchy."""
        depth = 1000
        
        root = Node("Root")
        current = root
        
        start = time.time()
        for i in range(depth):
            child = Node(f"Level{i}")
            current.add_child(child)
            current = child
        elapsed = time.time() - start
        
        print(f"\nCreated hierarchy of depth {depth} in {elapsed:.2f}s")
        
        # Verify depth by walking up
        current_depth = 0
        current = root
        while current.children:
            current = current.children[0]
            current_depth += 1
        
        assert current_depth == depth
    
    def test_wide_hierarchy(self):
        """Create node with 1000 children."""
        width = 1000
        
        parent = Node("Parent")
        
        start = time.time()
        for i in range(width):
            child = Node(f"Child{i}")
            parent.add_child(child)
        elapsed = time.time() - start
        
        print(f"\nAdded {width} children in {elapsed:.2f}s")
        
        assert len(parent.children) == width


class TestSpriteStress:
    """Stress tests for sprite system."""
    
    def test_massive_sprite_creation(self):
        """Create 1000 sprites."""
        count = 1000
        
        start = time.time()
        sprites = [Sprite(64, 64) for _ in range(count)]
        elapsed = time.time() - start
        
        print(f"\nCreated {count} sprites in {elapsed:.2f}s")
        
        assert len(sprites) == count
        assert elapsed < 5, "Sprite creation too slow"
        
        del sprites
        gc.collect()
    
    def test_large_sprite_dimensions(self):
        """Create sprites with extreme dimensions."""
        sizes = [
            (4096, 4096),
            (8192, 4096),
            (4096, 8192),
        ]
        
        for width, height in sizes:
            start = time.time()
            sprite = Sprite(width, height)
            elapsed = time.time() - start
            
            print(f"\nCreated {width}x{height} sprite in {elapsed:.2f}s")
            
            assert sprite.width == width
            assert sprite.height == height
    
    def test_many_layers_per_sprite(self):
        """Create sprite with many layers."""
        sprite = Sprite(32, 32)
        layer_count = 200
        
        start = time.time()
        for i in range(layer_count):
            sprite.newLayer(f"Layer{i}")
        elapsed = time.time() - start
        
        print(f"\nCreated {layer_count} layers in {elapsed:.2f}s")
        
        assert len(sprite.layers) >= layer_count
    
    def test_many_frames_per_sprite(self):
        """Create sprite with many frames."""
        sprite = Sprite(32, 32)
        frame_count = 500
        
        start = time.time()
        for _ in range(frame_count):
            sprite.newFrame()
        elapsed = time.time() - start
        
        print(f"\nCreated {frame_count} frames in {elapsed:.2f}s")
        
        assert len(sprite.frames) >= frame_count


@pytest.mark.asyncio
class TestProjectStress:
    """Stress tests for project system."""
    
    async def test_massive_scene_count(self):
        """Create project with 500 scenes."""
        config = ProjectConfig()
        project = SecureProject("stress-test", config)
        
        scene_count = 500
        
        start = time.time()
        for i in range(scene_count):
            project.create_scene(f"Scene {i}")
        elapsed = time.time() - start
        
        print(f"\nCreated {scene_count} scenes in {elapsed:.2f}s")
        
        assert len(project.scenes) == scene_count
    
    async def test_large_asset_registry(self):
        """Register many assets."""
        config = ProjectConfig(max_assets=10000)
        project = SecureProject("asset-stress", config)
        
        asset_count = 5000
        
        start = time.time()
        for i in range(asset_count):
            project.register_asset(f"asset{i}", f"path{i}.png", {"meta": i})
        elapsed = time.time() - start
        
        print(f"\nRegistered {asset_count} assets in {elapsed:.2f}s")
        
        assert len(project.assets) == asset_count


class TestMemoryUnderLoad:
    """Test memory behavior under heavy load."""
    
    def test_memory_stable_with_repeated_operations(self):
        """Memory doesn't grow unbounded."""
        import gc
        
        gc.collect()
        process = psutil.Process(os.getpid())
        baseline = process.memory_info().rss
        
        # Perform many allocations and deallocations
        for _ in range(100):
            sprites = [Sprite(64, 64) for _ in range(100)]
            for sprite in sprites:
                for _ in range(5):
                    sprite.newLayer()
            del sprites
        
        gc.collect()
        current = process.memory_info().rss
        
        # Should not grow more than 50%
        growth_ratio = current / baseline
        print(f"\nMemory: baseline={baseline/1024/1024:.1f}MB, current={current/1024/1024:.1f}MB")
        print(f"Growth ratio: {growth_ratio:.2f}x")
        
        # Allow some growth but not unbounded
        assert growth_ratio < 2.0, f"Memory grew too much: {growth_ratio:.2f}x"


class TestConcurrencyLoad:
    """Test concurrent operations."""
    
    @pytest.mark.asyncio
    async def test_concurrent_project_operations(self):
        """Multiple operations can run concurrently."""
        config = ProjectConfig()
        project = SecureProject("concurrent", config)
        
        async def create_scene_batch(start, count):
            for i in range(start, start + count):
                project.create_scene(f"Scene {i}")
            return count
        
        # Run multiple concurrent batch operations
        tasks = [
            create_scene_batch(0, 50),
            create_scene_batch(50, 50),
            create_scene_batch(100, 50),
            create_scene_batch(150, 50),
        ]
        
        results = await asyncio.gather(*tasks)
        
        assert sum(results) == 200
        assert len(project.scenes) == 200


class TestEndurance:
    """Long-running stress tests."""
    
    def test_sustained_operations(self):
        """Sustained operation for 5 seconds."""
        duration = 5.0
        start = time.time()
        iterations = 0
        
        while time.time() - start < duration:
            sprite = Sprite(32, 32)
            for _ in range(10):
                sprite.newLayer()
            iterations += 1
        
        elapsed = time.time() - start
        rate = iterations / elapsed
        
        print(f"\nCompleted {iterations} iterations in {elapsed:.2f}s")
        print(f"Rate: {rate:.0f} ops/sec")
        
        assert rate > 10, "Operations too slow"
