# /**************************************************************************/
# /*  color_ops.py                                                          */
# /**************************************************************************/

"""Color operations for pixel art.

Includes color quantization, outline generation, and
color manipulation utilities.
"""

from typing import List, Tuple, Set, Optional, Callable
from collections import defaultdict


def rgb_to_hsv(r: int, g: int, b: int) -> Tuple[float, float, float]:
    """Convert RGB to HSV color space.
    
    Returns:
        (hue: 0-360, saturation: 0-1, value: 0-1)
    """
    r_norm, g_norm, b_norm = r / 255.0, g / 255.0, b / 255.0
    
    max_val = max(r_norm, g_norm, b_norm)
    min_val = min(r_norm, g_norm, b_norm)
    diff = max_val - min_val
    
    # Value
    v = max_val
    
    # Saturation
    s = 0 if max_val == 0 else diff / max_val
    
    # Hue
    if diff == 0:
        h = 0
    elif max_val == r_norm:
        h = (60 * ((g_norm - b_norm) / diff) + 360) % 360
    elif max_val == g_norm:
        h = (60 * ((b_norm - r_norm) / diff) + 120) % 360
    else:  # max_val == b_norm
        h = (60 * ((r_norm - g_norm) / diff) + 240) % 360
    
    return (h, s, v)


def hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
    """Convert HSV to RGB color space."""
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    
    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    
    return (
        int((r + m) * 255),
        int((g + m) * 255),
        int((b + m) * 255)
    )


def color_distance(c1: Tuple[int, ...], c2: Tuple[int, ...]) -> float:
    """Calculate perceptual color distance.
    
    Uses simple Euclidean distance in RGB space.
    """
    if len(c1) < 3 or len(c2) < 3:
        return 0.0
    
    dr = c1[0] - c2[0]
    dg = c1[1] - c2[1]
    db = c1[2] - c2[2]
    
    return (dr * dr + dg * dg + db * db) ** 0.5


def find_nearest_color(color: Tuple[int, ...], 
                       palette: List[Tuple[int, ...]]) -> Tuple[int, ...]:
    """Find nearest color in palette."""
    if not palette:
        return color
    
    min_dist = float('inf')
    nearest = palette[0]
    
    for p in palette:
        dist = color_distance(color, p)
        if dist < min_dist:
            min_dist = dist
            nearest = p
    
    return nearest


def quantize_colors(colors: List[Tuple[int, ...]], 
                    max_colors: int) -> List[Tuple[int, ...]]:
    """Reduce color count using median cut algorithm (simplified).
    
    Args:
        colors: List of colors to quantize
        max_colors: Maximum number of colors in output
    
    Returns:
        Reduced palette
    """
    if len(colors) <= max_colors:
        return list(set(colors))
    
    # Count color frequencies
    color_counts = defaultdict(int)
    for c in colors:
        # Round to reduce similar colors
        rounded = (c[0] & 0xF0, c[1] & 0xF0, c[2] & 0xF0, c[3] if len(c) > 3 else 255)
        color_counts[rounded] += 1
    
    # Sort by frequency and take top colors
    sorted_colors = sorted(color_counts.items(), key=lambda x: -x[1])
    
    result = []
    for color, count in sorted_colors[:max_colors]:
        # Expand back to full range
        r = min(255, color[0] + 0x0F)
        g = min(255, color[1] + 0x0F)
        b = min(255, color[2] + 0x0F)
        a = color[3] if len(color) > 3 else 255
        result.append((r, g, b, a))
    
    return result


def create_outline(pixels: Set[Tuple[int, int]],
                 color: Tuple[int, ...],
                 width: int = 1,
                 diagonal: bool = False) -> Set[Tuple[int, int, Tuple[int, ...]]]:
    """Generate outline around pixel set.
    
    Args:
        pixels: Set of (x, y) positions
        color: Outline color
        width: Outline width in pixels
        diagonal: Include diagonal neighbors
    
    Returns:
        Set of (x, y, color) outline pixels
    """
    if not pixels:
        return set()
    
    outline = set()
    
    # Directions
    if diagonal:
        directions = [(-1, -1), (0, -1), (1, -1),
                     (-1, 0),          (1, 0),
                     (-1, 1),  (0, 1),  (1, 1)]
    else:
        directions = [(0, -1), (-1, 0), (1, 0), (0, 1)]
    
    # Find outline pixels
    for x, y in pixels:
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if (nx, ny) not in pixels:
                outline.add((nx, ny, color))
    
    return outline


def desaturate(color: Tuple[int, ...], 
               factor: float = 1.0) -> Tuple[int, ...]:
    """Desaturate a color.
    
    Args:
        color: RGB or RGBA color
        factor: Desaturation factor (0.0 = unchanged, 1.0 = grayscale)
    
    Returns:
        Desaturated color
    """
    if len(color) < 3:
        return color
    
    r, g, b = color[:3]
    gray = int(0.299 * r + 0.587 * g + 0.114 * b)
    
    new_r = int(r + (gray - r) * factor)
    new_g = int(g + (gray - g) * factor)
    new_b = int(b + (gray - b) * factor)
    
    if len(color) > 3:
        return (new_r, new_g, new_b, color[3])
    return (new_r, new_g, new_b)


def adjust_brightness(color: Tuple[int, ...],
                     factor: float) -> Tuple[int, ...]:
    """Adjust color brightness.
    
    Args:
        color: RGB or RGBA color
        factor: Brightness factor (1.0 = unchanged, <1 darker, >1 brighter)
    
    Returns:
        Adjusted color
    """
    if len(color) < 3:
        return color
    
    r, g, b = color[:3]
    
    if factor < 1.0:
        # Darken
        new_r = int(r * factor)
        new_g = int(g * factor)
        new_b = int(b * factor)
    else:
        # Lighten
        new_r = min(255, int(r + (255 - r) * (factor - 1)))
        new_g = min(255, int(g + (255 - g) * (factor - 1)))
        new_b = min(255, int(b + (255 - b) * (factor - 1)))
    
    if len(color) > 3:
        return (new_r, new_g, new_b, color[3])
    return (new_r, new_g, new_b)


def blend_colors(color1: Tuple[int, ...],
                color2: Tuple[int, ...],
                t: float) -> Tuple[int, ...]:
    """Blend two colors.
    
    Args:
        color1, color2: Colors to blend
        t: Blend factor (0.0 = color1, 1.0 = color2)
    
    Returns:
        Blended color
    """
    def lerp(a, b, t):
        return int(a + (b - a) * t)
    
    if len(color1) < 3 or len(color2) < 3:
        return color1
    
    r = lerp(color1[0], color2[0], t)
    g = lerp(color1[1], color2[1], t)
    b = lerp(color1[2], color2[2], t)
    
    a = 255
    if len(color1) > 3 and len(color2) > 3:
        a = lerp(color1[3], color2[3], t)
    
    return (r, g, b, a)
