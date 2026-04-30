# /**************************************************************************/
# /*  test_edge_cases.py                                                    */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Edge case and boundary condition tests.

Tests extreme and unusual input conditions.
"""

import pytest

from engine.core.node_base import Node
from engine.tools.pixel_art_editor.scripting.api.sprite import Sprite
from engine.tools.pixel_art_editor.scripting.api.color import Color


class TestBoundaryValues:
    """Test behavior at boundary values."""
    
    def test_minimum_sprite_size(self):
        """Sprite with size 1x1."""
        sprite = Sprite(1, 1)
        assert sprite.width == 1
        assert sprite.height == 1
    
    def test_zero_size_sprite(self):
        """Sprite with zero dimensions should handle gracefully."""
        # Should either reject or handle gracefully
        try:
            sprite = Sprite(0, 0)
            # If allowed, check it doesn't crash
            assert sprite.width == 0 or sprite.width == 1
        except ValueError:
            pass  # Rejection is acceptable
    
    def test_very_long_name(self):
        """Node with extremely long name."""
        long_name = "A" * 10000
        node = Node(long_name)
        assert node.name == long_name
    
    def test_special_characters_in_name(self):
        """Node names with special characters."""
        special_names = [
            "Node/with/slashes",
            "Node\\with\\backslashes",
            "Node with spaces",
            "Node\twith\ttabs",
            "Node\nwith\nnewlines",
            "Node\x00with\x00nulls",
            "Node表情",
            "Node🎮",
        ]
        
        for name in special_names:
            node = Node(name)
            assert node.name == name
    
    def test_unicode_names(self):
        """Unicode in node names."""
        names = [
            "Node表情",
            "Node🎮",
            "Nœud",
            "Узел",
            "नोड",
            "ノード",
        ]
        
        for name in names:
            node = Node(name)
            assert node.name == name


class TestEmptyCollections:
    """Test behavior with empty collections."""
    
    def test_empty_children_iteration(self):
        """Iterating empty children list."""
        node = Node("Empty")
        count = 0
        for child in node.children:
            count += 1
        assert count == 0
    
    def test_empty_sprite_layers(self):
        """Sprite always has at least one layer."""
        sprite = Sprite(32, 32)
        assert len(sprite.layers) >= 1
    
    def test_empty_sprite_frames(self):
        """Sprite always has at least one frame."""
        sprite = Sprite(32, 32)
        assert len(sprite.frames) >= 1


class TestCircularReferences:
    """Test circular reference handling."""
    
    def test_self_parent(self):
        """Node cannot be its own parent."""
        node = Node("Self")
        
        with pytest.raises((ValueError, RuntimeError)):
            node.add_child(node)
    
    def test_circular_parent_child(self):
        """Prevent circular parent-child relationships."""
        a = Node("A")
        b = Node("B")
        c = Node("C")
        
        a.add_child(b)
        b.add_child(c)
        
        # Trying to make C parent of A should fail
        with pytest.raises((ValueError, RuntimeError)):
            c.add_child(a)


class TestColorEdgeCases:
    """Edge cases for color operations."""
    
    def test_color_values_at_bounds(self):
        """Color values at 0 and 255."""
        black = Color(0, 0, 0)
        white = Color(255, 255, 255)
        
        assert black.r == 0
        assert white.r == 255
    
    def test_color_values_out_of_range(self):
        """Color values outside 0-255 range."""
        # Should clamp or handle gracefully
        try:
            color = Color(300, -50, 1000)
            # If allowed, check clamping
            assert color.r >= 0 and color.r <= 255
        except ValueError:
            pass  # Rejection is acceptable
    
    def test_transparent_color(self):
        """Fully transparent color."""
        color = Color(255, 255, 255, 0)
        assert color.a == 0


class TestNumericEdgeCases:
    """Test numeric edge cases."""
    
    def test_float_dimensions(self):
        """Sprite with float dimensions."""
        # Should convert to int or reject
        sprite = Sprite(32.7, 64.3)
        
        # Check dimensions are integers
        assert isinstance(sprite.width, int)
        assert isinstance(sprite.height, int)
    
    def test_negative_dimensions(self):
        """Sprite with negative dimensions."""
        with pytest.raises(ValueError):
            Sprite(-32, -64)


class TestConcurrentModifications:
    """Test concurrent modification scenarios."""
    
    def test_modify_while_iterating(self):
        """Modifying children while iterating."""
        parent = Node("Parent")
        
        for i in range(10):
            parent.add_child(Node(f"Child{i}"))
        
        # This should handle gracefully or raise appropriate error
        try:
            for child in parent.children:
                parent.remove_child(child)
        except RuntimeError:
            pass  # Expected behavior for concurrent modification


class TestResourceExhaustion:
    """Test near-resource-exhaustion scenarios."""
    
    @pytest.mark.slow
    def test_near_memory_limit(self):
        """Behavior near memory limits (simulated)."""
        # This test should be run with memory monitoring
        # Create as many sprites as possible
        sprites = []
        
        try:
            for i in range(10000):
                sprite = Sprite(256, 256)
                sprites.append(sprite)
                
                if i % 1000 == 0:
                    print(f"Created {i} sprites")
                    
        except MemoryError:
            # Expected at some point
            print(f"Memory limit reached at {len(sprites)} sprites")
            pass
        
        # Should have created at least some sprites
        assert len(sprites) > 0


class TestNullAndNone:
    """Test null/none handling."""
    
    def test_null_parent(self):
        """Node with null parent."""
        node = Node("Orphan")
        assert node.parent is None
    
    def test_remove_null_child(self):
        """Removing non-existent child."""
        parent = Node("Parent")
        non_child = Node("NotAChild")
        
        # Should handle gracefully
        parent.remove_child(non_child)
        # Should not crash
