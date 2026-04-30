# /**************************************************************************/
# /*  multimesh_instance.py                                                 */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""2D multimesh instance for efficient repeated geometry."""

from typing import Optional, List
from engine.core.nodes2d import Node2D, Vector2, Color


class MultiMesh:
    """Resource containing mesh data for multiple instances."""
    
    TRANSFORM_2D = 0
    TRANSFORM_3D = 1
    
    COLOR_NONE = 0
    COLOR_8BIT = 1
    COLOR_FLOAT = 2
    
    CUSTOM_DATA_NONE = 0
    CUSTOM_DATA_8BIT = 1
    CUSTOM_DATA_FLOAT = 2
    
    def __init__(self):
        self._transform_format: int = self.TRANSFORM_2D
        self._color_format: int = self.COLOR_NONE
        self._custom_data_format: int = self.CUSTOM_DATA_NONE
        self._mesh = None
        self._instance_count: int = 0
        self._visible_instance_count: int = -1
        self._buffer = []


class MultiMeshInstance2D(Node2D):
    """Efficiently renders multiple instances of the same mesh.
    
    Much faster than creating many MeshInstance2D nodes for
    things like grass, particles, or crowds.
    """
    
    def __init__(self, name: str = "MultiMeshInstance2D"):
        super().__init__(name)
        self._multimesh: Optional[MultiMesh] = None
        self._texture = None
        self._normal_map = None
    
    def set_multimesh(self, multimesh: Optional[MultiMesh]) -> None:
        """Set the multimesh resource."""
        self._multimesh = multimesh
    
    def get_multimesh(self) -> Optional[MultiMesh]:
        return self._multimesh
    
    def set_texture(self, texture) -> None:
        """Set texture for instances."""
        self._texture = texture
    
    def get_texture(self):
        return self._texture
    
    def set_normal_map(self, normal_map) -> None:
        """Set normal map for lighting."""
        self._normal_map = normal_map
    
    def get_normal_map(self):
        return self._normal_map
    
    def __repr__(self) -> str:
        instances = self._multimesh._instance_count if self._multimesh else 0
        return f"MultiMeshInstance2D('{self.name}', instances={instances})"
