# /**************************************************************************/
# /*  image_buffer.py                                                       */
# /**************************************************************************/

"""Image buffer for pixel data storage (RGBA)."""

from dataclasses import dataclass
from typing import Tuple, Optional, List
from PIL import Image
from enum import IntEnum

# Optional numpy for performance
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None


class ColorMode(IntEnum):
    """Color mode for image data."""
    RGBA = 0       # 32-bit RGBA
    GRAYSCALE = 1  # 8-bit grayscale
    INDEXED = 2    # Indexed color (palette-based)


@dataclass(slots=True)
class PixelDelta:
    """Single-pixel change used for compact undo and dirty tracking."""
    x: int
    y: int
    before: Tuple[int, ...]
    after: Tuple[int, ...]


def merge_rect(a: Optional[Tuple[int, int, int, int]], b: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
    """Merge two x/y/w/h rectangles."""
    if a is None:
        return b
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    x1 = min(ax, bx)
    y1 = min(ay, by)
    x2 = max(ax + aw, bx + bw)
    y2 = max(ay + ah, by + bh)
    return (x1, y1, x2 - x1, y2 - y1)


class ImageBuffer:
    """Low-level image data storage.
    
    Equivalent to Aseprite's doc::Image class.
    Stores raw pixel data in a memory-efficient format.
    Uses PIL Image as primary storage, with optional numpy for performance.
    """
    
    def __init__(self, width: int, height: int, mode: ColorMode = ColorMode.RGBA):
        self.width = width
        self.height = height
        self.mode = mode
        
        # Allocate lazily. Empty cels dominate editor memory, especially for
        # large sprites and animation timelines.
        self._image: Optional[Image.Image] = None
        self.dirty_rect: Optional[Tuple[int, int, int, int]] = None
        
        # Optional numpy array for batch operations
        self._data = None
        self._needs_sync = False

    def _new_empty_image(self) -> Image.Image:
        if self.mode == ColorMode.RGBA:
            return Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        if self.mode == ColorMode.GRAYSCALE:
            return Image.new('L', (self.width, self.height), 0)
        return Image.new('P', (self.width, self.height), 0)

    def _ensure_image(self) -> Image.Image:
        if self._image is None:
            self._image = self._new_empty_image()
        return self._image
    
    def get_pixel(self, x: int, y: int) -> Tuple[int, ...]:
        """Get pixel at position."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            if self.mode == ColorMode.RGBA:
                return (0, 0, 0, 0)
            return (0,)
        
        if self._image is None:
            if self.mode == ColorMode.RGBA:
                return (0, 0, 0, 0)
            return (0,)
        return self._image.getpixel((x, y))
    
    def set_pixel(self, x: int, y: int, color: Tuple[int, ...]) -> Optional[PixelDelta]:
        """Set pixel at position."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return None
        
        image = self._ensure_image()
        before = image.getpixel((x, y))
        after = color[:4] if self.mode == ColorMode.RGBA else (color[0],)
        if before == after:
            return None
        image.putpixel((x, y), after if self.mode == ColorMode.RGBA else after[0])
        self.dirty_rect = merge_rect(self.dirty_rect, (x, y, 1, 1))
        self._needs_sync = True
        return PixelDelta(x, y, before if isinstance(before, tuple) else (before,), after)
    
    def clear(self, color: Tuple[int, ...] = (0, 0, 0, 0)) -> None:
        """Clear buffer to color."""
        if self.mode == ColorMode.RGBA:
            self._image = Image.new('RGBA', (self.width, self.height), color[:4])
        else:
            self._image = Image.new('L', (self.width, self.height), color[0])
        self.dirty_rect = (0, 0, self.width, self.height)
        self._data = None
        self._needs_sync = False
    
    def resize(self, new_width: int, new_height: int) -> None:
        """Resize buffer (nearest neighbor for pixel art)."""
        if self._image is not None:
            self._image = self._image.resize((new_width, new_height), Image.Resampling.NEAREST)
        self.width = new_width
        self.height = new_height
        self.dirty_rect = (0, 0, new_width, new_height)
        self._data = None
        self._needs_sync = False
    
    def to_pil(self) -> Image.Image:
        """Convert to PIL Image."""
        return self._ensure_image().copy()
    
    def from_pil(self, pil_image: Image.Image) -> None:
        """Load from PIL Image."""
        if pil_image.mode == 'RGBA':
            self._image = pil_image.convert('RGBA')
            self.mode = ColorMode.RGBA
        elif pil_image.mode in ('RGB', 'L'):
            self._image = pil_image.convert('RGBA')
            self.mode = ColorMode.RGBA
        elif pil_image.mode == 'P':
            # Indexed
            self._image = pil_image
            self.mode = ColorMode.INDEXED
        
        self.width, self.height = pil_image.size
        self._data = None
        self._needs_sync = False
    
    def copy(self) -> 'ImageBuffer':
        """Create a deep copy."""
        new_buffer = ImageBuffer(self.width, self.height, self.mode)
        new_buffer._image = self._image.copy() if self._image is not None else None
        if self._data is not None and HAS_NUMPY:
            new_buffer._data = self._data.copy()
        return new_buffer
    
    def get_bounds(self) -> Tuple[int, int, int, int]:
        """Get bounding box of non-transparent pixels."""
        if self.mode != ColorMode.RGBA:
            return (0, 0, self.width, self.height)
        if self._image is None:
            return (0, 0, 0, 0)
        
        # Use PIL to get bounding box
        if self._image.mode == 'RGBA':
            alpha = self._image.split()[3]
            bbox = alpha.getbbox()
            if bbox:
                return bbox
        
        return (0, 0, 0, 0)
    
    def is_empty(self) -> bool:
        """Check if buffer contains only transparent/zero pixels."""
        if self._image is None:
            return True
        if self.mode == ColorMode.RGBA and self._image.mode == 'RGBA':
            # Fast path: Use PIL's getbbox on alpha channel
            alpha = self._image.split()[3]
            return alpha.getbbox() is None
        
        # For other modes, check if any pixel is non-zero
        # Use PIL's getextrema for efficiency
        extrema = self._image.getextrema()
        if isinstance(extrema, tuple):
            # Multi-band image
            return all(min_val == max_val == 0 for min_val, max_val in extrema)
        else:
            # Single-band image
            min_val, max_val = extrema
            return min_val == max_val == 0
    
    def get_pixel_count(self) -> int:
        """Get total pixel count."""
        return self.width * self.height
    
    def get_memory_size(self) -> int:
        """Get memory size in bytes (estimate)."""
        # PIL doesn't expose exact memory, estimate based on mode
        bytes_per_pixel = 4 if self.mode == ColorMode.RGBA else 1
        if self._image is None:
            return 0
        return self.width * self.height * bytes_per_pixel
