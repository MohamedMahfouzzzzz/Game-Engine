# /**************************************************************************/
# /*  tilemap2d.py                                                           */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""TileMap2D - 2D tilemap for grid-based games."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple, Set
from enum import Enum

from .types import Vector2, Vector2i, Color, Texture2D
from .node2d import Node2D

import logging


logger = logging.getLogger(__name__)


class TileMap2D(Node2D):
    """2D tilemap node for creating grid-based worlds.
    
    Properties:
        cell_size: Size of each tile cell (Vector2i)
        tile_set: Dictionary mapping tile IDs to textures
        cells: Dictionary of cell positions to tile IDs
        tile_rotation: Dictionary of cell positions to rotation (0, 90, 180, 270)
        tile_flip: Dictionary of cell positions to flip flags (h, v)
        
    Signals:
        cell_changed: Emitted when a cell is modified
        cell_cleared: Emitted when cells are cleared
    """
    
    __slots__ = [
        "cell_size",
        "_tile_set", "_cells",
        "_tile_rotation", "_tile_flip",
        "_collision_cells"
    ]
    
    _SIGNALS = ["cell_changed", "cell_cleared", "cell_filled"]
    
    def __init__(self, name: str = "TileMap2D"):
        super().__init__(name)
        self.node_type = "TileMap2D"
        
        # Grid settings
        self.cell_size: Vector2i = Vector2i(32, 32)
        
        # Tile set - mapping tile_id -> texture
        self._tile_set: Dict[int, Optional[Texture2D]] = {}
        
        # Cell data - mapping (x, y) -> tile_id
        self._cells: Dict[Tuple[int, int], int] = {}
        
        # Transform per cell
        self._tile_rotation: Dict[Tuple[int, int], int] = {}  # 0, 90, 180, 270
        self._tile_flip: Dict[Tuple[int, int], Tuple[bool, bool]] = {}  # (flip_h, flip_v)
        
        # Collision data
        self._collision_cells: Set[Tuple[int, int]] = set()
    
    def set_cell_size(self, width: int, height: int) -> None:
        """Set the size of each tile cell."""
        self.cell_size = Vector2i(width, height)
    
    def add_tile(self, tile_id: int, texture: Texture2D) -> None:
        """Add a tile to the tile set."""
        self._tile_set[tile_id] = texture
    
    def remove_tile(self, tile_id: int) -> None:
        """Remove a tile from the tile set."""
        if tile_id in self._tile_set:
            del self._tile_set[tile_id]
            # Remove cells using this tile
            cells_to_remove = [pos for pos, tid in self._cells.items() if tid == tile_id]
            for pos in cells_to_remove:
                self.erase_cell(*pos)
    
    def set_cell(self, x: int, y: int, tile_id: int, 
                 flip_h: bool = False, flip_v: bool = False,
                 rotation: int = 0) -> None:
        """Set a cell to use a specific tile.
        
        Args:
            x, y: Cell coordinates
            tile_id: ID of tile to use (must be in tile_set)
            flip_h: Flip horizontally
            flip_v: Flip vertically
            rotation: Rotation in degrees (0, 90, 180, 270)
        """
        if tile_id not in self._tile_set:
            logger.warning(f"Tile ID {tile_id} not in tile set")
            return
        
        pos = (x, y)
        self._cells[pos] = tile_id
        self._tile_flip[pos] = (flip_h, flip_v)
        self._tile_rotation[pos] = rotation % 360
        
        self.signals.emit("cell_changed", pos, tile_id)
    
    def erase_cell(self, x: int, y: int) -> None:
        """Clear a cell (set to empty)."""
        pos = (x, y)
        if pos in self._cells:
            del self._cells[pos]
            if pos in self._tile_flip:
                del self._tile_flip[pos]
            if pos in self._tile_rotation:
                del self._tile_rotation[pos]
            if pos in self._collision_cells:
                self._collision_cells.discard(pos)
            self.signals.emit("cell_cleared", pos)
    
    def get_cell(self, x: int, y: int) -> int:
        """Get tile ID at cell position (-1 if empty)."""
        return self._cells.get((x, y), -1)
    
    def has_cell(self, x: int, y: int) -> bool:
        """Check if cell has a tile."""
        return (x, y) in self._cells
    
    def clear(self) -> None:
        """Clear all cells."""
        self._cells.clear()
        self._tile_flip.clear()
        self._tile_rotation.clear()
        self._collision_cells.clear()
        self.signals.emit("cell_cleared", None)
    
    def fill_rect(self, x: int, y: int, w: int, h: int, tile_id: int) -> None:
        """Fill a rectangle with a tile."""
        for dx in range(w):
            for dy in range(h):
                self.set_cell(x + dx, y + dy, tile_id)
        self.signals.emit("cell_filled", (x, y, w, h), tile_id)
    
    def get_used_cells(self) -> List[Tuple[int, int]]:
        """Get list of all cells that have tiles."""
        return list(self._cells.keys())
    
    def get_used_rect(self) -> Optional[Tuple[int, int, int, int]]:
        """Get bounding rectangle of used cells (x, y, width, height)."""
        if not self._cells:
            return None
        
        xs = [p[0] for p in self._cells.keys()]
        ys = [p[1] for p in self._cells.keys()]
        
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        return (min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)
    
    def map_to_world(self, x: int, y: int) -> Vector2:
        """Convert cell coordinates to world position."""
        return Vector2(
            x * self.cell_size.x,
            y * self.cell_size.y
        )
    
    def world_to_map(self, world_pos: Vector2) -> Vector2i:
        """Convert world position to cell coordinates."""
        return Vector2i(
            int(world_pos.x / self.cell_size.x),
            int(world_pos.y / self.cell_size.y)
        )
    
    def set_collision_cell(self, x: int, y: int, enabled: bool) -> None:
        """Mark/unmark a cell as having collision."""
        pos = (x, y)
        if enabled:
            self._collision_cells.add(pos)
        else:
            self._collision_cells.discard(pos)
    
    def has_collision(self, x: int, y: int) -> bool:
        """Check if cell has collision."""
        return (x, y) in self._collision_cells
    
    def get_collision_rect(self, x: int, y: int) -> Optional[Tuple[float, float, float, float]]:
        """Get collision rectangle for a cell."""
        if not self.has_collision(x, y):
            return None
        
        world_pos = self.map_to_world(x, y)
        return (
            world_pos.x,
            world_pos.y,
            self.cell_size.x,
            self.cell_size.y
        )
    
    def _draw(self, renderer) -> None:
        """Draw all visible tiles."""
        if not self.visible:
            return
        
        for (x, y), tile_id in self._cells.items():
            texture = self._tile_set.get(tile_id)
            if not texture or not texture.is_loaded():
                continue
            
            # Calculate world position
            world_pos = self.map_to_world(x, y)
            
            # Get flip and rotation
            flip = self._tile_flip.get((x, y), (False, False))
            rotation = self._tile_rotation.get((x, y), 0)
            
            # Draw via renderer
            if hasattr(renderer, 'draw_tile'):
                renderer.draw_tile(
                    texture=texture,
                    position=world_pos,
                    size=(self.cell_size.x, self.cell_size.y),
                    flip_h=flip[0],
                    flip_v=flip[1],
                    rotation=rotation
                )
