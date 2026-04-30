# /**************************************************************************/
# /*  test_algorithms.py                                                    */
# /**************************************************************************/

"""Unit tests for pixel art algorithms."""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engine.tools.pixel_art_editor.algorithms import (
    line_points, rectangle, ellipse, polygon,
    flood_fill_simple, magic_wand_select,
    apply_dither, DitherPattern, dither_patterns,
    quantize_colors, create_outline, desaturate
)


class TestLineDrawing(unittest.TestCase):
    """Test line drawing algorithms."""
    
    def test_horizontal_line(self):
        """Test horizontal line."""
        points = line_points(0, 0, 10, 0)
        self.assertEqual(len(points), 11)
        self.assertIn((0, 0), points)
        self.assertIn((10, 0), points)
    
    def test_vertical_line(self):
        """Test vertical line."""
        points = line_points(0, 0, 0, 10)
        self.assertEqual(len(points), 11)
        self.assertIn((0, 0), points)
        self.assertIn((0, 10), points)
    
    def test_diagonal_line(self):
        """Test diagonal line."""
        points = line_points(0, 0, 5, 5)
        self.assertEqual(len(points), 6)
        self.assertIn((0, 0), points)
        self.assertIn((5, 5), points)
    
    def test_steep_line(self):
        """Test steep diagonal."""
        points = line_points(0, 0, 2, 10)
        # Should have points for every y
        self.assertGreater(len(points), 5)


class TestRectangle(unittest.TestCase):
    """Test rectangle drawing."""
    
    def test_outline_rectangle(self):
        """Test outline rectangle."""
        points = set()
        rectangle(0, 0, 4, 4, lambda x, y: points.add((x, y)), filled=False)
        
        # Should have border pixels
        self.assertIn((0, 0), points)
        self.assertIn((4, 4), points)
        
        # Should NOT have center filled
        self.assertNotIn((2, 2), points)
    
    def test_filled_rectangle(self):
        """Test filled rectangle."""
        points = set()
        rectangle(0, 0, 4, 4, lambda x, y: points.add((x, y)), filled=True)
        
        # Should have 25 pixels (5x5)
        self.assertEqual(len(points), 25)
        
        # Should have center
        self.assertIn((2, 2), points)


class TestEllipse(unittest.TestCase):
    """Test ellipse drawing."""
    
    def test_ellipse_generation(self):
        """Test ellipse generates pixels."""
        points = set()
        ellipse(10, 10, 5, 3, lambda x, y: points.add((x, y)))
        
        # Should have reasonable number of pixels
        self.assertGreater(len(points), 10)
        
        # Should be roughly centered
        avg_x = sum(p[0] for p in points) / len(points)
        avg_y = sum(p[1] for p in points) / len(points)
        self.assertAlmostEqual(avg_x, 10, delta=2)
        self.assertAlmostEqual(avg_y, 10, delta=2)


class TestFloodFill(unittest.TestCase):
    """Test flood fill."""
    
    def test_flood_fill_simple(self):
        """Test simple flood fill."""
        # Create 10x10 grid
        grid = {}
        
        def get_pixel(x, y):
            return grid.get((x, y), (0, 0, 0, 255))
        
        def set_pixel(x, y, color):
            grid[(x, y)] = color
        
        # Fill region with red
        for x in range(3, 7):
            for y in range(3, 7):
                grid[(x, y)] = (255, 0, 0, 255)
        
        # Fill with blue
        filled = flood_fill_simple(
            5, 5, get_pixel, set_pixel,
            (255, 0, 0, 255), (0, 0, 255, 255),
            (0, 0, 10, 10)
        )
        
        # Should have filled the 4x4 region
        self.assertEqual(filled, 16)


class TestDithering(unittest.TestCase):
    """Test dithering."""
    
    def test_dither_patterns_exist(self):
        """Test dither patterns are available."""
        patterns = dither_patterns()
        self.assertIn('checkerboard', patterns)
        self.assertIn('bayer_4x4', patterns)
    
    def test_checkerboard_dither(self):
        """Test checkerboard pattern."""
        # At threshold 0.5, checkerboard should alternate
        results = [
            apply_dither(0, 0, 0.5, DitherPattern.CHECKERBOARD),
            apply_dither(1, 0, 0.5, DitherPattern.CHECKERBOARD),
            apply_dither(0, 1, 0.5, DitherPattern.CHECKERBOARD),
            apply_dither(1, 1, 0.5, DitherPattern.CHECKERBOARD),
        ]
        
        # Should have both True and False
        self.assertTrue(any(results))
        self.assertTrue(not all(results))
    
    def test_threshold_dither(self):
        """Test threshold pattern."""
        # Threshold 0.5: below should be False, above should be True
        self.assertFalse(apply_dither(0, 0, 0.3, DitherPattern.THRESHOLD))
        self.assertTrue(apply_dither(0, 0, 0.7, DitherPattern.THRESHOLD))


class TestColorOperations(unittest.TestCase):
    """Test color operations."""
    
    def test_quantize_colors(self):
        """Test color quantization."""
        # Create gradient colors
        colors = [(i, i, i, 255) for i in range(0, 256, 4)]  # 64 shades
        
        # Quantize to 16 colors
        quantized = quantize_colors(colors, 16)
        
        # Should have 16 or fewer colors
        self.assertLessEqual(len(quantized), 16)
    
    def test_create_outline(self):
        """Test outline creation."""
        # Create 2x2 shape
        shape = {(5, 5), (5, 6), (6, 5), (6, 6)}
        
        outline = create_outline(shape, (255, 0, 0, 255), width=1)
        
        # Should have outline pixels
        self.assertGreater(len(outline), 0)
    
    def test_desaturate(self):
        """Test desaturation."""
        red = (255, 0, 0, 255)
        gray = desaturate(red, factor=1.0)
        
        # Result should be grayscale (R=G=B)
        self.assertEqual(gray[0], gray[1])
        self.assertEqual(gray[1], gray[2])


if __name__ == '__main__':
    unittest.main()
