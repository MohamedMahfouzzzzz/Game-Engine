# /**************************************************************************/
# /*  __init__.py                                                           */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""2D navigation system for pathfinding."""

from engine.scene2d.navigation.region import NavigationRegion2D
from engine.scene2d.navigation.agent import NavigationAgent2D
from engine.scene2d.navigation.obstacle import NavigationObstacle2D

__all__ = [
    "NavigationRegion2D",
    "NavigationAgent2D",
    "NavigationObstacle2D",
]
