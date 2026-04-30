# /**************************************************************************/
# /*  region.py                                                             */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Navigation region for 2D pathfinding."""

from typing import List, Optional
from engine.core.nodes2d import Node2D, Vector2


class NavigationPolygon:
    """Polygon defining navigable area."""
    
    def __init__(self):
        self._vertices: List[Vector2] = []
        self._outlines: List[List[Vector2]] = []
    
    def get_vertices(self) -> List[Vector2]:
        return self._vertices
    
    def set_vertices(self, vertices: List[Vector2]) -> None:
        self._vertices = vertices
    
    def add_outline(self, outline: List[Vector2]) -> None:
        self._outlines.append(outline)
    
    def get_outline_count(self) -> int:
        return len(self._outlines)


class NavigationRegion2D(Node2D):
    """Defines navigable area for pathfinding.
    
    Used by NavigationAgent2D to find paths around obstacles.
    """
    
    def __init__(self, name: str = "NavigationRegion2D"):
        super().__init__(name)
        self._navigation_polygon: Optional[NavigationPolygon] = None
        self._enter_cost: float = 0.0
        self._travel_cost: float = 1.0
        self._navigation_layers: int = 1
        self._use_edge_connections: bool = True
        self._edge_connection_margin: float = 12.0
        self._baking_rect: tuple = (0, 0, 0, 0)
        self._baking_rect_offset: Vector2 = Vector2()
    
    def set_navigation_polygon(self, polygon: Optional[NavigationPolygon]) -> None:
        self._navigation_polygon = polygon
    
    def get_navigation_polygon(self) -> Optional[NavigationPolygon]:
        return self._navigation_polygon
    
    def set_enter_cost(self, cost: float) -> None:
        """Cost to enter this region (0 = default)."""
        self._enter_cost = max(0.0, cost)
    
    def get_enter_cost(self) -> float:
        return self._enter_cost
    
    def set_travel_cost(self, cost: float) -> None:
        """Cost multiplier for traveling through this region."""
        self._travel_cost = max(0.0, cost)
    
    def get_travel_cost(self) -> float:
        return self._travel_cost
    
    def set_navigation_layers(self, layers: int) -> None:
        """Set which navigation layers this region belongs to."""
        self._navigation_layers = layers
    
    def get_navigation_layers(self) -> int:
        return self._navigation_layers
    
    def get_rid(self) -> int:
        """Get physics server RID."""
        return id(self)
    
    def __repr__(self) -> str:
        return f"NavigationRegion2D('{self.name}', layers={self._navigation_layers})"
