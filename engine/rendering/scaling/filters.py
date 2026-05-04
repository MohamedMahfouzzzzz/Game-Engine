"""Advanced pixel scaling filters."""

import numpy as np
from PIL import Image
from typing import Optional


class FilterBase:
    """Base class for scaling filters."""

    def apply(self, image: Image.Image, scale_factor: int) -> Image.Image:
        """Apply filter to image."""
        raise NotImplementedError


class NearestNeighbor(FilterBase):
    """Nearest neighbor scaling (fast, blocky)."""

    def apply(self, image: Image.Image, scale_factor: int) -> Image.Image:
        """Apply nearest neighbor scaling."""
        new_size = (image.width * scale_factor, image.height * scale_factor)
        return image.resize(new_size, Image.NEAREST)

    def __repr__(self) -> str:
        return "NearestNeighbor"


class Linear(FilterBase):
    """Linear interpolation scaling."""

    def apply(self, image: Image.Image, scale_factor: int) -> Image.Image:
        """Apply linear scaling."""
        new_size = (image.width * scale_factor, image.height * scale_factor)
        return image.resize(new_size, Image.BILINEAR)

    def __repr__(self) -> str:
        return "Linear"


class EPX(FilterBase):
    """EPX pixel scaling (good for pixel art)."""

    def apply(self, image: Image.Image, scale_factor: int) -> Image.Image:
        """Apply EPX scaling."""
        if scale_factor <= 1:
            return image

        result = image
        # Apply 2x EPX multiple times
        while scale_factor >= 2:
            result = self._apply_2x(result)
            scale_factor -= 1

        if scale_factor == 1:
            result = image.resize(
                (image.width * 2, image.height * 2),
                Image.NEAREST
            )

        return result

    @staticmethod
    def _apply_2x(image: Image.Image) -> Image.Image:
        """Apply single EPX 2x pass."""
        pixels = np.array(image, dtype=np.int32)

        if len(pixels.shape) == 2:
            # Grayscale
            h, w = pixels.shape
            new_pixels = np.zeros((h * 2, w * 2), dtype=np.int32)

            for y in range(h):
                for x in range(w):
                    c = pixels[y, x]
                    a = pixels[y - 1, x] if y > 0 else c
                    b = pixels[y, x + 1] if x < w - 1 else c
                    d = pixels[y, x - 1] if x > 0 else c

                    p0 = c
                    p1 = c if c == b and a != d else b
                    p2 = c if c == d and a != b else d
                    p3 = c

                    new_pixels[y * 2, x * 2] = p0
                    new_pixels[y * 2, x * 2 + 1] = p1
                    new_pixels[y * 2 + 1, x * 2] = p2
                    new_pixels[y * 2 + 1, x * 2 + 1] = p3
        else:
            # Color image
            h, w, c = pixels.shape
            new_pixels = np.zeros((h * 2, w * 2, c), dtype=np.int32)

            for y in range(h):
                for x in range(w):
                    curr = pixels[y, x]
                    up = pixels[y - 1, x] if y > 0 else curr
                    right = pixels[y, x + 1] if x < w - 1 else curr
                    left = pixels[y, x - 1] if x > 0 else curr

                    p0 = curr
                    p1 = curr if np.array_equal(curr, right) and not np.array_equal(up, left) else right
                    p2 = curr if np.array_equal(curr, left) and not np.array_equal(up, right) else left
                    p3 = curr

                    new_pixels[y * 2, x * 2] = p0
                    new_pixels[y * 2, x * 2 + 1] = p1
                    new_pixels[y * 2 + 1, x * 2] = p2
                    new_pixels[y * 2 + 1, x * 2 + 1] = p3

        return Image.fromarray(np.clip(new_pixels, 0, 255).astype(np.uint8))

    def __repr__(self) -> str:
        return "EPX"


class XBR(FilterBase):
    """XBR pixel scaling (advanced, high quality)."""

    def apply(self, image: Image.Image, scale_factor: int) -> Image.Image:
        """Apply XBR scaling."""
        # Simplified XBR (full implementation is very complex)
        # Use high-quality bicubic as approximation
        new_size = (image.width * scale_factor, image.height * scale_factor)
        return image.resize(new_size, Image.BICUBIC)

    def __repr__(self) -> str:
        return "XBR"


class Smooth(FilterBase):
    """Smooth scaling with bicubic interpolation."""

    def apply(self, image: Image.Image, scale_factor: int) -> Image.Image:
        """Apply smooth scaling."""
        new_size = (image.width * scale_factor, image.height * scale_factor)
        return image.resize(new_size, Image.BICUBIC)

    def __repr__(self) -> str:
        return "Smooth"


class Adaptive(FilterBase):
    """Adaptive scaling that detects content type."""

    def apply(self, image: Image.Image, scale_factor: int) -> Image.Image:
        """Apply adaptive scaling."""
        if self._is_pixel_art(image):
            filter_obj = EPX()
        else:
            filter_obj = Smooth()

        return filter_obj.apply(image, scale_factor)

    @staticmethod
    def _is_pixel_art(image: Image.Image, sample_size: int = 10) -> bool:
        """Detect if image is pixel art."""
        pixels = np.array(image)

        # Sample pixels
        sampled = pixels[::max(1, pixels.shape[0] // sample_size),
                        ::max(1, pixels.shape[1] // sample_size)]

        # Check color variety (pixel art has less colors)
        if len(pixels.shape) == 3:
            unique_colors = len(np.unique(sampled.reshape(-1, sampled.shape[-1]), axis=0))
        else:
            unique_colors = len(np.unique(sampled))

        # Pixel art typically has < 256 colors
        return unique_colors < 256

    def __repr__(self) -> str:
        return "Adaptive"
