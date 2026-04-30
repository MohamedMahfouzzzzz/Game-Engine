# /**************************************************************************/
# /*  tile_set.py                                                           */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Tile set resource for tile-based maps."""

from enum import IntEnum
from typing import Dict, List, Optional, Tuple
from engine.core.nodes2d import Vector2, Color
from engine.scene2d.sprite import Texture2D


class TileSetSource:
    """Source of tile data (e.g., atlas or scene)."""
    
    def __init__(self):
        self._id: int = 0
    
    def get_id(self) -> int:
        return self._id
    
    def set_id(self, id: int) -> None:
        self._id = id


class TileSetAtlasSource(TileSetSource):
    """Tile source from texture atlas."""
    
    def __init__(self, texture: Texture2D = None):
        super().__init__()
        self._texture: Optional[Texture2D] = texture
        self._margins: Vector2 = Vector2()
        self._separation: Vector2 = Vector2()
        self._texture_region_size: Vector2 = Vector2(16, 16)
        self._use_texture_padding: bool = True
        self._tiles: Dict[Tuple[int, int], 'TileData'] = {}
    
    def get_texture(self) -> Optional[Texture2D]:
        return self._texture
    
    def set_texture(self, texture: Texture2D) -> None:
        self._texture = texture
    
    def get_margins(self) -> Vector2:
        return self._margins
    
    def set_margins(self, margins: Vector2) -> None:
        self._margins = margins
    
    def get_separation(self) -> Vector2:
        return self._separation
    
    def set_separation(self, separation: Vector2) -> None:
        self._separation = separation
    
    def get_texture_region_size(self) -> Vector2:
        return self._texture_region_size
    
    def set_texture_region_size(self, size: Vector2) -> None:
        self._texture_region_size = size
    
    def has_tile(self, atlas_coords: Tuple[int, int]) -> bool:
        return atlas_coords in self._tiles
    
    def create_tile(self, atlas_coords: Tuple[int, int], alternative_tile: int = 0) -> 'TileData':
        tile = TileData()
        self._tiles[atlas_coords] = tile
        return tile
    
    def get_tile_data(self, atlas_coords: Tuple[int, int]) -> Optional['TileData']:
        return self._tiles.get(atlas_coords)


class TileSetScenesCollectionSource(TileSetSource):
    """Tile source from scene files."""
    
    def __init__(self):
        super().__init__()
        self._scenes: Dict[int, str] = {}
    
    def create_scene_tile(self, id: int, scene_file_path: str) -> None:
        self._scenes[id] = scene_file_path
    
    def has_scene_tile(self, id: int) -> bool:
        return id in self._scenes
    
    def get_scene_tile_path(self, id: int) -> Optional[str]:
        return self._scenes.get(id)


class TileData:
    """Data for a single tile."""
    
    def __init__(self):
        self._flip_h: bool = False
        self._flip_v: bool = False
        self._transpose: bool = False
        self._probability: float = 1.0
        self._terrain_set: int = -1
        self._terrain: int = -1
        self._terrains_peering_bit: Dict[int, int] = {}
        self._custom_data: Dict[str, any] = {}
        self._modulate: Color = Color(1, 1, 1, 1)
        self._material = None
        self._navigation_layers: int = 1
        self._z_index: int = 0
    
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
    
    def set_probability(self, prob: float) -> None:
        self._probability = max(0.0, min(1.0, prob))
    
    def get_probability(self) -> float:
        return self._probability
    
    def set_modulate(self, color: Color) -> None:
        self._modulate = color
    
    def get_modulate(self) -> Color:
        return self._modulate
    
    def set_z_index(self, z: int) -> None:
        self._z_index = z
    
    def get_z_index(self) -> int:
        return self._z_index
    
    def set_custom_data(self, layer_name: str, value: any) -> None:
        self._custom_data[layer_name] = value
    
    def get_custom_data(self, layer_name: str) -> any:
        return self._custom_data.get(layer_name)


class TileSet:
    """Resource containing all tile definitions for a tilemap.
    
    Supports multiple sources (atlases, scenes) and terrain systems.
    """
    
    def __init__(self):
        self._tile_size: Vector2 = Vector2(16, 16)
        self._tile_shape: int = 0  # Square
        self._tile_layout: int = 0  # Diamond Down
        self._tile_offset_axis: int = 0  # Horizontal
        self._tile_offset: float = 0.0
        self._sources: Dict[int, TileSetSource] = {}
        self._custom_data_layers: List[dict] = []
        self._terrain_sets: List[dict] = []
        self._physics_layers: List[dict] = []
        self._navigation_layers: List[dict] = []
        self._occlusion_layers: List[dict] = []
        self._next_source_id: int = 1
    
    def get_tile_size(self) -> Vector2:
        return self._tile_size
    
    def set_tile_size(self, size: Vector2) -> None:
        self._tile_size = Vector2(max(1, size.x), max(1, size.y))
    
    def get_tile_shape(self) -> int:
        return self._tile_shape
    
    def set_tile_shape(self, shape: int) -> None:
        self._tile_shape = shape
    
    def add_source(self, source: TileSetSource, atlas_source_id_override: int = -1) -> int:
        """Add a tile source. Returns source ID."""
        if atlas_source_id_override >= 0:
            source_id = atlas_source_id_override
        else:
            source_id = self._next_source_id
            self._next_source_id += 1
        
        source.set_id(source_id)
        self._sources[source_id] = source
        return source_id
    
    def remove_source(self, source_id: int) -> None:
        if source_id in self._sources:
            del self._sources[source_id]
    
    def get_source(self, source_id: int) -> Optional[TileSetSource]:
        return self._sources.get(source_id)
    
    def get_source_count(self) -> int:
        return len(self._sources)
    
    def get_next_source_id(self) -> int:
        return self._next_source_id
    
    def has_source(self, source_id: int) -> bool:
        return source_id in self._sources
    
    def get_pattern(self, atlas_coords: Tuple[int, int]) -> Optional[TileData]:
        """Get tile data for pattern."""
        for source in self._sources.values():
            if isinstance(source, TileSetAtlasSource):
                if source.has_tile(atlas_coords):
                    return source.get_tile_data(atlas_coords)
        return None
    
    def __repr__(self) -> str:
        return f"TileSet(sources={len(self._sources)}, tile_size={self._tile_size})"
