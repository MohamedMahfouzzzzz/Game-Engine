# /**************************************************************************/
# /*  path_2d.py                                                            */
# /**************************************************************************/

"""Godot Path2D port - 2D path/curve."""

from typing import List, Optional
from engine.core.nodes2d import Node2D
from engine.godot_scene2d.types import Point2


class Curve2D:
    """2D curve for paths."""
    
    def __init__(self):
        self._points: List[Point2] = []
        self._closed: bool = False
        self._bake_interval: float = 5.0
        self._baked_length: float = 0.0
        self._baked_points: List[Point2] = []
    
    def get_point_count(self) -> int:
        return len(self._points)
    
    def add_point(self, position: Point2, in_control: Point2 = None, out_control: Point2 = None, index: int = -1) -> None:
        self._points.append(position)
    
    def remove_point(self, index: int) -> None:
        if 0 <= index < len(self._points):
            del self._points[index]
    
    def clear_points(self) -> None:
        self._points.clear()
    
    def get_point_position(self, index: int) -> Point2:
        if 0 <= index < len(self._points):
            return self._points[index]
        return Point2()
    
    def set_point_position(self, index: int, position: Point2) -> None:
        if 0 <= index < len(self._points):
            self._points[index] = position
    
    def sample(self, offset: float) -> Point2:
        """Sample point at offset along curve."""
        if not self._points:
            return Point2()
        if len(self._points) == 1:
            return self._points[0]
        return self._points[0]
    
    def get_closest_point(self, to_point: Point2) -> Point2:
        if not self._points:
            return Point2()
        return self._points[0]
    
    def get_baked_length(self) -> float:
        return self._baked_length
    
    def set_bake_interval(self, interval: float) -> None:
        self._bake_interval = max(0.001, interval)
    
    def get_bake_interval(self) -> float:
        return self._bake_interval
    
    def set_closed(self, closed: bool) -> None:
        self._closed = closed
    
    def is_closed(self) -> bool:
        return self._closed


class Path2D(Node2D):
    """2D path defined by a curve."""
    
    def __init__(self, name: str = "Path2D"):
        super().__init__(name)
        self._curve: Optional[Curve2D] = None
    
    def set_curve(self, curve: Optional[Curve2D]) -> None:
        self._curve = curve
    
    def get_curve(self) -> Optional[Curve2D]:
        return self._curve
    
    def __repr__(self) -> str:
        return f"Path2D('{self.name}', curve={self._curve is not None})"


class PathFollow2D(Node2D):
    """Follows a Path2D."""
    
    def __init__(self, name: str = "PathFollow2D"):
        super().__init__(name)
        self._progress: float = 0.0
        self._h_offset: float = 0.0
        self._v_offset: float = 0.0
        self._progress_ratio: float = 0.0
        self._rotates: bool = True
        self._cubic_interp: bool = true
        self._loop: bool = False
        self._tilt: float = 0.0
    
    def set_progress(self, progress: float) -> None:
        self._progress = progress
    
    def get_progress(self) -> float:
        return self._progress
    
    def set_h_offset(self, h_offset: float) -> None:
        self._h_offset = h_offset
    
    def get_h_offset(self) -> float:
        return self._h_offset
    
    def set_v_offset(self, v_offset: float) -> None:
        self._v_offset = v_offset
    
    def get_v_offset(self) -> float:
        return self._v_offset
    
    def set_progress_ratio(self, ratio: float) -> None:
        self._progress_ratio = max(0.0, min(1.0, ratio))
    
    def get_progress_ratio(self) -> float:
        return self._progress_ratio
    
    def set_rotates(self, rotates: bool) -> None:
        self._rotates = rotates
    
    def is_rotating(self) -> bool:
        return self._rotates
    
    def set_cubic_interpolation(self, enable: bool) -> None:
        self._cubic_interp = enable
    
    def get_cubic_interpolation(self) -> bool:
        return self._cubic_interp
    
    def set_loop(self, loop: bool) -> None:
        self._loop = loop
    
    def has_loop(self) -> bool:
        return self._loop
    
    def set_tilt(self, tilt: float) -> None:
        self._tilt = tilt
    
    def get_tilt(self) -> float:
        return self._tilt
    
    def __repr__(self) -> str:
        return f"PathFollow2D('{self.name}', progress={self._progress})"
