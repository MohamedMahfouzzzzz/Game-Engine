# /**************************************************************************/
# /*  test_node_system.py                                                   */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Engine core node system tests.

Tests the scene graph, node hierarchy, and tree operations.
"""

import pytest
from engine.core.node_base import Node, Node2D


class TestNodeBasics:
    """Test basic node operations."""
    
    def test_node_creation(self):
        """Node can be created with name."""
        node = Node("TestNode")
        assert node.name == "TestNode"
        assert node.uid is not None
        assert node.uid.startswith("GE-NO-")
    
    def test_node_uid_is_unique(self):
        """Each node gets unique UID."""
        node1 = Node("Node1")
        node2 = Node("Node2")
        assert node1.uid != node2.uid
    
    def test_node_default_values(self):
        """Node has sensible defaults."""
        node = Node("Default")
        assert node.visible is True
        assert node.processing is True
        assert node.parent is None
        assert len(node.children) == 0


class TestNodeHierarchy:
    """Test node tree operations."""
    
    def test_add_child(self):
        """Child can be added to node."""
        parent = Node("Parent")
        child = Node("Child")
        
        parent.add_child(child)
        
        assert child in parent.children
        assert child.parent is parent
    
    def test_remove_child(self):
        """Child can be removed from node."""
        parent = Node("Parent")
        child = Node("Child")
        parent.add_child(child)
        
        parent.remove_child(child)
        
        assert child not in parent.children
        assert child.parent is None
    
    def test_deep_hierarchy(self):
        """Can create deep node hierarchies."""
        root = Node("Root")
        current = root
        
        for i in range(50):
            child = Node(f"Level{i}")
            current.add_child(child)
            current = child
        
        # Walk back up
        depth = 0
        current = root
        while current.children:
            current = current.children[0]
            depth += 1
        
        assert depth == 50
    
    def test_multiple_children(self):
        """Node can have multiple children."""
        parent = Node("Parent")
        
        for i in range(10):
            child = Node(f"Child{i}")
            parent.add_child(child)
        
        assert len(parent.children) == 10
    
    def test_find_child(self):
        """Can find child by name."""
        parent = Node("Parent")
        child1 = Node("Child1")
        child2 = Node("Child2")
        
        parent.add_child(child1)
        parent.add_child(child2)
        
        found = parent.get_child("Child1")
        assert found is child1
    
    def test_find_child_not_found(self):
        """Returns None for non-existent child."""
        parent = Node("Parent")
        found = parent.get_child("NonExistent")
        assert found is None
    
    def test_reparenting(self):
        """Child can be moved between parents."""
        parent1 = Node("Parent1")
        parent2 = Node("Parent2")
        child = Node("Child")
        
        parent1.add_child(child)
        assert child.parent is parent1
        
        parent2.add_child(child)
        assert child.parent is parent2
        assert child not in parent1.children


class TestNode2D:
    """Test Node2D specific functionality."""
    
    def test_node2d_creation(self):
        """Node2D can be created with transform."""
        node = Node2D("Node2D")
        assert node.x == 0
        assert node.y == 0
        assert node.rotation == 0
        assert node.scale_x == 1
        assert node.scale_y == 1
    
    def test_node2d_transform(self):
        """Transform properties work correctly."""
        node = Node2D("Node")
        
        node.x = 100
        node.y = 200
        node.rotation = 45
        node.scale_x = 2
        node.scale_y = 0.5
        
        assert node.x == 100
        assert node.y == 200
        assert node.rotation == 45
        assert node.scale_x == 2
        assert node.scale_y == 0.5
    
    def test_node2d_uid_prefix(self):
        """Node2D has correct UID prefix."""
        node = Node2D("Test")
        assert node.uid.startswith("GE-N2D-")


class TestUIDRegistry:
    """Test UID generation and registry."""
    
    def test_generate_uid(self):
        """UID generation creates valid UIDs."""
        from engine.core.uid_registry import UIDRegistry
        
        uid = UIDRegistry.generate("Node")
        assert uid.startswith("GE-NO-")
        assert len(uid) > 10
    
    def test_generate_different_prefixes(self):
        """Different types get different prefixes."""
        from engine.core.uid_registry import UIDRegistry
        
        node_uid = UIDRegistry.generate("Node")
        node2d_uid = UIDRegistry.generate("Node2D")
        
        assert node_uid.startswith("GE-NO-")
        assert node2d_uid.startswith("GE-N2D-")
    
    def test_uid_collision_avoidance(self):
        """Generated UIDs should not collide."""
        from engine.core.uid_registry import UIDRegistry
        
        uids = [UIDRegistry.generate("Node") for _ in range(1000)]
        
        # All should be unique
        assert len(set(uids)) == len(uids)


class TestNodeSignals:
    """Test node signal system."""
    
    def test_node_has_signals(self):
        """Node has signal system."""
        node = Node("Test")
        # Signals should be accessible
        assert hasattr(node, 'signals') or hasattr(node, 'emit')
