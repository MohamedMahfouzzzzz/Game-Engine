# /**************************************************************************/
# /*  navigation_agent_2d.py                                                */
# /**************************************************************************/

"""Godot NavigationAgent2D port - Pathfinding agent."""

from typing import List, Optional, Callable
from engine.core.nodes2d import Node2D
from engine.godot_scene2d.types import Point2


class NavigationAgent2D(Node2D):
    """2D navigation/pathfinding agent."""
    
    def __init__(self, name: str = "NavigationAgent2D"):
        super().__init__(name)
        self._target_position: Point2 = Point2()
        self._navigation_layers: int = 1
        self._radius: float = 0.0
        self._neighbor_distance: float = 50.0
        self._max_neighbors: int = 10
        self._time_horizon_agents: float = 1.0
        self._time_horizon_obstacles: float = 0.0
        self._max_speed: float = 100.0
        self._path_desired_distance: float = 20.0
        self._target_desired_distance: float = 10.0
        self._path_metadata_flags: int = 0
        self._debug_enabled: bool = False
        self._debug_use_custom: bool = False
        self._avoidance_enabled: bool = True
        self._avoidance_layers: int = 1
        self._avoidance_mask: int = 1
        self._avoidance_priority: float = 1.0
        
        self._path: List[Point2] = []
        self._path_index: int = 0
        self._navigation_finished: bool = True
        self._velocity: Point2 = Point2()
        self._next_location: Point2 = Point2()
        
        self._path_changed_callbacks: List[Callable] = []
        self._target_reached_callbacks: List[Callable] = []
    
    def set_target_position(self, target_position: Point2) -> None:
        self._target_position = target_position
    
    def get_target_position(self) -> Point2:
        return self._target_position
    
    def set_navigation_layers(self, navigation_layers: int) -> None:
        self._navigation_layers = navigation_layers
    
    def get_navigation_layers(self) -> int:
        return self._navigation_layers
    
    def set_velocity(self, velocity: Point2) -> None:
        self._velocity = velocity
    
    def set_radius(self, radius: float) -> None:
        self._radius = max(0.0, radius)
    
    def get_radius(self) -> float:
        return self._radius
    
    def set_avoidance_enabled(self, enabled: bool) -> None:
        self._avoidance_enabled = enabled
    
    def get_avoidance_enabled(self) -> bool:
        return self._avoidance_enabled
    
    def set_max_speed(self, max_speed: float) -> None:
        self._max_speed = max(0.0, max_speed)
    
    def get_max_speed(self) -> float:
        return self._max_speed
    
    def get_next_path_position(self) -> Point2:
        return self._next_location
    
    def get_final_position(self) -> Point2:
        return self._path[-1] if self._path else self._target_position
    
    def distance_to_target(self) -> float:
        pos = self.get_position()
        dx = self._target_position.x - pos.x
        dy = self._target_position.y - pos.y
        return (dx * dx + dy * dy) ** 0.5
    
    def get_current_navigation_result(self) -> any:
        return None
    
    def is_target_reached(self) -> bool:
        return self.distance_to_target() <= self._target_desired_distance
    
    def is_target_reachable(self) -> bool:
        return len(self._path) > 0
    
    def is_navigation_finished(self) -> bool:
        return self._navigation_finished
    
    def get_current_navigation_path(self) -> List[Point2]:
        return self._path.copy()
    
    def get_current_navigation_path_index(self) -> int:
        return self._path_index
    
    def set_avoidance_layers(self, layers: int) -> None:
        self._avoidance_layers = layers
    
    def get_avoidance_layers(self) -> int:
        return self._avoidance_layers
    
    def set_avoidance_mask(self, mask: int) -> None:
        self._avoidance_mask = mask
    
    def get_avoidance_mask(self) -> int:
        return self._avoidance_mask
    
    def set_avoidance_priority(self, priority: float) -> None:
        self._avoidance_priority = max(0.0, priority)
    
    def get_avoidance_priority(self) -> float:
        return self._avoidance_priority
    
    def get_rid(self) -> any:
        return None
    
    def get_pathfinding_result(self) -> any:
        return None
    
    def set_debug_enabled(self, enabled: bool) -> None:
        self._debug_enabled = enabled
    
    def get_debug_enabled(self) -> bool:
        return self._debug_enabled
    
    def get_velocity(self) -> Point2:
        return self._velocity
    
    def set_path_desired_distance(self, distance: float) -> None:
        self._path_desired_distance = max(0.0, distance)
    
    def get_path_desired_distance(self) -> float:
        return self._path_desired_distance
    
    def set_target_desired_distance(self, distance: float) -> None:
        self._target_desired_distance = max(0.0, distance)
    
    def get_target_desired_distance(self) -> float:
        return self._target_desired_distance
    
    def set_path_metadata_flags(self, flags: int) -> None:
        self._path_metadata_flags = flags
    
    def get_path_metadata_flags(self) -> int:
        return self._path_metadata_flags
    
    def is_valid(self) -> bool:
        return True
    
    def __repr__(self) -> str:
        return f"NavigationAgent2D('{self.name}', target={self._target_position}, reached={self.is_target_reached()})"
