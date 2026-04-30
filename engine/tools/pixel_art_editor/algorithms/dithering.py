# /**************************************************************************/
# /*  dithering.py                                                          */
# /**************************************************************************/

"""Dithering patterns for pixel art.

Provides various dithering algorithms for creating
smooth transitions between colors.
"""

from typing import List, Callable, Tuple
from enum import Enum, auto


class DitherPattern(Enum):
    """Dither pattern types."""
    NONE = auto()
    CHECKERBOARD = auto()
    BAYER_2X2 = auto()
    BAYER_4X4 = auto()
    BAYER_8X8 = auto()
    HALFTONE = auto()
    SCATTER = auto()
    NOISE = auto()


# Bayer matrices for ordered dithering
BAYER_2X2_MATRIX = [
    [0, 2],
    [3, 1]
]

BAYER_4X4_MATRIX = [
    [0, 8, 2, 10],
    [12, 4, 14, 6],
    [3, 11, 1, 9],
    [15, 7, 13, 5]
]

BAYER_8X8_MATRIX = [
    [0, 32, 8, 40, 2, 34, 10, 42],
    [48, 16, 56, 24, 50, 18, 58, 26],
    [12, 44, 4, 36, 14, 46, 6, 38],
    [60, 28, 52, 20, 62, 30, 54, 22],
    [3, 35, 11, 43, 1, 33, 9, 41],
    [51, 19, 59, 27, 49, 17, 57, 25],
    [15, 47, 7, 39, 13, 45, 5, 37],
    [63, 31, 55, 23, 61, 29, 53, 21]
]


def get_threshold_matrix(pattern: DitherPattern) -> List[List[int]]:
    """Get threshold matrix for dither pattern."""
    if pattern == DitherPattern.BAYER_2X2:
        return BAYER_2X2_MATRIX
    elif pattern == DitherPattern.BAYER_4X4:
        return BAYER_4X4_MATRIX
    elif pattern == DitherPattern.BAYER_8X8:
        return BAYER_8X8_MATRIX
    elif pattern == DitherPattern.CHECKERBOARD:
        return [[0, 1], [1, 0]]
    return [[0]]


def dither_patterns() -> dict:
    """Get all dither patterns with descriptions."""
    return {
        DitherPattern.NONE: "No dithering",
        DitherPattern.CHECKERBOARD: "Checkerboard pattern",
        DitherPattern.BAYER_2X2: "Bayer 2x2 (coarse)",
        DitherPattern.BAYER_4X4: "Bayer 4x4 (medium)",
        DitherPattern.BAYER_8X8: "Bayer 8x8 (fine)",
        DitherPattern.HALFTONE: "Halftone dots",
        DitherPattern.SCATTER: "Scattered dots",
        DitherPattern.NOISE: "Random noise",
    }


def apply_dither(x: int, y: int, 
                 intensity: float,
                 pattern: DitherPattern) -> bool:
    """Apply dither pattern at position.
    
    Args:
        x, y: Pixel position
        intensity: Threshold intensity (0.0-1.0)
        pattern: Dither pattern to apply
    
    Returns:
        True if pixel should be drawn
    """
    if pattern == DitherPattern.NONE:
        return intensity >= 0.5
    
    if pattern == DitherPattern.NOISE:
        import random
        return random.random() < intensity
    
    if pattern == DitherPattern.HALFTONE:
        # Halftone based on distance from center of cell
        cell_x = x % 4
        cell_y = y % 4
        center_x, center_y = 1.5, 1.5
        dist = ((cell_x - center_x) ** 2 + (cell_y - center_y) ** 2) ** 0.5
        threshold = dist / 2.0
        return intensity > threshold
    
    if pattern == DitherPattern.SCATTER:
        # Scattered pattern
        cell_x = x % 4
        cell_y = y % 4
        scatter_map = [
            [0, 2, 1, 3],
            [2, 1, 3, 0],
            [1, 3, 0, 2],
            [3, 0, 2, 1]
        ]
        threshold = scatter_map[cell_y][cell_x] / 4.0
        return intensity > threshold
    
    # Ordered dithering with Bayer matrices
    matrix = get_threshold_matrix(pattern)
    size = len(matrix)
    
    threshold = matrix[y % size][x % size] / (size * size)
    return intensity > threshold


def dither_gradient(width: int, height: int,
                    pattern: DitherPattern,
                    direction: str = "horizontal") -> List[List[float]]:
    """Generate dithered gradient pattern.
    
    Args:
        width, height: Size of gradient
        pattern: Dither pattern to use
        direction: "horizontal" or "vertical"
    
    Returns:
        2D list of threshold values (0.0-1.0)
    """
    result = []
    
    for y in range(height):
        row = []
        for x in range(width):
            if direction == "horizontal":
                intensity = x / (width - 1) if width > 1 else 1.0
            else:
                intensity = y / (height - 1) if height > 1 else 1.0
            
            # Apply dither threshold
            row.append(1.0 if apply_dither(x, y, intensity, pattern) else 0.0)
        
        result.append(row)
    
    return result


def create_dither_brush(size: int, density: float,
                        pattern: DitherPattern = DitherPattern.SCATTER) -> List[List[int]]:
    """Create a dithered brush pattern.
    
    Args:
        size: Brush size
        density: Pixel density (0.0-1.0)
        pattern: Dither pattern
    
    Returns:
        2D list of 0/1 for brush shape
    """
    brush = []
    
    for y in range(size):
        row = []
        for x in range(size):
            # Map to circle for round brush
            cx, cy = size // 2, size // 2
            dx, dy = x - cx, y - cy
            distance = (dx * dx + dy * dy) ** 0.5 / (size // 2)
            
            if distance <= 1.0:
                # Inside brush circle
                intensity = density * (1.0 - distance * 0.5)
                row.append(1 if apply_dither(x, y, intensity, pattern) else 0)
            else:
                row.append(0)
        
        brush.append(row)
    
    return brush


def color_dither(color1: Tuple[int, ...], 
                 color2: Tuple[int, ...],
                 x: int, y: int,
                 ratio: float,
                 pattern: DitherPattern) -> Tuple[int, ...]:
    """Dither between two colors.
    
    Args:
        color1, color2: Colors to blend
        x, y: Position for dither pattern
        ratio: Blend ratio (0.0 = color1, 1.0 = color2)
        pattern: Dither pattern
    
    Returns:
        Result color
    """
    if apply_dither(x, y, ratio, pattern):
        return color2
    return color1
