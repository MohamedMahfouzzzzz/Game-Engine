# /**************************************************************************/
# /*  brush_presets.py                                                      */
# /**************************************************************************/

"""Pre-defined brush presets.

Includes pixel art optimized brushes like:
- Perfect circles at various sizes
- Square brushes
- Dither patterns
- Texture brushes
"""

from typing import List
from engine.tools.pixel_art_editor.core.brush import Brush, BrushType


class BrushPresets:
    """Collection of pre-defined brush presets."""
    
    @staticmethod
    def get_pixel_brush() -> Brush:
        """Get single pixel brush."""
        return Brush.pixel()
    
    @staticmethod
    def get_circle_brushes() -> List[Brush]:
        """Get set of circle brushes (1-32px)."""
        brushes = []
        sizes = [1, 2, 3, 4, 5, 6, 8, 10, 12, 14, 16, 20, 24, 28, 32]
        for size in sizes:
            brush = Brush.circle(size, f"Circle {size}px")
            brushes.append(brush)
        return brushes
    
    @staticmethod
    def get_square_brushes() -> List[Brush]:
        """Get set of square brushes (1-32px)."""
        brushes = []
        sizes = [1, 2, 3, 4, 5, 6, 8, 10, 12, 14, 16, 20, 24, 28, 32]
        for size in sizes:
            brush = Brush.square(size, f"Square {size}px")
            brushes.append(brush)
        return brushes
    
    @staticmethod
    def get_dither_brush(pattern: str = "checker") -> Brush:
        """Get dither pattern brush.
        
        Patterns: checker, stripes, dots, gradient
        """
        brush = Brush(f"Dither {pattern}", BrushType.PATTERN, 8)
        
        # Create pattern matrix
        if pattern == "checker":
            brush.pattern = [
                [1, 0, 1, 0],
                [0, 1, 0, 1],
                [1, 0, 1, 0],
                [0, 1, 0, 1],
            ]
        elif pattern == "stripes":
            brush.pattern = [
                [1, 1, 0, 0],
                [1, 1, 0, 0],
                [1, 1, 0, 0],
                [1, 1, 0, 0],
            ]
        elif pattern == "dots":
            brush.pattern = [
                [1, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 0],
            ]
        elif pattern == "gradient":
            brush.pattern = [
                [0.25, 0.5, 0.75, 1.0],
                [0.5, 0.75, 1.0, 0.75],
                [0.75, 1.0, 0.75, 0.5],
                [1.0, 0.75, 0.5, 0.25],
            ]
        
        return brush
    
    @staticmethod
    def get_soft_brush(size: int = 8) -> Brush:
        """Get soft/anti-aliased brush for smooth edges."""
        brush = Brush(f"Soft {size}px", BrushType.CIRCLE, size)
        # Soft brushes have partial opacity at edges
        brush.opacity = 0.8
        return brush
    
    @staticmethod
    def get_line_brush(width: int = 1) -> Brush:
        """Get line brush for drawing lines."""
        brush = Brush(f"Line {width}px", BrushType.LINE, width)
        return brush
    
    @classmethod
    def register_all_to_manager(cls, manager) -> None:
        """Register all presets to a brush manager."""
        # Circle brushes
        for brush in cls.get_circle_brushes():
            manager.add_brush("Basic", brush)
        
        # Square brushes
        for brush in cls.get_square_brushes():
            manager.add_brush("Basic", brush)
        
        # Pixel brush
        manager.add_brush("Pixels", cls.get_pixel_brush())
        
        # Dither brushes
        for pattern in ["checker", "stripes", "dots", "gradient"]:
            manager.add_brush("Pixels", cls.get_dither_brush(pattern))
        
        # Soft brushes
        for size in [4, 8, 12, 16]:
            manager.add_brush("Artistic", cls.get_soft_brush(size))
