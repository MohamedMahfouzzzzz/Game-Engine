# /**************************************************************************/
# /*  navigation_region_2d.py                                               */
# /**************************************************************************/

"""Godot NavigationRegion2D port - Navigation mesh region."""

from typing import List, Optional
from engine.core.nodes2d import Node2D
from engine.godot_scene2d.types import Point2, Rect2


class NavigationPolygon:
    """Navigation mesh data."""
    
    def __init__(self):
        self._vertices: List[Point2] = []
        self._polygons: List[List[int]] = []
        self._outlines: List[List[Point2]] = []
    
    def add_polygon(self, polygon: List[int]) -> None:
        self._polygons.append(polygon)
    
    def get_polygon(self, index: int) -> List[int]:
        if 0 <= index < len(self._polygons):
            return self._polygons[index]
        return []
    
    def get_polygon_count(self) -> int:
        return len(self._polygons)
    
    def add_vertex(self, vertex: Point2) -> int:
        self._vertices.append(vertex)
        return len(self._vertices) - 1
    
    def get_vertex(self, index: int) -> Point2:
        if 0 <= index < len(self._vertices):
            return self._vertices[index]
        return Point2()
    
    def get_vertex_count(self) -> int:
        return len(self._vertices)
    
    def add_outline(self, outline: List[Point2]) -> None:
        self._outlines.append(outline)
    
    def clear(self) -> None:
        self._vertices.clear()
        self._polygons.clear()
        self._outlines.clear()


class NavigationRegion2D(Node2D):
    """Navigation region with polygon data."""
    
    def __init__(self, name: str = "NavigationRegion2D"):
        super().__init__(name)
        self._navigation_polygon: Optional[NavigationPolygon] = None
        self._navigation_layers: int = 1
        self._navigation_map: any = None
        self._enabled: bool = True
        self._baking_rect: Rect2 = Rect2()
        self._use_edge_connections: bool = True
        self._edge_connection_margin: float = 1.0
        self._enter_cost: float = 0.0
        self._travel_cost: float = 1.0
    
    def set_navigation_polygon(self, polygon: Optional[NavigationPolygon]) -> None:
        self._navigation_polygon = polygon
    
    def get_navigation_polygon(self) -> Optional[NavigationPolygon]:
        return self._navigation_polygon
    
    def set_navigation_layers(self, layers: int) -> None:
        self._navigation_layers = layers
    
    def get_navigation_layers(self) -> int:
        return self._navigation_layers
    
    def set_navigation_layer_value(self, layer_number: int, value: bool) -> None:
        if value:
            self._navigation_layers |= (1 << (layer_number - 1))
        else:
            self._navigation_layers &= ~(1 << (layer_number - 1))
    
    def get_navigation_layer_value(self, layer_number: int) -> bool:
        return (self._navigation_layers & (1 << (layer_number - 1))) != 0
    
    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled
    
    def is_enabled(self) -> bool:
        return self._enabled
    
    def get_rid(self) -> any:
        return None
    
    def set_travel_cost(self, cost: float) -> None:
        self._travel_cost = max(0.0, cost)
    
    def get_travel_cost(self) -> float:
        return self._travel_cost
    
    def set_enter_cost(self, cost: float) -> None:
        self._enter_cost = max(0.0, cost)
    
    def get_enter_cost(self) -> float:
        return self._enter_cost
    
    def bake_navigation_polygon(self, on_thread: bool = False) -> None:
        """Bake navigation mesh from outlines."""
        pass
    
    def __repr__(self) -> str:
        return f"NavigationRegion2D('{self.name}', layers={self._navigation_layers}, enabled={self._enabled})"
