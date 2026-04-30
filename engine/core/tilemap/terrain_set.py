# /**************************************************************************/
# /*  tilemap/terrain_set.py                                                */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""TerrainSet for auto-tiling with peering bits."""

from __future__ import annotations

from enum import Enum, auto
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass, field

from .types import Direction, Vector2i

class TerrainMode(Enum):
    """Terrain matching mode."""
    CONNECT = auto()  # Match specific terrain IDs
    PATH = auto()     # Path-like connections


@dataclass
class TerrainEntry:
    """Terrain entry with tile selection table."""
    terrain_id: int = -1
    valid_peering_bits: Set[int] = field(default_factory=set)
    tile_selection_table: Dict[int, Vector2i] = field(default_factory=dict)


class TerrainSet:
    """Terrain auto-tiling system using peering bits.
    
    Matches neighboring tiles and selects appropriate sprite
    based on 8-bit peering configuration.
    
    Peering bits (clockwise from top):
        bit 0: TOP
        bit 1: TOP-RIGHT
        bit 2: RIGHT
        bit 3: BOTTOM-RIGHT
        bit 4: BOTTOM
        bit 5: BOTTOM-LEFT
        bit 6: LEFT
        bit 7: TOP-LEFT
    
    For 2x2 minimal sets, uses 4 bits:
        bit 0: TOP
        bit 1: RIGHT
        bit 2: BOTTOM
        bit 3: LEFT
    """
    
    def __init__(self, terrain_set_id: int = 0):
        self.terrain_set_id = terrain_set_id
        self.mode = TerrainMode.CONNECT
        self.use_corner_bits = False
        
        # Terrain types in this set
        self.terrains: Dict[int, TerrainEntry] = {}
        
        # Bit names for reference
        self._bit_names = [
            "top", "top_right", "right", "bottom_right",
            "bottom", "bottom_left", "left", "top_left"
        ]
    
    def add_terrain(self, terrain_id: int, name: str, color: Tuple[int, int, int] = (255, 255, 255)) -> TerrainEntry:
        """Add a new terrain type."""
        entry = TerrainEntry(terrain_id=terrain_id)
        self.terrains[terrain_id] = entry
        return entry
    
    def set_tile_for_bits(self, terrain_id: int, peering_bits: int, atlas_coords: Vector2i) -> None:
        """Map peering bit pattern to atlas coordinates."""
        if terrain_id not in self.terrains:
            self.add_terrain(terrain_id, f"Terrain_{terrain_id}")
        
        entry = self.terrains[terrain_id]
        entry.valid_peering_bits.add(peering_bits)
        entry.tile_selection_table[peering_bits] = atlas_coords
    
    def get_tile_for_bits(self, terrain_id: int, peering_bits: int) -> Vector2i:
        """Get atlas coordinates for peering bit pattern."""
        if terrain_id not in self.terrains:
            return Vector2i(0, 0)
        
        entry = self.terrains[terrain_id]
        
        # Exact match
        if peering_bits in entry.tile_selection_table:
            return entry.tile_selection_table[peering_bits]
        
        # Find closest match (fallback)
        # Simplified: return first available
        if entry.tile_selection_table:
            return next(iter(entry.tile_selection_table.values()))
        
        return Vector2i(0, 0)
    
    def calculate_peering_bits(
        self,
        center_terrain: int,
        neighbors: Dict[Direction, int]
    ) -> int:
        """Calculate 8-bit peering mask from neighbors."""
        bits = 0
        
        # Map directions to bit positions
        bit_map = {
            Direction.TOP: 0,
            Direction.TOP_RIGHT: 1,
            Direction.RIGHT: 2,
            Direction.BOTTOM_RIGHT: 3,
            Direction.BOTTOM: 4,
            Direction.BOTTOM_LEFT: 5,
            Direction.LEFT: 6,
            Direction.TOP_LEFT: 7,
        }
        
        for direction, neighbor_terrain in neighbors.items():
            if neighbor_terrain == center_terrain:
                if direction in bit_map:
                    bits |= (1 << bit_map[direction])
        
        return bits
    
    def get_minimum_required_tiles(self) -> int:
        """Get minimum tile count for this mode."""
        if self.use_corner_bits:
            return 256  # 8 bits
        return 16  # 4 cardinal directions


__all__ = ["TerrainMode", "TerrainSet", "TerrainEntry"]
