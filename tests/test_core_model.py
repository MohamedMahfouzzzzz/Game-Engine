# /**************************************************************************/
# /*  test_core_model.py                                                    */
# /**************************************************************************/

"""Unit tests for core model classes."""

import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engine.tools.pixel_art_editor.core import (
    Document, Sprite, Layer, LayerGroup, Cel, LinkedCel,
    ImageBuffer, Palette, Brush, BrushType, Tag, TagRepeat,
    BlendMode, ColorMode, Frame
)


class TestBlendMode(unittest.TestCase):
    """Test BlendMode enum."""
    
    def test_values(self):
        """Test enum values are sequential."""
        self.assertEqual(BlendMode.NORMAL.value, 0)
        self.assertEqual(BlendMode.MULTIPLY.value, 1)
        self.assertEqual(BlendMode.SCREEN.value, 2)
        self.assertEqual(BlendMode.OVERLAY.value, 3)
    
    def test_is_intenum(self):
        """Test BlendMode is IntEnum for binary compatibility."""
        # Should be comparable to int
        self.assertEqual(int(BlendMode.NORMAL), 0)


class TestDocument(unittest.TestCase):
    """Test Document class."""
    
    def setUp(self):
        self.doc = Document(64, 64, 'TestDoc')
    
    def test_initial_dimensions(self):
        """Test document has correct initial dimensions."""
        self.assertEqual(self.doc.width, 64)
        self.assertEqual(self.doc.height, 64)
        self.assertEqual(self.doc.name, 'TestDoc')
    
    def test_default_layers(self):
        """Test document has default layer."""
        self.assertEqual(self.doc.sprite.layer_count, 1)
        self.assertIsNotNone(self.doc.sprite.get_layer(0))
    
    def test_add_layer(self):
        """Test adding layers."""
        layer = self.doc.sprite.add_layer('New Layer')
        self.assertEqual(self.doc.sprite.layer_count, 2)
        self.assertEqual(layer.name, 'New Layer')
    
    def test_add_frame(self):
        """Test adding frames."""
        self.doc.sprite.add_frame(100)
        self.assertEqual(self.doc.sprite.frame_count, 2)
    
    def test_metadata(self):
        """Test document metadata."""
        self.doc.author = 'Test Author'
        self.doc.description = 'Test Description'
        self.assertEqual(self.doc.author, 'Test Author')
        self.assertEqual(self.doc.description, 'Test Description')


class TestImageBuffer(unittest.TestCase):
    """Test ImageBuffer class."""
    
    def setUp(self):
        self.buffer = ImageBuffer(32, 32, ColorMode.RGBA)
    
    def test_dimensions(self):
        """Test buffer dimensions."""
        self.assertEqual(self.buffer.width, 32)
        self.assertEqual(self.buffer.height, 32)
        self.assertEqual(self.buffer.get_pixel_count(), 32 * 32)
    
    def test_pixel_operations(self):
        """Test pixel get/set."""
        color = (255, 128, 64, 255)
        self.buffer.set_pixel(10, 10, color)
        result = self.buffer.get_pixel(10, 10)
        self.assertEqual(result, color)
    
    def test_out_of_bounds(self):
        """Test out-of-bounds access returns transparent."""
        result = self.buffer.get_pixel(100, 100)
        self.assertEqual(result, (0, 0, 0, 0))
    
    def test_clear(self):
        """Test clearing buffer."""
        self.buffer.set_pixel(5, 5, (255, 255, 255, 255))
        self.buffer.clear((0, 0, 0, 0))
        result = self.buffer.get_pixel(5, 5)
        self.assertEqual(result, (0, 0, 0, 0))
    
    def test_is_empty(self):
        """Test is_empty check."""
        # New buffer should be empty (transparent)
        self.assertTrue(self.buffer.is_empty())
        
        # Set a pixel
        self.buffer.set_pixel(0, 0, (255, 0, 0, 255))
        self.assertFalse(self.buffer.is_empty())
    
    def test_copy(self):
        """Test copying buffer."""
        self.buffer.set_pixel(5, 5, (255, 0, 0, 255))
        copy = self.buffer.copy()
        
        self.assertEqual(copy.width, self.buffer.width)
        self.assertEqual(copy.height, self.buffer.height)
        self.assertEqual(copy.get_pixel(5, 5), (255, 0, 0, 255))


class TestBrush(unittest.TestCase):
    """Test Brush class."""
    
    def test_circle_creation(self):
        """Test creating circle brush."""
        brush = Brush.circle(8, 'Circle8')
        self.assertEqual(brush.type, BrushType.CIRCLE)
        self.assertEqual(brush.size, 8)
        self.assertEqual(brush.name, 'Circle8')
    
    def test_square_creation(self):
        """Test creating square brush."""
        brush = Brush.square(4, 'Square4')
        self.assertEqual(brush.type, BrushType.SQUARE)
        self.assertEqual(brush.size, 4)
    
    def test_brush_preview(self):
        """Test brush preview generation."""
        brush = Brush.circle(4, 'Test')
        preview = brush.get_preview()
        self.assertIsNotNone(preview)


class TestTag(unittest.TestCase):
    """Test Tag class."""
    
    def test_tag_creation(self):
        """Test creating tag."""
        tag = Tag('Walk', 0, 5, (255, 0, 0), TagRepeat.FORWARD)
        self.assertEqual(tag.name, 'Walk')
        self.assertEqual(tag.from_frame, 0)
        self.assertEqual(tag.to_frame, 5)
        self.assertEqual(tag.repeat.value, TagRepeat.FORWARD.value)


class TestLayer(unittest.TestCase):
    """Test Layer class."""
    
    def test_layer_properties(self):
        """Test layer properties."""
        layer = Layer(1, 'Test Layer')
        self.assertEqual(layer.name, 'Test Layer')
        self.assertEqual(layer.layer_id, 1)
        self.assertEqual(layer.opacity, 255)
        self.assertEqual(layer.blend_mode, BlendMode.NORMAL)
    
    def test_layer_visibility(self):
        """Test layer visibility."""
        layer = Layer(1, 'Test')
        self.assertTrue(layer.is_visible)
        
        layer.is_visible = False
        self.assertFalse(layer.is_visible)


class TestFrame(unittest.TestCase):
    """Test Frame class."""
    
    def test_frame_duration(self):
        """Test frame duration."""
        frame = Frame(0, 100)
        self.assertEqual(frame.duration_ms, 100)
        
        frame.set_duration(200)
        self.assertEqual(frame.duration_ms, 200)


if __name__ == '__main__':
    unittest.main()
