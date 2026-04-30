# /**************************************************************************/
# /*  test_brushes.py                                                       */
# /**************************************************************************/

"""Unit tests for brush system."""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engine.tools.pixel_art_editor.brushes import (
    BrushManager, BrushPresets, PressureCurve
)
from engine.tools.pixel_art_editor.brushes.pressure_curve import (
    CurveType, BrushDynamics
)
from engine.tools.pixel_art_editor.core import Brush, BrushType


class TestBrushManager(unittest.TestCase):
    """Test BrushManager."""
    
    def setUp(self):
        self.manager = BrushManager()
    
    def test_initial_state(self):
        """Test initial state."""
        categories = self.manager.get_categories()
        self.assertEqual(len(categories), 0)
    
    def test_create_category(self):
        """Test creating category."""
        category = self.manager.create_category('Test Category')
        self.assertIsNotNone(category)
        self.assertEqual(category.name, 'Test Category')
        self.assertIn('Test Category', self.manager.get_categories())
    
    def test_add_brush(self):
        """Test adding brush."""
        self.manager.create_category('Test')
        brush = Brush.circle(8, 'TestBrush')
        
        result = self.manager.add_brush(brush, 'Test')
        self.assertTrue(result)
        
        # Verify brush was added
        all_brushes = self.manager.get_all_brushes()
        self.assertEqual(len(all_brushes['Test']), 1)
    
    def test_get_brush(self):
        """Test getting brush."""
        self.manager.create_category('Test')
        brush = Brush.circle(8, 'TestBrush')
        self.manager.add_brush(brush, 'Test')
        
        retrieved = self.manager.get_brush('TestBrush')
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, 'TestBrush')
    
    def test_get_brush_not_found(self):
        """Test getting non-existent brush."""
        brush = self.manager.get_brush('NonExistent')
        self.assertIsNone(brush)


class TestBrushPresets(unittest.TestCase):
    """Test brush presets."""
    
    def setUp(self):
        self.manager = BrushManager()
    
    def test_register_all(self):
        """Test registering all presets."""
        BrushPresets.register_all_to_manager(self.manager)
        
        # Should have multiple categories
        categories = self.manager.get_categories()
        self.assertGreater(len(categories), 0)
        
        # Should have brushes
        all_brushes = self.manager.get_all_brushes()
        total = sum(len(b) for b in all_brushes.values())
        self.assertGreater(total, 10)
    
    def test_preset_brushes_exist(self):
        """Test specific preset brushes exist."""
        BrushPresets.register_all_to_manager(self.manager)
        
        # Check for expected brushes
        self.assertIsNotNone(self.manager.get_brush('Pencil'))
        self.assertIsNotNone(self.manager.get_brush('Pen'))
        self.assertIsNotNone(self.manager.get_brush('Eraser'))


class TestPressureCurve(unittest.TestCase):
    """Test pressure curves."""
    
    def test_linear_curve(self):
        """Test linear pressure curve."""
        curve = PressureCurve.linear()
        
        # Test bounds
        self.assertEqual(curve.map(0.0), 0.0)
        self.assertEqual(curve.map(1.0), 1.0)
        
        # Test middle
        self.assertAlmostEqual(curve.map(0.5), 0.5, places=5)
    
    def test_quadratic_curve(self):
        """Test quadratic pressure curve."""
        curve = PressureCurve.quadratic()
        
        # Quadratic should be below linear at middle
        linear_mid = 0.5
        quad_mid = curve.map(0.5)
        self.assertLess(quad_mid, linear_mid)
    
    def test_s_curve(self):
        """Test S-curve."""
        curve = PressureCurve.s_curve()
        
        # Should map 0->0 and 1->1
        self.assertEqual(curve.map(0.0), 0.0)
        self.assertEqual(curve.map(1.0), 1.0)
        
        # Middle should be near 0.5
        mid = curve.map(0.5)
        self.assertGreater(mid, 0.4)
        self.assertLess(mid, 0.6)


class TestBrushDynamics(unittest.TestCase):
    """Test brush dynamics."""
    
    def test_initial_state(self):
        """Test initial state."""
        dynamics = BrushDynamics()
        self.assertTrue(dynamics.size_enabled)
        self.assertTrue(dynamics.opacity_enabled)
    
    def test_apply_dynamics(self):
        """Test applying dynamics to brush."""
        dynamics = BrushDynamics()
        dynamics.min_size = 1.0
        dynamics.max_size = 10.0
        
        brush = Brush.circle(10, 'Test')
        
        # Apply with 50% pressure
        dynamics.apply(brush, 0.5)
        
        # Size should be between min and max
        self.assertGreaterEqual(brush.size, 1.0)
        self.assertLessEqual(brush.size, 10.0)


if __name__ == '__main__':
    unittest.main()
