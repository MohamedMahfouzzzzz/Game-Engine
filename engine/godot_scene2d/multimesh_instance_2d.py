# /**************************************************************************/
# /*  multimesh_instance_2d.py                                            */
# /**************************************************************************/

"""Godot MultiMeshInstance2D port - Instanced 2D mesh rendering."""

from typing import Optional
from engine.core.nodes2d import Node2D
from engine.godot_scene2d.mesh_instance_2d import Mesh2D
from engine.godot_scene2d.types import Color


class MultiMesh:
    """Multi-mesh for instanced rendering."""
    
    def __init__(self):
        self._transform_format: int = 0
        self._color_format: int = 0
        self._custom_data_format: int = 0
        self._instance_count: int = 0
        self._visible_instance_count: int = -1
        self._mesh: Optional[Mesh2D] = None
    
    def set_mesh(self, mesh: Optional[Mesh2D]) -> None:
        self._mesh = mesh
    
    def get_mesh(self) -> Optional[Mesh2D]:
        return self._mesh
    
    def set_instance_count(self, count: int) -> None:
        self._instance_count = max(0, count)
    
    def get_instance_count(self) -> int:
        return self._instance_count
    
    def set_visible_instance_count(self, count: int) -> None:
        self._visible_instance_count = max(-1, count)
    
    def get_visible_instance_count(self) -> int:
        return self._visible_instance_count
    
    def set_instance_transform(self, index: int, transform: any) -> None:
        pass
    
    def get_instance_transform(self, index: int) -> any:
        return None
    
    def set_instance_color(self, index: int, color: Color) -> None:
        pass
    
    def get_instance_color(self, index: int) -> Color:
        return Color(1, 1, 1)


class MultiMeshInstance2D(Node2D):
    """Renders multiple mesh instances efficiently."""
    
    def __init__(self, name: str = "MultiMeshInstance2D"):
        super().__init__(name)
        self._multimesh: Optional[MultiMesh] = None
        self._texture: Optional[any] = None
        self._normal_map: Optional[any] = None
    
    def set_multimesh(self, multimesh: Optional[MultiMesh]) -> None:
        self._multimesh = multimesh
    
    def get_multimesh(self) -> Optional[MultiMesh]:
        return self._multimesh
    
    def set_texture(self, texture: Optional[any]) -> None:
        self._texture = texture
    
    def get_texture(self) -> Optional[any]:
        return self._texture
    
    def set_normal_map(self, normal_map: Optional[any]) -> None:
        self._normal_map = normal_map
    
    def get_normal_map(self) -> Optional[any]:
        return self._normal_map
    
    def __repr__(self) -> str:
        return f"MultiMeshInstance2D('{self.name}', instances={self._multimesh.get_instance_count() if self._multimesh else 0})"
