# /**************************************************************************/
# /*  line_2d.py                                                            */
# /**************************************************************************/

"""Godot Line2D port - 2D polyline node."""

from enum import IntEnum
from typing import List, Optional
from engine.core.nodes2d import Node2D
from engine.godot_scene2d.types import Point2, Color


class Line2DJointMode(IntEnum):
    LINE_JOINT_SHARP = 0
    LINE_JOINT_BEVEL = 1
    LINE_JOINT_ROUND = 2


class Line2DCapMode(IntEnum):
    LINE_CAP_NONE = 0
    LINE_CAP_BOX = 1
    LINE_CAP_ROUND = 2


class Line2D(Node2D):
    """2D polyline with width and styling."""
    
    def __init__(self, name: str = "Line2D"):
        super().__init__(name)
        self._points: List[Point2] = []
        self._width: float = 10.0
        self._width_curve: Optional[any] = None
        self._default_color: Color = Color(1, 1, 1)
        self._gradient: Optional[any] = None
        self._texture: Optional[any] = None
        self._texture_mode: int = 0
        self._joint_mode: Line2DJointMode = Line2DJointMode.LINE_JOINT_SHARP
        self._begin_cap_mode: Line2DCapMode = Line2DCapMode.LINE_CAP_NONE
        self._end_cap_mode: Line2DCapMode = Line2DCapMode.LINE_CAP_NONE
        self._sharp_limit: float = 10.0
        self._round_precision: int = 8
        self._antialiased: bool = False
    
    def set_points(self, points: List[Point2]) -> None:
        self._points = list(points)
    
    def get_points(self) -> List[Point2]:
        return self._points.copy()
    
    def add_point(self, point: Point2, at_position: int = -1) -> None:
        if at_position < 0 or at_position >= len(self._points):
            self._points.append(point)
        else:
            self._points.insert(at_position, point)
    
    def remove_point(self, index: int) -> None:
        if 0 <= index < len(self._points):
            del self._points[index]
    
    def clear_points(self) -> None:
        self._points.clear()
    
    def get_point_count(self) -> int:
        return len(self._points)
    
    def get_point_position(self, index: int) -> Point2:
        if 0 <= index < len(self._points):
            return self._points[index]
        return Point2()
    
    def set_point_position(self, index: int, position: Point2) -> None:
        if 0 <= index < len(self._points):
            self._points[index] = position
    
    def set_width(self, width: float) -> None:
        self._width = max(0.0, width)
    
    def get_width(self) -> float:
        return self._width
    
    def set_default_color(self, color: Color) -> None:
        self._default_color = color
    
    def get_default_color(self) -> Color:
        return self._default_color
    
    def set_joint_mode(self, mode: Line2DJointMode) -> None:
        self._joint_mode = mode
    
    def get_joint_mode(self) -> Line2DJointMode:
        return self._joint_mode
    
    def set_begin_cap_mode(self, mode: Line2DCapMode) -> None:
        self._begin_cap_mode = mode
    
    def get_begin_cap_mode(self) -> Line2DCapMode:
        return self._begin_cap_mode
    
    def set_end_cap_mode(self, mode: Line2DCapMode) -> None:
        self._end_cap_mode = mode
    
    def get_end_cap_mode(self) -> Line2DCapMode:
        return self._end_cap_mode
    
    def set_antialiased(self, antialiased: bool) -> None:
        self._antialiased = antialiased
    
    def is_antialiased(self) -> bool:
        return self._antialiased
    
    def get_total_length(self) -> float:
        length = 0.0
        for i in range(1, len(self._points)):
            dx = self._points[i].x - self._points[i-1].x
            dy = self._points[i].y - self._points[i-1].y
            length += (dx**2 + dy**2) ** 0.5
        return length
    
    def get_point_at_offset(self, offset: float) -> Point2:
        if not self._points:
            return Point2()
        if len(self._points) == 1:
            return self._points[0]
        
        current_offset = 0.0
        for i in range(1, len(self._points)):
            p1 = self._points[i-1]
            p2 = self._points[i]
            segment_length = ((p2.x - p1.x)**2 + (p2.y - p1.y)**2) ** 0.5
            
            if current_offset + segment_length >= offset:
                t = (offset - current_offset) / segment_length if segment_length > 0 else 0
                return Point2(p1.x + (p2.x - p1.x) * t, p1.y + (p2.y - p1.y) * t)
            
            current_offset += segment_length
        
        return self._points[-1]
    
    def __repr__(self) -> str:
        return f"Line2D('{self.name}', points={len(self._points)}, width={self._width})"
