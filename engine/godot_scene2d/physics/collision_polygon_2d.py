# /**************************************************************************/
# /*  collision_polygon_2d.py                                               */
# /**************************************************************************/

"""Godot CollisionPolygon2D port - Polygon collision shape."""

from typing import List, Optional
from engine.core.nodes2d import Node2D
from engine.godot_scene2d.types import Point2


class CollisionPolygon2D(Node2D):
    """Polygon-based collision shape."""
    
    def __init__(self, name: str = "CollisionPolygon2D"):
        super().__init__(name)
        self._polygon: List[Point2] = []
        self._build_mode: int = 0  # 0=segments, 1=solids
        self._disabled: bool = False
        self._one_way_collision: bool = False
        self._one_way_collision_margin: float = 1.0
    
    def set_polygon(self, polygon: List[Point2]) -> None:
        self._polygon = list(polygon)
    
    def get_polygon(self) -> List[Point2]:
        return self._polygon.copy()
    
    def set_build_mode(self, mode: int) -> None:
        self._build_mode = mode
    
    def get_build_mode(self) -> int:
        return self._build_mode
    
    def set_disabled(self, disabled: bool) -> None:
        self._disabled = disabled
    
    def is_disabled(self) -> bool:
        return self._disabled
    
    def set_one_way_collision(self, enabled: bool) -> None:
        self._one_way_collision = enabled
    
    def is_one_way_collision_enabled(self) -> bool:
        return self._one_way_collision
    
    def set_one_way_collision_margin(self, margin: float) -> None:
        self._one_way_collision_margin = max(0.0, margin)
    
    def get_one_way_collision_margin(self) -> float:
        return self._one_way_collision_margin
    
    def __repr__(self) -> str:
        return f"CollisionPolygon2D('{self.name}', vertices={len(self._polygon)}, mode={self._build_mode})"
