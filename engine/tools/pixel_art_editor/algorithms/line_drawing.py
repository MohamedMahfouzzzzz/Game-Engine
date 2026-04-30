# /**************************************************************************/
# /*  line_drawing.py                                                       */
# /**************************************************************************/

"""Line and shape drawing algorithms.

Bresenham's line algorithm for pixel-perfect lines.
Midpoint circle algorithm for circles and ellipses.
"""

from typing import List, Tuple, Callable, Optional


def line(x0: int, y0: int, x1: int, y1: int, 
         plot_func: Callable[[int, int], None]) -> None:
    """Draw line using Bresenham's algorithm.
    
    Args:
        x0, y0: Start point
        x1, y1: End point
        plot_func: Function to plot a pixel at (x, y)
    """
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    
    x, y = x0, y0
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    
    if dx > dy:
        err = dx // 2
        while x != x1:
            plot_func(x, y)
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
    else:
        err = dy // 2
        while y != y1:
            plot_func(x, y)
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy
    
    plot_func(x1, y1)  # Plot end point


def line_points(x0: int, y0: int, x1: int, y1: int) -> List[Tuple[int, int]]:
    """Get list of points for a line.
    
    Returns:
        List of (x, y) tuples
    """
    points = []
    line(x0, y0, x1, y1, lambda x, y: points.append((x, y)))
    return points


def rectangle(x: int, y: int, w: int, h: int, 
              plot_func: Callable[[int, int], None],
              filled: bool = False) -> None:
    """Draw rectangle.
    
    Args:
        x, y: Top-left corner
        w, h: Width and height
        plot_func: Function to plot pixel
        filled: Whether to fill the rectangle
    """
    if filled:
        for py in range(y, y + h):
            for px in range(x, x + w):
                plot_func(px, py)
    else:
        # Top and bottom edges
        for px in range(x, x + w):
            plot_func(px, y)
            plot_func(px, y + h - 1)
        
        # Left and right edges
        for py in range(y + 1, y + h - 1):
            plot_func(x, py)
            plot_func(x + w - 1, py)


def ellipse(cx: int, cy: int, rx: int, ry: int,
            plot_func: Callable[[int, int], None],
            filled: bool = False) -> None:
    """Draw ellipse using midpoint algorithm.
    
    Args:
        cx, cy: Center point
        rx, ry: X and Y radii
        plot_func: Function to plot pixel
        filled: Whether to fill the ellipse
    """
    if rx == ry:
        # Circle optimization
        circle(cx, cy, rx, plot_func, filled)
        return
    
    x, y = 0, ry
    
    # Decision parameters
    d1 = (ry * ry) - (rx * rx * ry) + (0.25 * rx * rx)
    dx = 2 * ry * ry * x
    dy = 2 * rx * rx * y
    
    # Region 1
    while dx < dy:
        if filled:
            _ellipse_fill_lines(cx, cy, x, y, plot_func)
        else:
            _ellipse_plot_points(cx, cy, x, y, plot_func)
        
        if d1 < 0:
            x += 1
            dx += 2 * ry * ry
            d1 += dx + (ry * ry)
        else:
            x += 1
            y -= 1
            dx += 2 * ry * ry
            dy -= 2 * rx * rx
            d1 += dx - dy + (ry * ry)
    
    # Region 2
    d2 = ((ry * ry) * ((x + 0.5) * (x + 0.5))) + \
         ((rx * rx) * ((y - 1) * (y - 1))) - \
         (rx * rx * ry * ry)
    
    while y >= 0:
        if filled:
            _ellipse_fill_lines(cx, cy, x, y, plot_func)
        else:
            _ellipse_plot_points(cx, cy, x, y, plot_func)
        
        if d2 > 0:
            y -= 1
            dy -= 2 * rx * rx
            d2 += (rx * rx) - dy
        else:
            y -= 1
            x += 1
            dx += 2 * ry * ry
            dy -= 2 * rx * rx
            d2 += dx - dy + (rx * rx)


def _ellipse_plot_points(cx: int, cy: int, x: int, y: int,
                         plot_func: Callable[[int, int], None]) -> None:
    """Plot 4 points for ellipse symmetry."""
    plot_func(cx + x, cy + y)
    plot_func(cx - x, cy + y)
    plot_func(cx + x, cy - y)
    plot_func(cx - x, cy - y)


def _ellipse_fill_lines(cx: int, cy: int, x: int, y: int,
                        plot_func: Callable[[int, int], None]) -> None:
    """Fill horizontal lines for ellipse."""
    for px in range(cx - x, cx + x + 1):
        plot_func(px, cy + y)
        plot_func(px, cy - y)


def circle(cx: int, cy: int, r: int,
           plot_func: Callable[[int, int], None],
           filled: bool = False) -> None:
    """Draw circle using midpoint algorithm.
    
    Args:
        cx, cy: Center point
        r: Radius
        plot_func: Function to plot pixel
        filled: Whether to fill the circle
    """
    x, y = 0, r
    d = 1 - r
    
    while y >= x:
        if filled:
            # Fill horizontal lines
            for px in range(cx - x, cx + x + 1):
                plot_func(px, cy + y)
                plot_func(px, cy - y)
            for px in range(cx - y, cx + y + 1):
                plot_func(px, cy + x)
                plot_func(px, cy - x)
        else:
            # Plot 8 points
            _circle_plot8(cx, cy, x, y, plot_func)
        
        x += 1
        if d < 0:
            d += 2 * x + 1
        else:
            y -= 1
            d += 2 * (x - y) + 1


def _circle_plot8(cx: int, cy: int, x: int, y: int,
                  plot_func: Callable[[int, int], None]) -> None:
    """Plot 8 points for circle symmetry."""
    plot_func(cx + x, cy + y)
    plot_func(cx - x, cy + y)
    plot_func(cx + x, cy - y)
    plot_func(cx - x, cy - y)
    plot_func(cx + y, cy + x)
    plot_func(cx - y, cy + x)
    plot_func(cx + y, cy - x)
    plot_func(cx - y, cy - x)


def polygon(points: List[Tuple[int, int]],
            plot_func: Callable[[int, int], None],
            filled: bool = False) -> None:
    """Draw polygon from list of points.
    
    Args:
        points: List of (x, y) vertices
        plot_func: Function to plot pixel
        filled: Whether to fill the polygon
    """
    if len(points) < 3:
        return
    
    if filled:
        # Scanline fill algorithm
        _fill_polygon(points, plot_func)
    else:
        # Draw edges
        for i in range(len(points)):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % len(points)]
            line(x0, y0, x1, y1, plot_func)


def _fill_polygon(points: List[Tuple[int, int]],
                  plot_func: Callable[[int, int], None]) -> None:
    """Fill polygon using scanline algorithm."""
    # Find bounds
    min_y = min(p[1] for p in points)
    max_y = max(p[1] for p in points)
    
    # Scan each row
    for y in range(min_y, max_y + 1):
        # Find intersections
        intersections = []
        
        for i in range(len(points)):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % len(points)]
            
            # Check if edge crosses this y
            if (y0 <= y < y1) or (y1 <= y < y0):
                if y0 != y1:
                    # Calculate intersection x
                    x = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
                    intersections.append(x)
        
        # Sort and fill between pairs
        intersections.sort()
        for i in range(0, len(intersections) - 1, 2):
            x_start = int(intersections[i])
            x_end = int(intersections[i + 1])
            for x in range(x_start, x_end + 1):
                plot_func(x, y)
