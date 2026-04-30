# /**************************************************************************/
# /*  tilemap.py                                                            */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Godot-inspired TileMap System

TileMapLayer: Single layer of tiles
TileSet: Resource defining all available tiles
TileData: Properties for individual tile types
TerrainSet: Auto-tiling rules

Features:
- Atlas-based tilesets
- Physics collision per tile
- Auto-tiling with terrain peering bits
- Custom data layers
"""

from __future__ import annotations

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Any
from pathlib import Path

from engine.core.nodes2d import Node2D, Vector2, Color, Texture2D
from engine.core.types import NodeType

import logging



# =============================================================================
# Direction Enum for Neighbor Checks
# =============================================================================

logger = logging.getLogger(__name__)

class Direction(Enum):
    """8-directional neighbors for peering bits."""
    NORTH = auto()
    NORTH_EAST = auto()
    EAST = auto()
    SOUTH_EAST = auto()
    SOUTH = auto()
    SOUTH_WEST = auto()
    WEST = auto()
    NORTH_WEST = auto()


# =============================================================================
# Helper Classes
# =============================================================================

class Vector2i:
    """Integer 2D vector for grid coordinates."""
    
    def __init__(self, x: int = 0, y: int = 0):
        self.x = int(x)
        self.y = int(y)
    
    def __add__(self, other: Vector2i) -> Vector2i:
        return Vector2i(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: Vector2i) -> Vector2i:
        return Vector2i(self.x - other.x, self.y - other.y)
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Vector2i):
            return False
        return self.x == other.x and self.y == other.y
    
    def __hash__(self) -> int:
        return hash((self.x, self.y))
    
    def __repr__(self) -> str:
        return f"Vector2i({self.x}, {self.y})"


class Rect2i:
    """Integer rectangle for grid regions."""
    
    def __init__(self, x: int = 0, y: int = 0, width: int = 0, height: int = 0):
        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)
    
    def has_point(self, point: Vector2i) -> bool:
        return (
            self.x <= point.x < self.x + self.width and
            self.y <= point.y < self.y + self.height
        )
    
    def __repr__(self) -> str:
        return f"Rect2i({self.x}, {self.y}, {self.width}, {self.height})"


@dataclass
class Shape2D:
    """Base collision shape."""
    pass


@dataclass
class RectangleShape2D(Shape2D):
    """Rectangle collision shape."""
    size: Vector2 = field(default_factory=lambda: Vector2(16, 16))
    
    def translated(self, offset: Vector2) -> RectangleShape2D:
        """Return shape translated by offset."""
        return self  # Position handled separately


@dataclass
class NavigationPolygon:
    """Navigation mesh for A* pathfinding."""
    vertices: List[Vector2] = field(default_factory=list)
    polygons: List[List[int]] = field(default_factory=list)  # Vertex indices


# =============================================================================
# Custom Data Layer
# =============================================================================

@dataclass
class CustomDataLayer:
    """Schema for custom tile data."""
    layer_id: int
    name: str
    type_name: str = "string"  # "string", "int", "float", "bool"
    
    def get_default(self):
        defaults = {
            "string": "",
            "int": 0,
            "float": 0.0,
            "bool": False
        }
        return defaults.get(self.type_name, "")


# =============================================================================
# Physics Layer
# =============================================================================

@dataclass
class PhysicsLayer:
    """Collision layer configuration."""
    layer_id: int
    name: str
    collision_layer: int = 1  # Bitmask
    collision_mask: int = 1   # What it collides with


# =============================================================================
# Terrain Set (Auto-Tiling)
# =============================================================================

class TerrainMode(Enum):
    """Auto-tiling modes."""
    CONNECT = auto()           # Simple connection-based
    MATCH_CORNERS = auto()     # 16-tile (corners matter)
    MATCH_SIDES = auto()       # 47-tile or 16-tile (sides matter)


@dataclass
class TerrainSet:
    """Auto-tiling terrain rules.
    
    Peering bits define which neighbors connect:
    - Each direction gets a bit position
    - Bitmask of connections selects the correct tile variant
    
    Example: MATCH_SIDES with 4 directions
    - NORTH=0b0001, EAST=0b0010, SOUTH=0b0100, WEST=0b1000
    - All neighbors = 0b1111 = 15, selects center tile
    - No neighbors = 0b0000 = 0, selects isolated tile
    """
    
    terrain_id: int
    name: str
    mode: TerrainMode = TerrainMode.MATCH_SIDES
    
    # Bitmask for each direction
    peering_bits: Dict[Direction, int] = field(default_factory=dict)
    
    # tile_selection_table: bitmask -> (atlas_x, atlas_y)
    tile_selection_table: Dict[int, Tuple[int, int]] = field(default_factory=dict)
    
    def __post_init__(self):
        """Set default peering bits if not specified."""
        if not self.peering_bits:
            # Standard 4-direction peering
            self.peering_bits = {
                Direction.NORTH: 0b0001,
                Direction.EAST: 0b0010,
                Direction.SOUTH: 0b0100,
                Direction.WEST: 0b1000,
            }


# =============================================================================
# Tile Data
# =============================================================================

@dataclass
class TileData:
    """Definition of a single tile type.
    
    Properties:
        tile_id: Unique identifier
        atlas_coords: Position in atlas texture (col, row)
        alternative_tiles: Variations for randomization
        physics_shapes: Collision per physics layer {layer_id: [shapes]}
        terrain_peering_bits: {terrain_id: terrain_value}
        custom_data: Arbitrary metadata dict
        probability: Selection weight for random variants
    """
    
    tile_id: int
    atlas_coords: Vector2i
    atlas_source_id: int = 0
    
    alternative_tiles: List[int] = field(default_factory=list)
    
    # Physics shapes indexed by physics layer
    physics_shapes: Dict[int, List[Shape2D]] = field(default_factory=dict)
    
    # Navigation polygons indexed by nav layer
    navigation_polygons: Dict[int, NavigationPolygon] = field(default_factory=dict)
    
    # Custom data storage
    custom_data: Dict[str, Any] = field(default_factory=dict)
    
    # Terrain for auto-tiling
    terrain_peering_bits: Dict[int, int] = field(default_factory=dict)
    
    # Random selection weight
    probability: float = 1.0
    
    # Animation (for animated tiles)
    animation_frames: List[int] = field(default_factory=list)
    animation_speed: float = 0.0


# =============================================================================
# Cell Data (Instance in TileMap)
# =============================================================================

@dataclass
class CellData:
    """A placed tile instance in the tilemap."""
    source_id: int              # Which tile type
    atlas_coords: Optional[Vector2i] = None  # Specific atlas position
    alternative_tile: int = 0  # Which alternative variant
    flip_h: bool = False
    flip_v: bool = False
    transpose: bool = False     # For isometric
    
    # Runtime animation
    animation_frame: int = 0
    animation_time: float = 0.0


# =============================================================================
# TileSet Resource
# =============================================================================

class TileSet:
    """Resource containing all tile definitions.
    
    Can be shared between multiple TileMapLayer nodes.
    
    Properties:
        atlas_texture: Source image
        tile_size: Size of each tile in pixels
        separation: Gap between tiles in atlas
        margin: Outer margin of atlas
        tiles: Dictionary of tile definitions
        physics_layers: Collision layer configs
        navigation_layers: Pathfinding layer configs
        custom_data_layers: Metadata schemas
        terrain_sets: Auto-tiling rules
    """
    
    def __init__(self):
        self.atlas_texture: Optional[Texture2D] = None
        self.tile_size = Vector2i(16, 16)
        self.separation = Vector2i(0, 0)
        self.margin = Vector2i(0, 0)
        self.columns: int = 0  # 0 = auto from texture
        
        # Tile definitions
        self._tiles: Dict[int, TileData] = {}
        
        # Layer configurations
        self.physics_layers: List[PhysicsLayer] = []
        self.navigation_layers: List[Any] = []
        self.custom_data_layers: List[CustomDataLayer] = []
        
        # Auto-tiling
        self.terrain_sets: Dict[int, TerrainSet] = {}
    
    def set_atlas_texture(self, texture: Texture2D, tile_size: Vector2i = None) -> None:
        """Set source texture and auto-generate tiles."""
        self.atlas_texture = texture
        if tile_size:
            self.tile_size = tile_size
        
        # Auto-generate tiles from atlas
        if texture and texture.width > 0:
            tiles_x = texture.width // self.tile_size.x
            tiles_y = texture.height // self.tile_size.y
            
            for y in range(tiles_y):
                for x in range(tiles_x):
                    tile_id = y * tiles_x + x
                    self._tiles[tile_id] = TileData(
                        tile_id=tile_id,
                        atlas_coords=Vector2i(x, y)
                    )
    
    def get_tile(self, tile_id: int) -> Optional[TileData]:
        """Get tile definition by ID."""
        return self._tiles.get(tile_id)
    
    def set_tile(self, tile_data: TileData) -> None:
        """Define or update a tile."""
        self._tiles[tile_data.tile_id] = tile_data
    
    def remove_tile(self, tile_id: int) -> None:
        """Remove a tile definition."""
        if tile_id in self._tiles:
            del self._tiles[tile_id]
    
    def get_source_count(self) -> int:
        """Get number of defined tiles."""
        return len(self._tiles)
    
    def get_terrain_set(self, terrain_id: int) -> Optional[TerrainSet]:
        """Get terrain rules by ID."""
        return self.terrain_sets.get(terrain_id)
    
    def add_terrain_set(self, terrain: TerrainSet) -> None:
        """Add auto-tiling rules."""
        self.terrain_sets[terrain.terrain_id] = terrain
    
    def get_atlas_coords_from_id(self, source_id: int) -> Vector2i:
        """Convert tile ID to atlas coordinates."""
        tile = self._tiles.get(source_id)
        if tile:
            return tile.atlas_coords
        return Vector2i(0, 0)


# =============================================================================
# TileMapLayer
# =============================================================================

class TileMapLayer(Node2D):
    """A single layer of tiles.
    
    Multiple layers can stack (ground, details, collision, foreground).
    
    Properties:
        tile_set: TileSet resource
        tile_size: Override tile size (default from TileSet)
        enabled: Whether to render
        y_sort_enabled: Sort by Y for isometric
    
    Signals:
        cell_changed: When a cell is modified
        changed: When any bulk change occurs
    """
    
    _SIGNALS = ["cell_changed", "changed"]
    
    def __init__(self, name: str = "TileMapLayer"):
        super().__init__(name)
        self.node_type = NodeType.TILEMAPLAYER
        
        self.tile_set: Optional[TileSet] = None
        self.tile_size = Vector2i(16, 16)
        self.position_offset = Vector2(0, 0)
        
        # Rendering
        self.enabled = True
        self.y_sort_enabled = False
        
        # Sparse storage: only store non-empty cells
        self._tile_map: Dict[Vector2i, CellData] = {}
        
        # Physics sync flag
        self._physics_dirty = False
    
    # =======================================================================
    # Cell Operations
    # =======================================================================
    
    def set_cell(self, coords: Vector2i, source_id: int,
                 atlas_coords: Optional[Vector2i] = None,
                 alternative_tile: int = 0) -> None:
        """Place a tile at grid coordinates.
        
        Args:
            coords: Grid position (x, y)
            source_id: Tile type ID from TileSet
            atlas_coords: Specific atlas position (optional)
            alternative_tile: Variant index (0 = default)
        """
        self._tile_map[coords] = CellData(
            source_id=source_id,
            atlas_coords=atlas_coords,
            alternative_tile=alternative_tile
        )
        
        self.signals.emit("cell_changed", coords)
        self._update_terrain_bits(coords)
        self._physics_dirty = True
    
    def erase_cell(self, coords: Vector2i) -> None:
        """Remove tile at coordinates."""
        if coords in self._tile_map:
            del self._tile_map[coords]
            self.signals.emit("cell_changed", coords)
            self._physics_dirty = True
    
    def get_cell_source_id(self, coords: Vector2i) -> int:
        """Get tile ID at coordinates (-1 if empty)."""
        cell = self._tile_map.get(coords)
        return cell.source_id if cell else -1
    
    def get_cell_atlas_coords(self, coords: Vector2i) -> Vector2i:
        """Get atlas coordinates of tile at position."""
        cell = self._tile_map.get(coords)
        if cell and cell.atlas_coords:
            return cell.atlas_coords
        # Return from tileset
        if self.tile_set and cell:
            return self.tile_set.get_atlas_coords_from_id(cell.source_id)
        return Vector2i(-1, -1)
    
    def get_used_cells(self) -> List[Vector2i]:
        """Get all coordinates with tiles."""
        return list(self._tile_map.keys())
    
    def get_used_rect(self) -> Rect2i:
        """Get bounding rectangle of all tiles."""
        if not self._tile_map:
            return Rect2i(0, 0, 0, 0)
        
        coords = list(self._tile_map.keys())
        min_x = min(c.x for c in coords)
        max_x = max(c.x for c in coords)
        min_y = min(c.y for c in coords)
        max_y = max(c.y for c in coords)
        
        return Rect2i(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)
    
    def clear(self) -> None:
        """Remove all tiles."""
        self._tile_map.clear()
        self._physics_dirty = True
        self.signals.emit("changed")
    
    # =======================================================================
    # Coordinate Conversion
    # =======================================================================
    
    def local_to_map(self, local_pos: Vector2) -> Vector2i:
        """Convert pixel position to tile coordinates."""
        tile_size = self.tile_size
        if self.tile_set:
            tile_size = self.tile_set.tile_size
        
        return Vector2i(
            int((local_pos.x - self.position_offset.x) / tile_size.x),
            int((local_pos.y - self.position_offset.y) / tile_size.y)
        )
    
    def map_to_local(self, map_coords: Vector2i) -> Vector2:
        """Convert tile coordinates to pixel position."""
        tile_size = self.tile_size
        if self.tile_set:
            tile_size = self.tile_set.tile_size
        
        return Vector2(
            map_coords.x * tile_size.x + self.position_offset.x,
            map_coords.y * tile_size.y + self.position_offset.y
        )
    
    def get_neighbor_cell(self, coords: Vector2i, direction: Direction) -> Vector2i:
        """Get adjacent cell coordinates."""
        offsets = {
            Direction.NORTH: Vector2i(0, -1),
            Direction.NORTH_EAST: Vector2i(1, -1),
            Direction.EAST: Vector2i(1, 0),
            Direction.SOUTH_EAST: Vector2i(1, 1),
            Direction.SOUTH: Vector2i(0, 1),
            Direction.SOUTH_WEST: Vector2i(-1, 1),
            Direction.WEST: Vector2i(-1, 0),
            Direction.NORTH_WEST: Vector2i(-1, -1),
        }
        return coords + offsets.get(direction, Vector2i(0, 0))
    
    # =======================================================================
    # Terrain Auto-Tiling
    # =======================================================================
    
    def _update_terrain_bits(self, coords: Vector2i) -> None:
        """Update terrain peering bits for auto-tiling.
        
        When a tile changes, check its neighbors and update
        all adjacent tiles' appearance based on terrain rules.
        """
        if not self.tile_set:
            return
        
        # Update the changed cell
        self._update_cell_terrain(coords)
        
        # Update all 8 neighbors (they might need to change)
        for direction in Direction:
            neighbor = self.get_neighbor_cell(coords, direction)
            self._update_cell_terrain(neighbor)
    
    def _update_cell_terrain(self, coords: Vector2i) -> None:
        """Update single cell based on terrain rules."""
        cell = self._tile_map.get(coords)
        if not cell:
            return
        
        tile_data = self.tile_set.get_tile(cell.source_id)
        if not tile_data:
            return
        
        # Check each terrain set this tile belongs to
        for terrain_id in tile_data.terrain_peering_bits:
            terrain_set = self.tile_set.get_terrain_set(terrain_id)
            if not terrain_set:
                continue
            
            # Calculate peering bitmask
            bitmask = self._calculate_peering_bitmask(coords, terrain_id, terrain_set)
            
            # Look up correct tile for this bitmask
            if bitmask in terrain_set.tile_selection_table:
                atlas_x, atlas_y = terrain_set.tile_selection_table[bitmask]
                cell.atlas_coords = Vector2i(atlas_x, atlas_y)
                self._tile_map[coords] = cell
    
    def _calculate_peering_bitmask(self, coords: Vector2i, 
                                    terrain_id: int,
                                    terrain_set: TerrainSet) -> int:
        """Calculate terrain peering bitmask for cell."""
        bitmask = 0
        
        for direction, bit_value in terrain_set.peering_bits.items():
            neighbor_coords = self.get_neighbor_cell(coords, direction)
            neighbor_cell = self._tile_map.get(neighbor_coords)
            
            if neighbor_cell:
                neighbor_tile = self.tile_set.get_tile(neighbor_cell.source_id)
                if neighbor_tile and terrain_id in neighbor_tile.terrain_peering_bits:
                    # Neighbor has same terrain - set bit
                    bitmask |= bit_value
        
        return bitmask
    
    # =======================================================================
    # Physics Integration
    # =======================================================================
    
    def get_collision_shapes(self) -> List[Tuple[Vector2, Shape2D]]:
        """Get all collision shapes with their world positions.
        
        Returns list of (position, shape) for physics engine.
        """
        if not self.tile_set:
            return []
        
        shapes = []
        for coords, cell in self._tile_map.items():
            tile_data = self.tile_set.get_tile(cell.source_id)
            if not tile_data:
                continue
            
            # Get shapes for each physics layer
            for layer_id, layer_shapes in tile_data.physics_shapes.items():
                world_pos = self.to_global(self.map_to_local(coords))
                for shape in layer_shapes:
                    shapes.append((world_pos, shape))
        
        return shapes
    
    # =======================================================================
    # Drawing
    # =======================================================================
    
    def _draw(self, renderer) -> None:
        """Render the tilemap layer."""
        if not self.visible or not self.enabled or not self.tile_set:
            return
        
        for coords, cell in self._tile_map.items():
            # Get atlas coordinates
            atlas_coords = cell.atlas_coords
            if atlas_coords is None:
                atlas_coords = self.tile_set.get_atlas_coords_from_id(cell.source_id)
            
            # Calculate draw position
            world_pos = self.to_global(self.map_to_local(coords))
            
            # Submit to renderer
            if hasattr(renderer, 'draw_tile'):
                renderer.draw_tile(
                    atlas=self.tile_set.atlas_texture,
                    atlas_coords=atlas_coords,
                    tile_size=self.tile_set.tile_size,
                    position=world_pos,
                    flip_h=cell.flip_h,
                    flip_v=cell.flip_v
                )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "Direction",
    "Vector2i",
    "Rect2i",
    "Shape2D",
    "RectangleShape2D",
    "NavigationPolygon",
    "CustomDataLayer",
    "PhysicsLayer",
    "TerrainMode",
    "TerrainSet",
    "TileData",
    "CellData",
    "TileSet",
    "TileMapLayer",
]
