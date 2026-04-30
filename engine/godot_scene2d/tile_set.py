# /**************************************************************************/
# /*  tile_set.py                                                           */
# /**************************************************************************/

"""Godot TileSet port - Tile definitions resource."""

from typing import Dict, List, Optional
from engine.godot_scene2d.types import Vector2i


class TileSet:
    """Collection of tile definitions."""
    
    def __init__(self):
        self._tiles: Dict[int, 'TileData'] = {}
        self._tile_size: Vector2i = Vector2i(16, 16)
        self._terrain_sets: Dict[int, 'TerrainSet'] = {}
        self._sources: Dict[int, any] = {}
    
    def set_tile_size(self, size: Vector2i) -> None:
        self._tile_size = size
    
    def get_tile_size(self) -> Vector2i:
        return self._tile_size
    
    def add_tile(self, tile_id: int, tile_data: 'TileData') -> None:
        self._tiles[tile_id] = tile_data
    
    def remove_tile(self, tile_id: int) -> None:
        if tile_id in self._tiles:
            del self._tiles[tile_id]
    
    def has_tile(self, tile_id: int) -> bool:
        return tile_id in self._tiles
    
    def get_tile(self, tile_id: int) -> Optional['TileData']:
        return self._tiles.get(tile_id)
    
    def get_tiles_ids(self) -> List[int]:
        return list(self._tiles.keys())
    
    def get_tiles_count(self) -> int:
        return len(self._tiles)
    
    def clear(self) -> None:
        self._tiles.clear()
    
    def __repr__(self) -> str:
        return f"TileSet(tiles={len(self._tiles)}, size={self._tile_size.x}x{self._tile_size.y})"
