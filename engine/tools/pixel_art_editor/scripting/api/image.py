# /**************************************************************************/
# /*  api/image.py                                                          */
# /**************************************************************************/

"""Image-related classes for Aseprite API."""

from __future__ import annotations

from typing import Dict, List, Optional, TYPE_CHECKING
from PIL import Image as PILImage

import logging


logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    from .color import Color, ColorMode


class ColorSpace:
    """Color space representation."""
    
    def __init__(self, name: str = "sRGB"):
        self.name = name
    
    @staticmethod
    def sRGB() -> "ColorSpace":
        return ColorSpace("sRGB")


class ImageSpec:
    """Image specification for creating images."""
    
    def __init__(self, width: int = 0, height: int = 0, colorMode: int = 0, 
                 transparentColor: int = 0, bitsPerPixel: int = 32):
        self.width = width
        self.height = height
        self.colorMode = colorMode
        self.transparentColor = transparentColor
        self.bitsPerPixel = bitsPerPixel


class Image:
    """Aseprite Image class."""
    _id_counter = 0
    
    def __init__(self, width: int, height: int, color_mode: "ColorMode" = None):
        from .color import ColorMode, Color
        if color_mode is None:
            color_mode = ColorMode.RGB
        self.width = width
        self.height = height
        self.colorMode = color_mode
        self._pixels: Dict[tuple[int, int], "Color"] = {}
        Image._id_counter += 1
        self.id = Image._id_counter
        self.rowStride = width * 4  # 4 bytes per pixel (RGBA)
        self.image = None  # PIL Image reference
    
    @classmethod
    def from_pil(cls, pil_image: PILImage.Image) -> "Image":
        """Create Image from PIL Image."""
        from .color import Color
        pil_image = pil_image.convert("RGBA")
        img = cls(pil_image.width, pil_image.height)
        for y in range(img.height):
            for x in range(img.width):
                r, g, b, a = pil_image.getpixel((x, y))
                if a or r or g or b:
                    img._pixels[(x, y)] = Color(r, g, b, a)
        return img
    
    def to_pil(self) -> PILImage.Image:
        """Convert to PIL Image."""
        img = PILImage.new("RGBA", (self.width, self.height))
        for (x, y), c in self._pixels.items():
            img.putpixel((x, y), (c.r, c.g, c.b, c.a))
        return img
    
    def getPixel(self, x: int, y: int) -> int:
        """Get pixel color as integer."""
        if 0 <= x < self.width and 0 <= y < self.height:
            pixel = self._pixels.get((x, y))
            return int(pixel) if pixel is not None else 0
        return 0
    
    def putPixel(self, x: int, y: int, color: int) -> None:
        """Set pixel color from integer."""
        from .color import Color
        if 0 <= x < self.width and 0 <= y < self.height:
            if color == 0:
                self._pixels.pop((x, y), None)
            else:
                self._pixels[(x, y)] = Color.from_int(color)
    
    def clear(self, color: int) -> None:
        """Clear image with color."""
        from .color import Color
        c = Color.from_int(color)
        self._pixels.clear()
        if color:
            for y in range(self.height):
                for x in range(self.width):
                    self._pixels[(x, y)] = c
    
    def drawPixel(self, x: int, y: int, color: "Color") -> None:
        """Draw a pixel."""
        if 0 <= x < self.width and 0 <= y < self.height:
            if int(color) == 0:
                self._pixels.pop((x, y), None)
            else:
                self._pixels[(x, y)] = color
    
    def drawLine(self, x0: int, y0: int, x1: int, y1: int, color: "Color") -> None:
        """Draw a line using Bresenham's algorithm."""
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        while True:
            self.drawPixel(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
    
    def drawRect(self, x: int, y: int, w: int, h: int, color: "Color") -> None:
        """Draw a rectangle outline."""
        for i in range(w):
            self.drawPixel(x + i, y, color)
            self.drawPixel(x + i, y + h - 1, color)
        for j in range(h):
            self.drawPixel(x, y + j, color)
            self.drawPixel(x + w - 1, y + j, color)


class Cel:
    """Aseprite Cel class (represents a cell in a layer/frame)."""
    
    def __init__(self, image: Image, frame: int = 1):
        self.image = image
        self.frame = frame
