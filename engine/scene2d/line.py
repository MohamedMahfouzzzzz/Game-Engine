# /**************************************************************************/
# /*  line.py                                                               */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""2D line drawing node."""

from enum import IntEnum
from typing import List
from engine.core.nodes2d import Node2D, Vector2, Color


class LineCapMode(IntEnum):
    """How line ends are drawn."""
    CAP_NONE = 0
    CAP_BOX = 1
    CAP_ROUND = 2


class LineJointMode(IntEnum):
    """How line segments are joined."""
    SHARP = 0
    BEVEL = 1
    ROUND = 2


class Line2D(Node2D):
    """Draws a polyline with width, colors, and textures.
    
    Features:
    - Gradient colors per point
    - Width variation
    - Texture tiling
    - Various cap and join styles
    """
    
    def __init__(self, name: str = "Line2D"):
        super().__init__(name)
        self._points: List[Vector2] = []
        self._width: float = 10.0
        self._width_curve = None
        self._default_color: Color = Color(1, 1, 1, 1)
        self._gradient = None
        self._texture = None
        self._texture_mode: int = 0  # None
        self._joint_mode: LineJointMode = LineJointMode.SHARP
        self._begin_cap_mode: LineCapMode = LineCapMode.CAP_BOX
        self._end_cap_mode: LineCapMode = LineCapMode.CAP_BOX
        self._sharp_limit: float = 2.0
        self._round_precision: int = 8
        self._antialiased: bool = False
    
    def set_points(self, points: List[Vector2]) -> None:
        """Set all line points."""
        self._points = list(points)
    
    def get_points(self) -> List[Vector2]:
        return list(self._points)
    
    def add_point(self, point: Vector2, index: int = -1) -> None:
        """Add point to line."""
        if index < 0:
            self._points.append(point)
        else:
            self._points.insert(index, point)
    
    def remove_point(self, index: int) -> None:
        """Remove point at index."""
        if 0 <= index < len(self._points):
            del self._points[index]
    
    def clear_points(self) -> None:
        """Remove all points."""
        self._points.clear()
    
    def get_point_count(self) -> int:
        return len(self._points)
    
    def set_width(self, width: float) -> None:
        """Set line width."""
        self._width = max(0.0, width)
    
    def get_width(self) -> float:
        return self._width
    
    def set_default_color(self, color: Color) -> None:
        """Set line color."""
        self._default_color = color
    
    def get_default_color(self) -> Color:
        return self._default_color
    
    def set_gradient(self, gradient) -> None:
        """Set gradient for color variation."""
        self._gradient = gradient
    
    def get_gradient(self):
        return self._gradient
    
    def set_texture(self, texture) -> None:
        """Set line texture."""
        self._texture = texture
    
    def get_texture(self):
        return self._texture
    
    def set_joint_mode(self, mode: LineJointMode) -> None:
        """Set how segments are joined."""
        self._joint_mode = mode
    
    def get_joint_mode(self) -> LineJointMode:
        return self._joint_mode
    
    def set_begin_cap_mode(self, mode: LineCapMode) -> None:
        """Set start cap style."""
        self._begin_cap_mode = mode
    
    def get_begin_cap_mode(self) -> LineCapMode:
        return self._begin_cap_mode
    
    def set_end_cap_mode(self, mode: LineCapMode) -> None:
        """Set end cap style."""
        self._end_cap_mode = mode
    
    def get_end_cap_mode(self) -> LineCapMode:
        return self._end_cap_mode
    
    def set_sharp_limit(self, limit: float) -> None:
        """Limit for sharp corners."""
        self._sharp_limit = max(0.0, limit)
    
    def get_sharp_limit(self) -> float:
        return self._sharp_limit
    
    def set_round_precision(self, precision: int) -> None:
        """Precision for round caps/joins."""
        self._round_precision = max(1, precision)
    
    def get_round_precision(self) -> int:
        return self._round_precision
    
    def set_antialiased(self, antialiased: bool) -> None:
        """Enable antialiasing."""
        self._antialiased = antialiased
    
    def get_antialiased(self) -> bool:
        return self._antialiased
    
    def __repr__(self) -> str:
        return f"Line2D('{self.name}', points={len(self._points)}, width={self._width})"
