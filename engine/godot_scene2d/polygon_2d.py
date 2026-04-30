# /**************************************************************************/
# /*  polygon_2d.py                                                         */
# /**************************************************************************/

"""Godot Polygon2D port - 2D polygon node."""

from typing import List, Optional
from engine.core.nodes2d import Node2D
from engine.godot_scene2d.types import Point2, Color


class Polygon2D(Node2D):
    """2D polygon with fill and outline."""
    
    def __init__(self, name: str = "Polygon2D"):
        super().__init__(name)
        self._polygon: List[Point2] = []
        self._uv: List[Point2] = []
        self._colors: List[Color] = []
        self._polygons: List[List[int]] = []
        self._internal_vertex_count: int = 0
        self._invert: bool = False
        self._invert_border: float = 100.0
        self._offset: Point2 = Point2()
        self._color: Color = Color(1, 1, 1)
        self._texture: Optional[any] = None
        self._texture_offset: Point2 = Point2()
        self._texture_scale: Point2 = Point2(1, 1)
        self._texture_rotation: float = 0.0
        self._skeleton: Optional[any] = None
    
    def set_polygon(self, polygon: List[Point2]) -> None:
        self._polygon = list(polygon)
    
    def get_polygon(self) -> List[Point2]:
        return self._polygon.copy()
    
    def set_color(self, color: Color) -> None:
        self._color = color
    
    def get_color(self) -> Color:
        return self._color
    
    def set_texture(self, texture: Optional[any]) -> None:
        self._texture = texture
    
    def get_texture(self) -> Optional[any]:
        return self._texture
    
    def set_texture_offset(self, offset: Point2) -> None:
        self._texture_offset = offset
    
    def get_texture_offset(self) -> Point2:
        return self._texture_offset
    
    def set_texture_scale(self, scale: Point2) -> None:
        self._texture_scale = scale
    
    def get_texture_scale(self) -> Point2:
        return self._texture_scale
    
    def set_texture_rotation(self, rotation: float) -> None:
        self._texture_rotation = rotation
    
    def get_texture_rotation(self) -> float:
        return self._texture_rotation
    
    def set_invert(self, invert: bool) -> None:
        self._invert = invert
    
    def get_invert(self) -> bool:
        return self._invert
    
    def set_invert_border(self, border: float) -> None:
        self._invert_border = border
    
    def get_invert_border(self) -> float:
        return self._invert_border
    
    def set_offset(self, offset: Point2) -> None:
        self._offset = offset
    
    def get_offset(self) -> Point2:
        return self._offset
    
    def get_area(self) -> float:
        """Calculate polygon area using shoelace formula."""
        if len(self._polygon) < 3:
            return 0.0
        
        area = 0.0
        n = len(self._polygon)
        for i in range(n):
            j = (i + 1) % n
            area += self._polygon[i].x * self._polygon[j].y
            area -= self._polygon[j].x * self._polygon[i].y
        
        return abs(area) / 2.0
    
    def get_center(self) -> Point2:
        if not self._polygon:
            return Point2()
        
        cx = sum(p.x for p in self._polygon) / len(self._polygon)
        cy = sum(p.y for p in self._polygon) / len(self._polygon)
        return Point2(cx, cy)
    
    def is_point_inside(self, point: Point2) -> bool:
        """Ray casting point-in-polygon test."""
        if len(self._polygon) < 3:
            return False
        
        inside = False
        n = len(self._polygon)
        
        for i in range(n):
            j = (i + 1) % n
            xi, yi = self._polygon[i].x, self._polygon[i].y
            xj, yj = self._polygon[j].x, self._polygon[j].y
            
            if ((yi > point.y) != (yj > point.y)) and \
               (point.x < (xj - xi) * (point.y - yi) / (yj - yi) + xi):
                inside = not inside
        
        return inside
    
    def __repr__(self) -> str:
        return f"Polygon2D('{self.name}', vertices={len(self._polygon)}, area={self.get_area():.1f})"
