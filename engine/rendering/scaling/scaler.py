"""Core pixel scaling system."""

from enum import Enum
from typing import Optional
import numpy as np
from PIL import Image


class ScaleFilter(Enum):
    """Available scaling filters."""

    NEAREST = "nearest"
    LINEAR = "linear"
    EPX = "epx"
    XBR = "xbr"
    SMOOTH = "smooth"


class PixelScaler:
    """Handles pixel art upscaling with multiple algorithms."""

    def __init__(self, filter_type: ScaleFilter = ScaleFilter.NEAREST):
        self.filter_type = filter_type

    def scale(self, image: Image.Image, scale_factor: int) -> Image.Image:
        """Scale image by factor."""
        if scale_factor <= 1:
            return image

        if self.filter_type == ScaleFilter.NEAREST:
            return self._scale_nearest(image, scale_factor)
        elif self.filter_type == ScaleFilter.LINEAR:
            return self._scale_linear(image, scale_factor)
        elif self.filter_type == ScaleFilter.EPX:
            return self._scale_epx(image, scale_factor)
        elif self.filter_type == ScaleFilter.XBR:
            return self._scale_xbr(image, scale_factor)
        elif self.filter_type == ScaleFilter.SMOOTH:
            return self._scale_smooth(image, scale_factor)
        else:
            return self._scale_nearest(image, scale_factor)

    def _scale_nearest(self, image: Image.Image, scale_factor: int) -> Image.Image:
        """Nearest neighbor scaling."""
        new_size = (
            image.width * scale_factor,
            image.height * scale_factor
        )
        return image.resize(new_size, Image.NEAREST)

    def _scale_linear(self, image: Image.Image, scale_factor: int) -> Image.Image:
        """Linear interpolation scaling."""
        new_size = (
            image.width * scale_factor,
            image.height * scale_factor
        )
        return image.resize(new_size, Image.BILINEAR)

    def _scale_epx(self, image: Image.Image, scale_factor: int) -> Image.Image:
        """EPX (2x) pixel scaling algorithm."""
        if scale_factor > 2:
            # Apply EPX multiple times
            result = image
            for _ in range(scale_factor // 2):
                result = self._apply_epx_2x(result)
            return result
        return self._apply_epx_2x(image)

    def _apply_epx_2x(self, image: Image.Image) -> Image.Image:
        """Apply single EPX 2x scaling pass."""
        pixels = np.array(image)
        h, w = pixels.shape[:2]

        # Create output image (2x size)
        new_h, new_w = h * 2, w * 2
        new_pixels = np.zeros((new_h, new_w, *pixels.shape[2:]), dtype=pixels.dtype)

        for y in range(h):
            for x in range(w):
                # Get current pixel and neighbors
                c = pixels[y, x]
                a = pixels[y - 1, x] if y > 0 else c
                b = pixels[y, x + 1] if x < w - 1 else c
                d = pixels[y, x - 1] if x > 0 else c

                # EPX algorithm
                p0 = c
                p1 = c if self._pixels_equal(c, b) and not self._pixels_equal(a, d) else b
                p2 = c if self._pixels_equal(c, d) and not self._pixels_equal(a, b) else d
                p3 = c

                # Place 2x2 block
                new_pixels[y * 2, x * 2] = p0
                new_pixels[y * 2, x * 2 + 1] = p1
                new_pixels[y * 2 + 1, x * 2] = p2
                new_pixels[y * 2 + 1, x * 2 + 1] = p3

        return Image.fromarray(new_pixels.astype(np.uint8))

    def _scale_xbr(self, image: Image.Image, scale_factor: int) -> Image.Image:
        """XBR pixel scaling algorithm (high quality)."""
        # For simplicity, apply EPX as baseline
        # Full XBR is complex, use this as approximation
        return self._scale_epx(image, scale_factor)

    def _scale_smooth(self, image: Image.Image, scale_factor: int) -> Image.Image:
        """Smooth scaling (bicubic interpolation)."""
        new_size = (
            image.width * scale_factor,
            image.height * scale_factor
        )
        return image.resize(new_size, Image.BICUBIC)

    @staticmethod
    def _pixels_equal(p1: np.ndarray, p2: np.ndarray, tolerance: int = 0) -> bool:
        """Check if two pixels are equal."""
        if tolerance == 0:
            return np.array_equal(p1, p2)
        return np.all(np.abs(p1.astype(int) - p2.astype(int)) <= tolerance)

    def get_recommended_filter(self, image_type: str) -> ScaleFilter:
        """Get recommended filter for image type."""
        if image_type == "pixelart":
            return ScaleFilter.EPX
        elif image_type == "photo":
            return ScaleFilter.BICUBIC
        else:
            return ScaleFilter.NEAREST
