# /**************************************************************************/
# /*  mesh_instance.py                                                      */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""2D mesh instance node."""

from typing import Optional
from engine.core.nodes2d import Node2D, Color


class Mesh:
    """Base mesh resource."""
    pass


class QuadMesh(Mesh):
    """Simple quad mesh."""
    
    def __init__(self):
        self._size = None
        self._subdivide = None


class MeshInstance2D(Node2D):
    """Displays a 2D mesh.
    
    Used for custom geometry or mesh-based sprites.
    """
    
    def __init__(self, name: str = "MeshInstance2D"):
        super().__init__(name)
        self._mesh: Optional[Mesh] = None
        self._texture = None
        self._normal_map = None
        self._specular_map = None
        self._modulate: Color = Color(1, 1, 1, 1)
        self._self_modulate: Color = Color(1, 1, 1, 1)
    
    def set_mesh(self, mesh: Optional[Mesh]) -> None:
        """Set the mesh to display."""
        self._mesh = mesh
    
    def get_mesh(self) -> Optional[Mesh]:
        return self._mesh
    
    def set_texture(self, texture) -> None:
        """Set texture for mesh."""
        self._texture = texture
    
    def get_texture(self):
        return self._texture
    
    def set_normal_map(self, normal_map) -> None:
        """Set normal map for lighting."""
        self._normal_map = normal_map
    
    def get_normal_map(self):
        return self._normal_map
    
    def set_modulate(self, color: Color) -> None:
        """Set color modulation."""
        self._modulate = color
    
    def get_modulate(self) -> Color:
        return self._modulate
    
    def __repr__(self) -> str:
        return f"MeshInstance2D('{self.name}', mesh={self._mesh.__class__.__name__ if self._mesh else None})"
