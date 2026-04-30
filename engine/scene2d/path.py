# /**************************************************************************/
# /*  path.py                                                               */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""2D path nodes for curve-based movement."""

import math
from typing import List, Tuple, Optional
from engine.core.nodes2d import Node2D, Vector2


class Curve2D:
    """2D curve defined by control points."""
    
    def __init__(self):
        self._points: List[Tuple[Vector2, Vector2, Vector2]] = []  # (in, pos, out)
        self._bake_interval: float = 5.0
        self._baked_length: float = 0.0
        self._baked_points: List[Vector2] = []
    
    def add_point(self, position: Vector2, in_handle: Vector2 = None,
                  out_handle: Vector2 = None, index: int = -1) -> None:
        """Add point to curve."""
        if in_handle is None:
            in_handle = Vector2()
        if out_handle is None:
            out_handle = Vector2()
        
        point = (in_handle, position, out_handle)
        if index < 0:
            self._points.append(point)
        else:
            self._points.insert(index, point)
        
        self._bake()
    
    def remove_point(self, index: int) -> None:
        if 0 <= index < len(self._points):
            del self._points[index]
            self._bake()
    
    def clear_points(self) -> None:
        self._points.clear()
        self._baked_points.clear()
        self._baked_length = 0.0
    
    def get_point_count(self) -> int:
        return len(self._points)
    
    def get_point_position(self, index: int) -> Vector2:
        if 0 <= index < len(self._points):
            return self._points[index][1]
        return Vector2()
    
    def get_baked_length(self) -> float:
        return self._baked_length
    
    def get_baked_points(self) -> List[Vector2]:
        return self._baked_points
    
    def sample(self, offset: float) -> Vector2:
        """Sample position at offset distance along curve."""
        if not self._baked_points:
            return Vector2()
        
        if offset <= 0:
            return self._baked_points[0]
        if offset >= self._baked_length:
            return self._baked_points[-1]
        
        # Find closest baked point
        idx = int(offset / self._bake_interval)
        idx = max(0, min(idx, len(self._baked_points) - 1))
        return self._baked_points[idx]
    
    def sample_baked(self, offset: float, cubic: bool = False) -> Vector2:
        """Sample baked curve at offset."""
        return self.sample(offset)
    
    def interpolate(self, t: float) -> Vector2:
        """Interpolate between 0 and 1 along curve."""
        return self.sample(t * self._baked_length)
    
    def _bake(self) -> None:
        """Bake curve into points for faster sampling."""
        self._baked_points.clear()
        if len(self._points) < 2:
            return
        
        for p in self._points:
            self._baked_points.append(p[1])
        
        # Calculate approximate length
        self._baked_length = 0.0
        for i in range(1, len(self._baked_points)):
            d = self._baked_points[i] - self._baked_points[i-1]
            self._baked_length += d.length()


class Path2D(Node2D):
    """Node containing a 2D curve.
    
    Used as reference for PathFollow2D or for drawing paths.
    """
    
    def __init__(self, name: str = "Path2D"):
        super().__init__(name)
        self._curve: Optional[Curve2D] = None
    
    def set_curve(self, curve: Optional[Curve2D]) -> None:
        self._curve = curve
    
    def get_curve(self) -> Optional[Curve2D]:
        return self._curve
    
    def __repr__(self) -> str:
        points = self._curve.get_point_count() if self._curve else 0
        return f"Path2D('{self.name}', points={points})"


class PathFollow2D(Node2D):
    """Follows a Path2D curve.
    
    Automatically updates position/rotation based on progress along path.
    """
    
    ROTATION_NONE = 0
    ROTATION_Y = 1
    ROTATION_XY = 2
    
    def __init__(self, name: str = "PathFollow2D"):
        super().__init__(name)
        self._path: Optional[Path2D] = None
        self._progress: float = 0.0
        self._progress_ratio: float = 0.0
        self._rotates: bool = True
        self._cubic_interp: bool = True
        self._loop: bool = false
        self._lookahead: float = 4.0
        self._tilt: float = 0.0
    
    def set_path(self, path: Optional[Path2D]) -> None:
        self._path = path
    
    def get_path(self) -> Optional[Path2D]:
        return self._path
    
    def set_progress(self, progress: float) -> None:
        """Set position along path (distance)."""
        if self._path and self._path.get_curve():
            max_len = self._path.get_curve().get_baked_length()
            if self._loop:
                self._progress = progress % max_len
            else:
                self._progress = max(0.0, min(max_len, progress))
        else:
            self._progress = max(0.0, progress)
        
        self._update_transform()
    
    def get_progress(self) -> float:
        return self._progress
    
    def set_progress_ratio(self, ratio: float) -> None:
        """Set position as ratio (0-1) of total length."""
        if self._path and self._path.get_curve():
            length = self._path.get_curve().get_baked_length()
            self.set_progress(ratio * length)
        self._progress_ratio = max(0.0, min(1.0, ratio))
    
    def get_progress_ratio(self) -> float:
        if self._path and self._path.get_curve():
            length = self._path.get_curve().get_baked_length()
            if length > 0:
                return self._progress / length
        return 0.0
    
    def set_rotates(self, rotates: bool) -> None:
        self._rotates = rotates
    
    def is_rotating(self) -> bool:
        return self._rotates
    
    def set_loop(self, loop: bool) -> None:
        self._loop = loop
    
    def has_loop(self) -> bool:
        return self._loop
    
    def _update_transform(self) -> None:
        """Update position based on progress."""
        if not self._path or not self._path.get_curve():
            return
        
        curve = self._path.get_curve()
        pos = curve.sample(self._progress)
        self.position = pos
        
        # Would calculate rotation based on tangent
        if self._rotates:
            pass  # Rotation calculation would go here
    
    def __repr__(self) -> str:
        return f"PathFollow2D('{self.name}', progress={self._progress})"
