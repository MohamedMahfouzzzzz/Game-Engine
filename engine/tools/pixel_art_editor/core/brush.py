# /**************************************************************************/
# /*  brush.py                                                              */
# /**************************************************************************/

"""Brush model for painting.

Equivalent to Aseprite's doc::Brush class.
"""

from typing import Tuple, Optional, List
from enum import IntEnum
from dataclasses import dataclass
from .image_buffer import ImageBuffer, ColorMode


class BrushType(IntEnum):
    """Brush types."""
    CIRCLE = 0
    SQUARE = 1
    LINE = 2
    IMAGE = 3
    PATTERN = 4


@dataclass
class BrushPoint:
    """A single point in a brush stamp."""
    x: int
    y: int
    color: Tuple[int, int, int, int]


class Brush:
    """A brush for painting on the canvas.
    
    Brushes have a shape (circle, square), size, and optional pattern.
    """
    
    _id_counter = 0
    
    def __init__(self, 
                 name: str = "Brush",
                 brush_type: BrushType = BrushType.CIRCLE,
                 size: int = 1):
        Brush._id_counter += 1
        self.id = Brush._id_counter
        self.name = name
        self.type = brush_type
        self.size = size  # Diameter for circle/square
        
        # Brush image (for custom brushes)
        self._image: Optional[ImageBuffer] = None
        
        # Pattern brush settings
        self.pattern: Optional[List[List[int]]] = None
        
        # Brush properties
        self.angle: float = 0.0  # Rotation angle
        self.opacity: float = 1.0  # Brush opacity
        
        # For textured brushes
        self._texture: Optional[ImageBuffer] = None
    
    @property
    def width(self) -> int:
        """Get brush width."""
        if self._image:
            return self._image.width
        return self.size
    
    @property
    def height(self) -> int:
        """Get brush height."""
        if self._image:
            return self._image.height
        return self.size
    
    def set_image(self, image: ImageBuffer) -> None:
        """Set custom brush image."""
        self._image = image
        self.type = BrushType.IMAGE
    
    def get_image(self) -> Optional[ImageBuffer]:
        """Get brush image if set."""
        return self._image
    
    def generate_stamp(self, color: Tuple[int, ...]) -> List[BrushPoint]:
        """Generate brush stamp points for given color.
        
        Returns list of points to paint.
        """
        points = []
        radius = self.size // 2
        
        if self.type == BrushType.CIRCLE:
            # Generate circle points
            for y in range(-radius, radius + 1):
                for x in range(-radius, radius + 1):
                    if x*x + y*y <= radius*radius:
                        # Apply brush opacity
                        r, g, b, a = color[:4]
                        a = int(a * self.opacity)
                        points.append(BrushPoint(x, y, (r, g, b, a)))
        
        elif self.type == BrushType.SQUARE:
            # Generate square points
            for y in range(-radius, radius + 1):
                for x in range(-radius, radius + 1):
                    r, g, b, a = color[:4]
                    a = int(a * self.opacity)
                    points.append(BrushPoint(x, y, (r, g, b, a)))
        
        elif self.type == BrushType.IMAGE and self._image:
            # Use image as brush shape
            for y in range(self._image.height):
                for x in range(self._image.width):
                    px = self._image.get_pixel(x, y)
                    if px[3] > 0:  # Non-transparent
                        # Blend brush color with brush image
                        r = int(color[0] * px[0] / 255)
                        g = int(color[1] * px[1] / 255)
                        b = int(color[2] * px[2] / 255)
                        a = int(color[3] * px[3] / 255 * self.opacity)
                        points.append(BrushPoint(
                            x - self._image.width // 2,
                            y - self._image.height // 2,
                            (r, g, b, a)
                        ))
        
        return points
    
    def get_bounds(self) -> Tuple[int, int, int, int]:
        """Get brush bounding box (width, height centered)."""
        w = self.width
        h = self.height
        return (-w // 2, -h // 2, w, h)
    
    def copy(self) -> 'Brush':
        """Create a copy of this brush."""
        new_brush = Brush(f"{self.name} copy", self.type, self.size)
        if self._image:
            new_brush._image = self._image.copy()
        new_brush.angle = self.angle
        new_brush.opacity = self.opacity
        new_brush.pattern = self.pattern
        return new_brush
    
    @classmethod
    def circle(cls, size: int, name: str = "Circle") -> 'Brush':
        """Create a circle brush."""
        return cls(name, BrushType.CIRCLE, size)
    
    @classmethod
    def square(cls, size: int, name: str = "Square") -> 'Brush':
        """Create a square brush."""
        return cls(name, BrushType.SQUARE, size)
    
    @classmethod
    def pixel(cls) -> 'Brush':
        """Create a single pixel brush (default)."""
        return cls("Pixel", BrushType.CIRCLE, 1)
