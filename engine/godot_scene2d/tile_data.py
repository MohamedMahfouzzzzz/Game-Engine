# /**************************************************************************/
# /*  tile_data.py                                                          */
# /**************************************************************************/

"""Godot TileData port - Individual tile definition."""

from typing import Optional, List
from engine.godot_scene2d.types import Vector2i


class TileData:
    """Data for a single tile type."""
    
    def __init__(self, atlas_coords: Vector2i = None):
        self._atlas_coords = atlas_coords if atlas_coords else Vector2i()
        self._flip_h: bool = False
        self._flip_v: bool = False
        self._transpose: bool = False
        self._terrain_set: int = -1
        self._terrain: int = -1
        self._probability: float = 1.0
        self._custom_data: dict = {}
    
    def set_flip_h(self, flip: bool) -> None:
        self._flip_h = flip
    
    def get_flip_h(self) -> bool:
        return self._flip_h
    
    def set_flip_v(self, flip: bool) -> None:
        self._flip_v = flip
    
    def get_flip_v(self) -> bool:
        return self._flip_v
    
    def set_transpose(self, transpose: bool) -> None:
        self._transpose = transpose
    
    def get_transpose(self) -> bool:
        return self._transpose
    
    def set_terrain_set(self, terrain_set: int) -> None:
        self._terrain_set = terrain_set
    
    def get_terrain_set(self) -> int:
        return self._terrain_set
    
    def set_terrain(self, terrain: int) -> None:
        self._terrain = terrain
    
    def get_terrain(self) -> int:
        return self._terrain
    
    def set_probability(self, probability: float) -> None:
        self._probability = max(0.0, min(1.0, probability))
    
    def get_probability(self) -> float:
        return self._probability
    
    def set_custom_data(self, name: str, value: any) -> None:
        self._custom_data[name] = value
    
    def get_custom_data(self, name: str) -> any:
        return self._custom_data.get(name)
    
    def __repr__(self) -> str:
        return f"TileData(coords={self._atlas_coords.x},{self._atlas_coords.y}, terrain={self._terrain})"
