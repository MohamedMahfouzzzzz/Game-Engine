# /**************************************************************************/
# /*  tilemap/tile_set.py                                                   */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""TileSet resource for tile definitions and atlases."""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path

from .types import Vector2i, Rect2i, Shape2D, RectangleShape2D

@dataclass
class PhysicsLayer:
    """Physics properties for a tile."""
    shape: Optional[Shape2D] = None
    body_type: str = "static"  # static, kinematic, dynamic
    collision_layer: int = 1
    collision_mask: int = 1
    one_way: bool = False


@dataclass
class NavigationPolygon:
    """Navigation mesh data for tile."""
    vertices: List[Tuple[float, float]] = field(default_factory=list)
    indices: List[int] = field(default_factory=list)


@dataclass
class CustomDataLayer:
    """User-defined data layer."""
    name: str = ""
    type_name: str = "string"  # string, int, float, bool, color
    default_value: Any = None


@dataclass
class TileData:
    """Data for a single tile type."""
    # Identification
    atlas_coords: Vector2i = field(default_factory=lambda: Vector2i(0, 0))
    alternative_id: int = 0
    
    # Visual
    texture_region: Tuple[int, int, int, int] = (0, 0, 16, 16)
    animation_columns: int = 0
    animation_separation: Vector2i = field(default_factory=lambda: Vector2i(0, 0))
    animation_speed: float = 0.0
    animation_frames: int = 1
    animation_mode: str = "default"  # default, random_start, random
    
    # Physics layers
    physics_layers: List[Optional[PhysicsLayer]] = field(default_factory=list)
    
    # Navigation
    navigation_polygons: List[Optional[NavigationPolygon]] = field(default_factory=list)
    
    # Custom data
    custom_data: Dict[str, Any] = field(default_factory=dict)
    
    # Terrain
    terrain_set_id: int = -1
    terrain: int = -1
    terrain_peering_bit: Dict[str, int] = field(default_factory=dict)
    
    # Flags
    flip_h: bool = False
    flip_v: bool = False
    transpose: bool = False
    
    def is_animated(self) -> bool:
        return self.animation_frames > 1


class TileSet:
    """TileSet resource containing tile definitions.
    
    Supports:
        - Atlas textures with grid-based tiles
        - Physics layers with collision shapes
        - Navigation layers for pathfinding
        - Custom data layers
        - Animation frames
    """
    
    def __init__(self):
        self._tiles: Dict[Tuple[int, int, int], TileData] = {}
        self._physics_layers: List[str] = []
        self._navigation_layers: List[str] = []
        self._custom_data_layers: List[CustomDataLayer] = []
        
        # Atlas configuration
        self.tile_size = Vector2i(16, 16)
        self.tile_shape = "square"  # square, isometric
        self.tile_offset = Vector2i(0, 0)
        self.tile_separation = Vector2i(0, 0)
        
        # Texture
        self.texture_path: Optional[str] = None
        self.texture_size = (0, 0)
    
    def set_atlas_texture(
        self,
        texture_path: str,
        tile_size: Vector2i,
        separation: Vector2i = None,
        offset: Vector2i = None
    ) -> None:
        """Configure atlas texture."""
        self.texture_path = texture_path
        self.tile_size = tile_size
        self.tile_separation = separation or Vector2i(0, 0)
        self.tile_offset = offset or Vector2i(0, 0)
    
    def add_physics_layer(self, name: str) -> int:
        """Add physics layer, return layer index."""
        self._physics_layers.append(name)
        return len(self._physics_layers) - 1
    
    def add_navigation_layer(self, name: str) -> int:
        """Add navigation layer, return layer index."""
        self._navigation_layers.append(name)
        return len(self._navigation_layers) - 1
    
    def add_custom_data_layer(self, name: str, type_name: str = "string", default: Any = None) -> int:
        """Add custom data layer."""
        layer = CustomDataLayer(name=name, type_name=type_name, default_value=default)
        self._custom_data_layers.append(layer)
        return len(self._custom_data_layers) - 1
    
    def create_tile(self, atlas_x: int, atlas_y: int, alternative: int = 0) -> TileData:
        """Create or get tile at atlas coordinates."""
        key = (atlas_x, atlas_y, alternative)
        if key not in self._tiles:
            tile = TileData(
                atlas_coords=Vector2i(atlas_x, atlas_y),
                alternative_id=alternative
            )
            
            # Calculate texture region
            x = self.tile_offset.x + atlas_x * (self.tile_size.x + self.tile_separation.x)
            y = self.tile_offset.y + atlas_y * (self.tile_size.y + self.tile_separation.y)
            tile.texture_region = (x, y, self.tile_size.x, self.tile_size.y)
            
            self._tiles[key] = tile
        
        return self._tiles[key]
    
    def get_tile(self, atlas_x: int, atlas_y: int, alternative: int = 0) -> Optional[TileData]:
        """Get tile by atlas coordinates."""
        key = (atlas_x, atlas_y, alternative)
        return self._tiles.get(key)
    
    def get_alternative_tiles(self, atlas_x: int, atlas_y: int) -> List[TileData]:
        """Get all alternative tiles at coordinates."""
        result = []
        for alt_id in range(100):  # Reasonable limit
            key = (atlas_x, atlas_y, alt_id)
            if key in self._tiles:
                result.append(self._tiles[key])
        return result
    
    def get_tiles_count(self) -> int:
        return len(self._tiles)
    
    def get_source_id(self, atlas_x: int, atlas_y: int) -> int:
        """Convert atlas coords to unique source ID."""
        # Simple encoding: y * 1000 + x
        return atlas_y * 1000 + atlas_x
    
    def get_atlas_coords_from_id(self, source_id: int) -> Vector2i:
        """Convert source ID back to atlas coords."""
        x = source_id % 1000
        y = source_id // 1000
        return Vector2i(x, y)


__all__ = [
    "TileSet",
    "TileData",
    "PhysicsLayer",
    "NavigationPolygon",
    "CustomDataLayer",
]
