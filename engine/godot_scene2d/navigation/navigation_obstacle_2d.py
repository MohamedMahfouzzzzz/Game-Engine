# /**************************************************************************/
# /*  navigation_obstacle_2d.py                                             */
# /**************************************************************************/

"""Godot NavigationObstacle2D port - Navigation obstacle."""

from typing import Optional
from engine.core.nodes2d import Node2D
from engine.godot_scene2d.types import Point2


class NavigationObstacle2D(Node2D):
    """Dynamic obstacle for navigation avoidance."""
    
    def __init__(self, name: str = "NavigationObstacle2D"):
        super().__init__(name)
        self._radius: float = 0.0
        self._velocity: Point2 = Point2()
        self._avoidance_layers: int = 1
        self._affect_navigation_mesh: bool = True
        self._carve_navigation_mesh: bool = False
        self._navigation_layers: int = 1
        
        self._estimate_radius: bool = True
        self._height: float = 1.0
        self._enabled: bool = True
        self._vertices: list = []
    
    def set_radius(self, radius: float) -> None:
        self._radius = max(0.0, radius)
        self._estimate_radius = False
    
    def get_radius(self) -> float:
        return self._radius
    
    def set_velocity(self, velocity: Point2) -> None:
        self._velocity = velocity
    
    def get_velocity(self) -> Point2:
        return self._velocity
    
    def set_avoidance_layers(self, layers: int) -> None:
        self._avoidance_layers = layers
    
    def get_avoidance_layers(self) -> int:
        return self._avoidance_layers
    
    def set_navigation_layers(self, layers: int) -> None:
        self._navigation_layers = layers
    
    def get_navigation_layers(self) -> int:
        return self._navigation_layers
    
    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled
    
    def is_enabled(self) -> bool:
        return self._enabled
    
    def set_estimate_radius(self, enabled: bool) -> None:
        self._estimate_radius = enabled
    
    def is_radius_estimated(self) -> bool:
        return self._estimate_radius
    
    def get_rid(self) -> any:
        return None
    
    def __repr__(self) -> str:
        return f"NavigationObstacle2D('{self.name}', radius={self._radius}, enabled={self._enabled})"
