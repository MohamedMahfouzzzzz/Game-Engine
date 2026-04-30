# /**************************************************************************/
# /*  agent.py                                                              */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Navigation agent for 2D pathfinding."""

from typing import List, Optional, Callable
from engine.core.nodes2d import Node2D, Vector2


class NavigationAgent2D(Node2D):
    """Agent that can navigate through NavigationRegion2D.
    
    Calculates paths and follows them to reach targets.
    """
    
    def __init__(self, name: str = "NavigationAgent2D"):
        super().__init__(name)
        self._target_position: Vector2 = Vector2()
        self._target_desired_distance: float = 1.0
        self._radius: float = 10.0
        self._neighbor_distance: float = 500.0
        self._max_neighbors: int = 10
        self._time_horizon_agents: float = 1.0
        self._time_horizon_obstacles: float = 0.0
        self._max_speed: float = 100.0
        self._path_desired_distance: float = 20.0
        self._path_max_distance: float = 100.0
        self._navigation_layers: int = 1
        self._avoidance_enabled: bool = True
        self._avoidance_layers: int = 1
        self._avoidance_mask: int = 1
        self._path_metadata_flags: int = 0
        
        # Path data
        self._path: List[Vector2] = []
        self._next_path_index: int = 0
        self._next_path_position: Vector2 = Vector2()
        self._distance_to_target: float = 0.0
        self._velocity: Vector2 = Vector2()
        self._velocity_forced: Vector2 = Vector2()
        
        # Callbacks
        self._path_changed_callback: Optional[Callable] = None
        self._target_reached_callback: Optional[Callable] = None
        self._navigation_finished_callback: Optional[Callable] = None
        self._link_reached_callback: Optional[Callable] = None
        self._waypoint_reached_callback: Optional[Callable] = None
    
    def set_target_position(self, position: Vector2) -> None:
        """Set destination for navigation."""
        self._target_position = position
    
    def get_target_position(self) -> Vector2:
        return self._target_position
    
    def get_next_path_position(self) -> Vector2:
        """Get next position to move toward."""
        if self._next_path_index < len(self._path):
            return self._path[self._next_path_index]
        return self._target_position
    
    def set_velocity(self, velocity: Vector2) -> None:
        """Set agent's desired velocity."""
        self._velocity = velocity
    
    def get_velocity(self) -> Vector2:
        """Get calculated velocity (after avoidance)."""
        return self._velocity_forced if self._avoidance_enabled else self._velocity
    
    def set_max_speed(self, speed: float) -> None:
        self._max_speed = max(0.0, speed)
    
    def get_max_speed(self) -> float:
        return self._max_speed
    
    def set_radius(self, radius: float) -> None:
        self._radius = max(0.0, radius)
    
    def get_radius(self) -> float:
        return self._radius
    
    def get_path(self) -> List[Vector2]:
        """Get the full calculated path."""
        return list(self._path)
    
    def distance_to_target(self) -> float:
        """Get remaining distance to target."""
        return self._distance_to_target
    
    def is_target_reached(self) -> bool:
        """Check if target is within desired distance."""
        return self._distance_to_target <= self._target_desired_distance
    
    def is_navigation_finished(self) -> bool:
        """Check if navigation is complete."""
        return self._next_path_index >= len(self._path) and self.is_target_reached()
    
    def set_avoidance_enabled(self, enabled: bool) -> None:
        self._avoidance_enabled = enabled
    
    def get_avoidance_enabled(self) -> bool:
        return self._avoidance_enabled
    
    def set_navigation_layers(self, layers: int) -> None:
        self._navigation_layers = layers
    
    def get_navigation_layers(self) -> int:
        return self._navigation_layers
    
    def set_path_changed_callback(self, callback: Optional[Callable]) -> None:
        self._path_changed_callback = callback
    
    def set_target_reached_callback(self, callback: Optional[Callable]) -> None:
        self._target_reached_callback = callback
    
    def set_navigation_finished_callback(self, callback: Optional[Callable]) -> None:
        self._navigation_finished_callback = callback
    
    def get_rid(self) -> int:
        return id(self)
    
    def __repr__(self) -> str:
        return f"NavigationAgent2D('{self.name}', target={self._target_position})"
