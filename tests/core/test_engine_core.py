# /**************************************************************************/
# /*  test_engine.py                                                        */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""
Comprehensive Test Suite for Game Engine Studio 2D
Tests all core functionality: Nodes, Physics, Rendering, Animation
"""

import unittest
import sys
import os
import zipfile

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Source'))

from engine.core.node import Node, Node2D, Scene, Project, NodeType, Transform2D
from engine.export.service import ExportService
from engine.interop.mapping_registry import MappingRegistry
from engine.scripting.abi import ScriptContext
from engine.scripting.host import ScriptHost


class TestNodeSystem(unittest.TestCase):
    """Test node system functionality"""
    
    def setUp(self):
        self.node = Node("TestNode")
    
    def test_node_creation(self):
        """Test node creation"""
        self.assertEqual(self.node.name, "TestNode")
        self.assertEqual(self.node.node_type, NodeType.NODE)
        self.assertIsNotNone(self.node.uid)
    
    def test_node_hierarchy(self):
        """Test parent-child relationships"""
        parent = Node("Parent")
        child = Node("Child")
        
        parent.add_child(child)
        
        self.assertEqual(child.parent, parent)
        self.assertIn(child, parent.children)
    
    def test_node_find_child(self):
        """Test finding child nodes"""
        parent = Node("Parent")
        child1 = Node("Child1")
        child2 = Node("Child2")
        
        parent.add_child(child1)
        parent.add_child(child2)
        
        found = parent.find_child("Child1")
        self.assertEqual(found, child1)
    
    def test_node_properties(self):
        """Test node properties"""
        self.node.set_property("health", 100)
        self.node.set_property("speed", 5.0)
        
        self.assertEqual(self.node.get_property("health"), 100)
        self.assertEqual(self.node.get_property("speed"), 5.0)
    
    def test_node_serialization(self):
        """Test node serialization"""
        self.node.set_property("test", "value")
        data = self.node.to_dict()
        
        self.assertEqual(data["name"], "TestNode")
        self.assertEqual(data["properties"]["test"], "value")


class TestNode2D(unittest.TestCase):
    """Test 2D node functionality"""
    
    def setUp(self):
        self.node = Node2D("TestNode2D")
    
    def test_node2d_creation(self):
        """Test Node2D creation"""
        self.assertEqual(self.node.node_type, NodeType.NODE2D)
        self.assertIsNotNone(self.node.transform)
    
    def test_transform_position(self):
        """Test position setting"""
        self.node.set_position(10.0, 20.0)
        pos = self.node.get_position()
        
        self.assertEqual(pos, (10.0, 20.0))
    
    def test_transform_rotation(self):
        """Test rotation setting"""
        import math
        self.node.set_rotation(math.pi / 4)
        
        self.assertAlmostEqual(self.node.get_rotation(), math.pi / 4)
    
    def test_transform_scale(self):
        """Test scale setting"""
        self.node.set_scale(2.0, 3.0)
        scale = self.node.get_scale()
        
        self.assertEqual(scale, (2.0, 3.0))


class TestScene(unittest.TestCase):
    """Test scene functionality"""
    
    def setUp(self):
        self.scene = Scene("TestScene")
    
    def test_scene_creation(self):
        """Test scene creation"""
        self.assertEqual(self.scene.name, "TestScene")
        self.assertIsNotNone(self.scene.root)
    
    def test_add_node_to_scene(self):
        """Test adding nodes to scene"""
        node = Node2D("TestNode")
        self.scene.add_node(node)
        
        self.assertIn(node.uid, self.scene.nodes)
        self.assertEqual(node.parent, self.scene.root)
    
    def test_remove_node_from_scene(self):
        """Test removing nodes from scene"""
        node = Node2D("TestNode")
        self.scene.add_node(node)
        self.scene.remove_node(node)
        
        self.assertNotIn(node.uid, self.scene.nodes)
    
    def test_get_node_from_scene(self):
        """Test getting node from scene"""
        node = Node2D("TestNode")
        self.scene.add_node(node)
        
        retrieved = self.scene.get_node(node.uid)
        self.assertEqual(retrieved, node)


class TestProject(unittest.TestCase):
    """Test project functionality"""
    
    def setUp(self):
        self.project = Project("TestProject")
    
    def test_project_creation(self):
        """Test project creation"""
        self.assertEqual(self.project.name, "TestProject")
        self.assertIsNotNone(self.project.id)
    
    def test_create_scene(self):
        """Test creating scenes"""
        scene = self.project.create_scene("Scene1")
        
        self.assertIn(scene.id, self.project.scenes)
        self.assertEqual(self.project.active_scene, scene)
    
    def test_multiple_scenes(self):
        """Test multiple scenes"""
        scene1 = self.project.create_scene("Scene1")
        scene2 = self.project.create_scene("Scene2")
        
        self.assertEqual(len(self.project.scenes), 2)
        self.assertIn(scene1.id, self.project.scenes)
        self.assertIn(scene2.id, self.project.scenes)
    
    def test_remove_scene(self):
        """Test removing scenes"""
        scene = self.project.create_scene("Scene1")
        self.project.remove_scene(scene.id)
        
        self.assertNotIn(scene.id, self.project.scenes)


class TestTransform2D(unittest.TestCase):
    """Test 2D transform functionality"""
    
    def setUp(self):
        self.transform = Transform2D()
    
    def test_transform_creation(self):
        """Test transform creation"""
        self.assertEqual(self.transform.position, (0.0, 0.0))
        self.assertEqual(self.transform.rotation, 0.0)
        self.assertEqual(self.transform.scale, (1.0, 1.0))
    
    def test_transform_matrix(self):
        """Test transformation matrix"""
        matrix = self.transform.get_matrix()
        
        self.assertIsNotNone(matrix)
        self.assertEqual(len(matrix), 3)
        self.assertEqual(len(matrix[0]), 3)


class TestPipelineFeatures(unittest.TestCase):
    def test_export_service_targets(self):
        project = Project("ExportProject")
        service = ExportService()
        results = service.export_all(project, os.path.join(os.getcwd(), "tmp_exports"))
        self.assertIn("windows", results)
        self.assertIn("linux", results)
        self.assertTrue(results["windows"].endswith(".zip"))
        with zipfile.ZipFile(results["windows"], "r") as zf:
            names = set(zf.namelist())
            self.assertIn("manifest.json", names)
            self.assertIn("checksums.sha256", names)

    def test_mapping_registry(self):
        registry = MappingRegistry()
        report = registry.compatibility_report()
        self.assertGreaterEqual(report["node_types"], 1)

    def test_script_host(self):
        host = ScriptHost()
        context = ScriptContext(node_id="n1", scene_id="s1", properties={})
        result = host.execute("gdlang", "var hp=100", context)
        self.assertEqual(result["hp"], 100)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestNodeSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestNode2D))
    suite.addTests(loader.loadTestsFromTestCase(TestScene))
    suite.addTests(loader.loadTestsFromTestCase(TestProject))
    suite.addTests(loader.loadTestsFromTestCase(TestTransform2D))
    suite.addTests(loader.loadTestsFromTestCase(TestPipelineFeatures))
    # Optional soak test file can be run separately to keep this suite fast.
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)




