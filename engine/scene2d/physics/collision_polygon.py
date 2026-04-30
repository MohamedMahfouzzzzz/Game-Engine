# /**************************************************************************/
# /*  collision_polygon.py                                                  */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Collision polygon node for physics bodies."""

from typing import List
from engine.core.nodes2d import Node2D, Vector2


class CollisionPolygon2D(Node2D):
    """Polygon collision shape defined by point array.
    
    Creates collision from polygon vertices.
    Can be built, segmented, or solid.
    """
    
    BUILD_SOLIDS = 0
    BUILD_SEGMENTS = 1
    
    def __init__(self, name: str = "CollisionPolygon2D"):
        super().__init__(name)
        self._polygon: List[Vector2] = []
        self._build_mode: int = self.BUILD_SOLIDS
        self._disabled: bool = False
        self._one_way_collision: bool = False
        self._one_way_collision_margin: float = 1.0
    
    def set_polygon(self, polygon: List[Vector2]) -> None:
        """Set polygon vertices."""
        self._polygon = list(polygon)
    
    def get_polygon(self) -> List[Vector2]:
        """Get polygon vertices."""
        return list(self._polygon)
    
    def set_build_mode(self, mode: int) -> None:
        """Set build mode: BUILD_SOLIDS or BUILD_SEGMENTS."""
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
    
    def add_point(self, point: Vector2, index: int = -1) -> None:
        """Add point to polygon."""
        if index < 0:
            self._polygon.append(point)
        else:
            self._polygon.insert(index, point)
    
    def remove_point(self, index: int) -> None:
        """Remove point at index."""
        if 0 <= index < len(self._polygon):
            del self._polygon[index]
    
    def clear_points(self) -> None:
        """Remove all points."""
        self._polygon.clear()
    
    def get_point_count(self) -> int:
        return len(self._polygon)
    
    def get_point(self, index: int) -> Vector2:
        """Get point at index."""
        if 0 <= index < len(self._polygon):
            return self._polygon[index]
        return Vector2()
    
    def __repr__(self) -> str:
        return f"CollisionPolygon2D('{self.name}', points={len(self._polygon)})"
