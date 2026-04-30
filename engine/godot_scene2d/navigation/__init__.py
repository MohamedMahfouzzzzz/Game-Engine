# /**************************************************************************/
# /*  navigation/__init__.py                                                */
# /**************************************************************************/

"""Godot Engine navigation nodes for 2D."""

from engine.godot_scene2d.navigation.navigation_region_2d import NavigationRegion2D, NavigationPolygon
from engine.godot_scene2d.navigation.navigation_agent_2d import NavigationAgent2D
from engine.godot_scene2d.navigation.navigation_obstacle_2d import NavigationObstacle2D

__all__ = [
    "NavigationRegion2D", "NavigationPolygon",
    "NavigationAgent2D", "NavigationObstacle2D"
]
