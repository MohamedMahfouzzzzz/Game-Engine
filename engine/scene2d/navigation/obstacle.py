# /**************************************************************************/
# /*  obstacle.py                                                           */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Navigation obstacle for 2D pathfinding."""

from typing import List
from engine.core.nodes2d import Node2D, Vector2


class NavigationObstacle2D(Node2D):
    """Obstacle that agents will avoid.
    
    Can be radius-based (circle) or polygon-based.
    """
    
    def __init__(self, name: str = "NavigationObstacle2D"):
        super().__init__(name)
        self._radius: float = 0.0
        self._vertices: List[Vector2] = []
        self._avoidance_enabled: bool = True
        self._affect_navigation_mesh: bool = False
        self._carve_navigation_mesh: bool = False
    
    def set_radius(self, radius: float) -> None:
        """Set radius for circular obstacle (0 = use vertices)."""
        self._radius = max(0.0, radius)
    
    def get_radius(self) -> float:
        return self._radius
    
    def set_vertices(self, vertices: List[Vector2]) -> None:
        """Set polygon vertices for obstacle."""
        self._vertices = list(vertices)
    
    def get_vertices(self) -> List[Vector2]:
        return list(self._vertices)
    
    def set_avoidance_enabled(self, enabled: bool) -> None:
        """Enable avoidance by agents."""
        self._avoidance_enabled = enabled
    
    def get_avoidance_enabled(self) -> bool:
        return self._avoidance_enabled
    
    def set_affect_navigation_mesh(self, affect: bool) -> None:
        """Affect navigation mesh baking."""
        self._affect_navigation_mesh = affect
    
    def get_affect_navigation_mesh(self) -> bool:
        return self._affect_navigation_mesh
    
    def set_carve_navigation_mesh(self, carve: bool) -> None:
        """Carve into navigation mesh."""
        self._carve_navigation_mesh = carve
    
    def get_carve_navigation_mesh(self) -> bool:
        return self._carve_navigation_mesh
    
    def get_rid(self) -> int:
        return id(self)
    
    def __repr__(self) -> str:
        return f"NavigationObstacle2D('{self.name}', radius={self._radius})"
