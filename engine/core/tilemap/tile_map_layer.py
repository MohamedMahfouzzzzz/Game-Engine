# /**************************************************************************/
# /*  tilemap/tile_map_layer.py                                             */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""TileMapLayer for grid storage and terrain auto-tiling."""

from __future__ import annotations

from typing import Dict, List, Optional, Iterator, Tuple
from dataclasses import dataclass, field

from engine.core.node_base import Node
from engine.core.types import NodeType
from .types import Vector2i, Rect2i, Direction
from .tile_set import TileSet, TileData
from .terrain_set import TerrainSet

@dataclass
class CellData:
    """Data for a single cell in tilemap."""
    coords: Vector2i = field(default_factory=lambda: Vector2i(0, 0))
    source_id: int = -1
    atlas_coords: Vector2i = field(default_factory=lambda: Vector2i(-1, -1))
    alternative_tile: int = 0
    terrain_set: int = -1
    terrain: int = -1
    flip_h: bool = False
    flip_v: bool = False
    transpose: bool = False
    
    def is_empty(self) -> bool:
        return self.source_id == -1


class TileMapLayer(Node):
    """Layer of tile data with grid storage.
    
    Features:
        - Sparse storage (only non-empty cells stored)
        - Terrain auto-tiling
        - Y-sort for isometric
        - Physics sync
    
    Properties:
        tile_set: TileSet resource
        tile_size: Override tile size
        enabled: Whether to render
        y_sort_enabled: Sort by Y for isometric
    
    Signals:
        cell_changed: When a cell is modified
        changed: When any bulk change occurs
    """
    
    _SIGNALS = ["cell_changed", "changed"]
    
    def __init__(self, name: str = "TileMapLayer"):
        super().__init__(name, NodeType.TILEMAPLAYER)
        
        self.tile_set: Optional[TileSet] = None
        self.tile_size = Vector2i(16, 16)
        self.position_offset = (0, 0)  # Tuple instead of Vector2
        
        # Rendering
        self.enabled = True
        self.y_sort_enabled = False
        
        # Sparse storage: only store non-empty cells
        self._cells: Dict[Tuple[int, int], CellData] = {}
        
        # For terrain auto-tiling
        self._dirty_cells: List[Vector2i] = []
    
    def set_cell(
        self,
        coords: Vector2i,
        source_id: int = -1,
        atlas_coords: Optional[Vector2i] = None,
        alternative_tile: int = 0
    ) -> None:
        """Place tile at coordinates."""
        key = (coords.x, coords.y)
        
        if source_id == -1:
            # Erase cell
            if key in self._cells:
                del self._cells[key]
                self._dirty_cells.append(coords)
                self.signals.emit("cell_changed", coords, None)
            return
        
        # Set cell
        cell = CellData(
            coords=coords,
            source_id=source_id,
            atlas_coords=atlas_coords or Vector2i(-1, -1),
            alternative_tile=alternative_tile
        )
        
        self._cells[key] = cell
        self._dirty_cells.append(coords)
        self.signals.emit("cell_changed", coords, cell)
    
    def erase_cell(self, coords: Vector2i) -> None:
        """Remove tile at coordinates."""
        self.set_cell(coords, -1)
    
    def get_cell(self, coords: Vector2i) -> CellData:
        """Get cell data (returns empty if none)."""
        key = (coords.x, coords.y)
        return self._cells.get(key, CellData(coords=coords))
    
    def get_cell_source_id(self, coords: Vector2i) -> int:
        """Get source ID at coordinates (-1 if empty)."""
        return self.get_cell(coords).source_id
    
    def get_cell_atlas_coords(self, coords: Vector2i) -> Vector2i:
        """Get atlas coordinates at position."""
        return self.get_cell(coords).atlas_coords
    
    def has_cell(self, coords: Vector2i) -> bool:
        """Check if cell has a tile."""
        return (coords.x, coords.y) in self._cells
    
    def get_used_cells(self) -> List[Vector2i]:
        """Get list of all non-empty cell coordinates."""
        return [Vector2i(x, y) for x, y in self._cells.keys()]
    
    def get_used_rect(self) -> Rect2i:
        """Get bounding rectangle of used cells."""
        if not self._cells:
            return Rect2i(0, 0, 0, 0)
        
        xs = [x for x, y in self._cells.keys()]
        ys = [y for x, y in self._cells.keys()]
        
        return Rect2i(
            min(xs),
            min(ys),
            max(xs) - min(xs) + 1,
            max(ys) - min(ys) + 1
        )
    
    def map_to_local(self, coords: Vector2i) -> Tuple[float, float]:
        """Convert grid coordinates to local position."""
        x = coords.x * self.tile_size.x + self.position_offset[0]
        y = coords.y * self.tile_size.y + self.position_offset[1]
        return (x, y)
    
    def local_to_map(self, local: Tuple[float, float]) -> Vector2i:
        """Convert local position to grid coordinates."""
        x = int((local[0] - self.position_offset[0]) // self.tile_size.x)
        y = int((local[1] - self.position_offset[1]) // self.tile_size.y)
        return Vector2i(x, y)
    
    def get_surrounding_cells(self, coords: Vector2i) -> Dict[Direction, CellData]:
        """Get neighboring cells."""
        result = {}
        directions = list(Direction)
        
        for direction in directions:
            offset = {
                Direction.TOP: Vector2i(0, -1),
                Direction.TOP_RIGHT: Vector2i(1, -1),
                Direction.RIGHT: Vector2i(1, 0),
                Direction.BOTTOM_RIGHT: Vector2i(1, 1),
                Direction.BOTTOM: Vector2i(0, 1),
                Direction.BOTTOM_LEFT: Vector2i(-1, 1),
                Direction.LEFT: Vector2i(-1, 0),
                Direction.TOP_LEFT: Vector2i(-1, -1),
            }
            neighbor_coords = coords + offset.get(direction, Vector2i(0, 0))
            result[direction] = self.get_cell(neighbor_coords)
        
        return result
    
    def update_terrain(self, coords: Vector2i, terrain_set: TerrainSet) -> None:
        """Update terrain auto-tiling for cell."""
        cell = self.get_cell(coords)
        if cell.is_empty() or cell.terrain == -1:
            return
        
        # Get neighbors
        neighbors = self.get_surrounding_cells(coords)
        neighbor_terrains = {
            d: n.terrain for d, n in neighbors.items()
        }
        
        # Calculate peering bits
        peering_bits = terrain_set.calculate_peering_bits(
            cell.terrain,
            neighbor_terrains
        )
        
        # Get new atlas coords
        new_atlas = terrain_set.get_tile_for_bits(cell.terrain, peering_bits)
        
        # Update cell
        if new_atlas != cell.atlas_coords:
            cell.atlas_coords = new_atlas
            self.signals.emit("cell_changed", coords, cell)
    
    def clear(self) -> None:
        """Remove all tiles."""
        self._cells.clear()
        self.signals.emit("changed")


__all__ = ["TileMapLayer", "CellData"]
