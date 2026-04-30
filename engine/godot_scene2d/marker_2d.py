# /**************************************************************************/
# /*  marker_2d.py                                                          */
# /**************************************************************************/

"""Godot Marker2D port - Visual position marker."""

from engine.core.nodes2d import Node2D


class Marker2D(Node2D):
    """Editor marker for position reference.
    
    A visual marker used in the editor to mark positions.
    """
    
    def __init__(self, name: str = "Marker2D"):
        super().__init__(name)
        self._gizmo_extents: float = 20.0
    
    def set_gizmo_extents(self, extents: float) -> None:
        """Set the gizmo display size."""
        self._gizmo_extents = max(0.0, extents)
    
    def get_gizmo_extents(self) -> float:
        """Get the gizmo display size."""
        return self._gizmo_extents
    
    def __repr__(self) -> str:
        return f"Marker2D('{self.name}', pos={self.get_position()}, extents={self._gizmo_extents})"
