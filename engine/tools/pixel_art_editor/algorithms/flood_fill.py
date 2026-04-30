# /**************************************************************************/
# /*  flood_fill.py                                                         */
# /**************************************************************************/

"""Flood fill (bucket fill) algorithm.

Implements scanline flood fill for efficient filling
of connected regions.
"""

from typing import Callable, Tuple, Set, List, Optional
from collections import deque


def flood_fill(x: int, y: int,
               get_pixel: Callable[[int, int], Tuple[int, ...]],
               set_pixel: Callable[[int, int, Tuple[int, ...]], None],
               match_func: Callable[[Tuple[int, ...], Tuple[int, ...]], bool],
               bounds: Tuple[int, int, int, int]) -> int:
    """Flood fill starting at position.
    
    Uses scanline algorithm for efficiency.
    
    Args:
        x, y: Start position
        get_pixel: Function to get pixel color at (x, y)
        set_pixel: Function to set pixel color at (x, y)
        match_func: Function to check if colors match
        bounds: (min_x, min_y, max_x, max_y) bounds
    
    Returns:
        Number of pixels filled
    """
    min_x, min_y, max_x, max_y = bounds
    
    # Check bounds
    if not (min_x <= x < max_x and min_y <= y < max_y):
        return 0
    
    # Get target color to match
    target_color = get_pixel(x, y)
    
    # Stack for scanlines to process
    stack = [(x, x, y, 1)]  # (x1, x2, y, dy)
    stack.append((x, x, y - 1, -1))
    
    filled = 0
    visited = set()
    
    while stack:
        x1, x2, y, dy = stack.pop()
        
        # Find left extent
        sx = x1
        while sx >= min_x and match_func(get_pixel(sx, y), target_color):
            if (sx, y) not in visited:
                set_pixel(sx, y, target_color)  # Will be replaced with new color by caller
                filled += 1
                visited.add((sx, y))
            sx -= 1
        sx += 1
        
        # Find right extent
        ex = x1 + 1
        while ex < max_x and match_func(get_pixel(ex, y), target_color):
            if (ex, y) not in visited:
                set_pixel(ex, y, target_color)
                filled += 1
                visited.add((ex, y))
            ex += 1
        
        # Check row above/below for new segments
        if sx < x1:
            stack.append((sx, x1 - 1, y + dy, dy))
        
        while ex <= x2:
            # Find segment start
            sx = ex
            while ex <= x2 and match_func(get_pixel(ex, y), target_color):
                if (ex, y) not in visited:
                    set_pixel(ex, y, target_color)
                    filled += 1
                    visited.add((ex, y))
                ex += 1
            
            if ex > sx:
                stack.append((sx, ex - 1, y + dy, dy))
            
            # Skip non-matching pixels
            while ex <= x2 and not match_func(get_pixel(ex, y), target_color):
                ex += 1
    
    return filled


def flood_fill_simple(x: int, y: int,
                      get_pixel: Callable[[int, int], Tuple[int, ...]],
                      set_pixel: Callable[[int, int, Tuple[int, ...]], None],
                      match_color: Tuple[int, ...],
                      fill_color: Tuple[int, ...],
                      bounds: Tuple[int, int, int, int]) -> int:
    """Simple flood fill with exact color matching.
    
    Args:
        x, y: Start position
        get_pixel: Function to get pixel color
        set_pixel: Function to set pixel color
        match_color: Color to match and replace
        fill_color: New color to fill with
        bounds: (min_x, min_y, max_x, max_y)
    
    Returns:
        Number of pixels filled
    """
    def match_func(c1, c2):
        return c1 == c2
    
    def wrapped_set_pixel(px, py, _):
        set_pixel(px, py, fill_color)
    
    return flood_fill(x, y, get_pixel, wrapped_set_pixel, match_func, bounds)


def magic_wand_select(x: int, y: int,
                      get_pixel: Callable[[int, int], Tuple[int, ...]],
                      bounds: Tuple[int, int, int, int],
                      tolerance: int = 0) -> Set[Tuple[int, int]]:
    """Magic wand selection (flood fill without filling).
    
    Returns set of connected pixels matching the color at (x, y).
    
    Args:
        x, y: Start position
        get_pixel: Function to get pixel color
        bounds: (min_x, min_y, max_x, max_y)
        tolerance: Color tolerance for matching
    
    Returns:
        Set of (x, y) tuples representing selection
    """
    min_x, min_y, max_x, max_y = bounds
    
    if not (min_x <= x < max_x and min_y <= y < max_y):
        return set()
    
    target_color = get_pixel(x, y)
    selection = set()
    queue = deque([(x, y)])
    
    def color_match(c1, c2):
        if tolerance == 0:
            return c1 == c2
        # Calculate color distance
        if len(c1) >= 3 and len(c2) >= 3:
            dr = c1[0] - c2[0]
            dg = c1[1] - c2[1]
            db = c1[2] - c2[2]
            dist = (dr * dr + dg * dg + db * db) ** 0.5
            return dist <= tolerance
        return c1 == c2
    
    while queue:
        cx, cy = queue.popleft()
        
        if (cx, cy) in selection:
            continue
        
        if not (min_x <= cx < max_x and min_y <= cy < max_y):
            continue
        
        if not color_match(get_pixel(cx, cy), target_color):
            continue
        
        selection.add((cx, cy))
        
        # Add neighbors
        queue.append((cx + 1, cy))
        queue.append((cx - 1, cy))
        queue.append((cx, cy + 1))
        queue.append((cx, cy - 1))
    
    return selection


def fill_contiguous(x: int, y: int,
                    pixels: Set[Tuple[int, int]],
                    bounds: Tuple[int, int, int, int]) -> Set[Tuple[int, int]]:
    """Find all contiguous pixels from a set starting at (x, y).
    
    Args:
        x, y: Start position (must be in pixels set)
        pixels: Set of available pixel positions
        bounds: (min_x, min_y, max_x, max_y)
    
    Returns:
        Set of contiguous pixel positions
    """
    if (x, y) not in pixels:
        return set()
    
    result = set()
    queue = deque([(x, y)])
    
    while queue:
        cx, cy = queue.popleft()
        
        if (cx, cy) in result:
            continue
        
        if (cx, cy) not in pixels:
            continue
        
        result.add((cx, cy))
        
        # Add 4-connected neighbors
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = cx + dx, cy + dy
            queue.append((nx, ny))
    
    return result
