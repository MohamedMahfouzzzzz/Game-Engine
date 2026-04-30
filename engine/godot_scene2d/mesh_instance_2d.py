# /**************************************************************************/
# /*  mesh_instance_2d.py                                                   */
# /**************************************************************************/

"""Godot MeshInstance2D port - 2D mesh display."""

from typing import Optional
from engine.core.nodes2d import Node2D
from engine.godot_scene2d.types import Point2, Rect2, Color


class Mesh2D:
    """2D mesh placeholder."""
    pass


class MeshInstance2D(Node2D):
    """2D mesh instance for rendering."""
    
    def __init__(self, name: str = "MeshInstance2D"):
        super().__init__(name)
        self._mesh: Optional[Mesh2D] = None
        self._texture: Optional[any] = None
        self._normal_map: Optional[any] = None
        self._self_modulate: Color = Color(1, 1, 1)
    
    def set_mesh(self, mesh: Optional[Mesh2D]) -> None:
        self._mesh = mesh
    
    def get_mesh(self) -> Optional[Mesh2D]:
        return self._mesh
    
    def set_texture(self, texture: Optional[any]) -> None:
        self._texture = texture
    
    def get_texture(self) -> Optional[any]:
        return self._texture
    
    def set_normal_map(self, normal_map: Optional[any]) -> None:
        self._normal_map = normal_map
    
    def get_normal_map(self) -> Optional[any]:
        return self._normal_map
    
    def set_self_modulate(self, modulate: Color) -> None:
        self._self_modulate = modulate
    
    def get_self_modulate(self) -> Color:
        return self._self_modulate
    
    def __repr__(self) -> str:
        return f"MeshInstance2D('{self.name}', mesh={self._mesh is not None})"
