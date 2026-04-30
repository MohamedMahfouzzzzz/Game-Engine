# /**************************************************************************/
# /*  marker.py                                                             */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""2D marker/position reference node."""

from engine.core.nodes2d import Node2D


class Marker2D(Node2D):
    """Invisible position marker for spawning, targeting, etc.
    
    Useful for:
    - Spawn points for enemies/items
    - Target positions for projectiles
    - Waypoints for pathfinding
    - Camera look targets
    """
    
    def __init__(self, name: str = "Marker2D"):
        super().__init__(name)
        self._gizmo_extents: float = 10.0
    
    def set_gizmo_extents(self, extents: float) -> None:
        """Size of editor gizmo visual."""
        self._gizmo_extents = max(0.0, extents)
    
    def get_gizmo_extents(self) -> float:
        return self._gizmo_extents
    
    def __repr__(self) -> str:
        return f"Marker2D('{self.name}', pos=({self.position.x}, {self.position.y}))"
