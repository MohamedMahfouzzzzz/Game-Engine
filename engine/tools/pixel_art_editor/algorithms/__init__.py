# /**************************************************************************/
# /*  algorithms/__init__.py                                                */
# /**************************************************************************/

"""Pixel art algorithms and utilities.

Includes algorithms for:
- Flood fill
- Line drawing (Bresenham)
- Circle/ellipse drawing
- Dithering patterns
- Color quantization
- Outline/stroke generation
"""

from .flood_fill import flood_fill, flood_fill_simple, magic_wand_select
from .line_drawing import line, line_points, rectangle, ellipse, polygon
from .dithering import dither_patterns, apply_dither, DitherPattern
from .color_ops import quantize_colors, create_outline, desaturate

__all__ = [
    "flood_fill",
    "flood_fill_simple",
    "magic_wand_select",
    "line",
    "line_points",
    "rectangle", 
    "ellipse",
    "polygon",
    "dither_patterns",
    "apply_dither",
    "DitherPattern",
    "quantize_colors",
    "create_outline",
    "desaturate",
]
