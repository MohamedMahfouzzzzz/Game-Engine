# /**************************************************************************/
# /*  tilemap.py                                                            */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""TileMap node for grid-based 2D levels."""

from typing import Dict, List, Optional, Tuple, Set
from engine.core.node_base import Node2D
from engine.core.types import NodeType

import logging


logger = logging.getLogger(__name__)



class Tile:
    """Single tile data."""

    def __init__(self, tile_id: int = -1, flip_h: bool = False, flip_v: bool = False):
        self.tile_id = tile_id  # -1 means empty
        self.flip_h = flip_h
        self.flip_v = flip_v
        self.custom_data: Dict[str, any] = {}


class TileSet:
    """Collection of tile definitions."""

    def __init__(self, name: str = "TileSet"):
        self.name = name
        self.texture_path: Optional[str] = None
        self.tile_size: Tuple[int, int] = (32, 32)
        self.columns: int = 1
        self.rows: int = 1
        self.tile_count: int = 1

        # Tile-specific data
        self.tile_data: Dict[int, Dict[str, any]] = {}  # tile_id -> properties

    def configure(self, texture_path: str, tile_width: int, tile_height: int,
                  columns: int, rows: int, tile_count: int) -> None:
        """Configure tileset from texture atlas."""
        self.texture_path = texture_path
        self.tile_size = (tile_width, tile_height)
        self.columns = columns
        self.rows = rows
        self.tile_count = tile_count

    def get_tile_uv(self, tile_id: int) -> Tuple[int, int, int, int]:
        """Get texture coordinates for a tile (x, y, w, h)."""
        if tile_id < 0 or tile_id >= self.tile_count:
            return (0, 0, 0, 0)
        col = tile_id % self.columns
        row = tile_id // self.columns
        x = col * self.tile_size[0]
        y = row * self.tile_size[1]
        return (x, y, self.tile_size[0], self.tile_size[1])

    def set_tile_collision(self, tile_id: int, collision: bool) -> None:
        """Set collision property for a tile."""
        if tile_id not in self.tile_data:
            self.tile_data[tile_id] = {}
        self.tile_data[tile_id]["collision"] = collision

    def has_collision(self, tile_id: int) -> bool:
        """Check if a tile has collision."""
        return self.tile_data.get(tile_id, {}).get("collision", False)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "texture_path": self.texture_path,
            "tile_size": self.tile_size,
            "columns": self.columns,
            "rows": self.rows,
            "tile_count": self.tile_count,
            "tile_data": self.tile_data,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TileSet":
        ts = cls(data.get("name", "TileSet"))
        ts.texture_path = data.get("texture_path")
        ts.tile_size = tuple(data.get("tile_size", [32, 32]))
        ts.columns = data.get("columns", 1)
        ts.rows = data.get("rows", 1)
        ts.tile_count = data.get("tile_count", 1)
        ts.tile_data = data.get("tile_data", {})
        return ts


class TileMap(Node2D):
    """A grid-based map of tiles."""

    def __init__(self, name: str = "TileMap"):
        super().__init__(name)
        self.node_type = NodeType.TILEMAP

        # Grid configuration
        self.cell_size: Tuple[int, int] = (32, 32)
        self.grid_size: Tuple[int, int] = (10, 10)  # width, height in cells

        # Tile storage: {(x, y): Tile}
        self.tiles: Dict[Tuple[int, int], Tile] = {}

        # TileSet reference
        self.tileset: Optional[TileSet] = None

        # Rendering options
        self.show_grid_lines: bool = False
        self.grid_line_color: Tuple[int, int, int, int] = (128, 128, 128, 128)

    def set_cell(self, x: int, y: int, tile_id: int, flip_h: bool = False, flip_v: bool = False) -> None:
        """Set a tile at grid position."""
        if tile_id < 0:
            # Remove tile
            if (x, y) in self.tiles:
                del self.tiles[(x, y)]
        else:
            self.tiles[(x, y)] = Tile(tile_id, flip_h, flip_v)

    def get_cell(self, x: int, y: int) -> Optional[Tile]:
        """Get tile at grid position."""
        return self.tiles.get((x, y))

    def get_cell_id(self, x: int, y: int) -> int:
        """Get tile ID at position (-1 if empty)."""
        tile = self.tiles.get((x, y))
        return tile.tile_id if tile else -1

    def clear(self) -> None:
        """Remove all tiles."""
        self.tiles.clear()

    def fill_rect(self, x: int, y: int, width: int, height: int, tile_id: int) -> None:
        """Fill a rectangular area with a tile."""
        for py in range(y, y + height):
            for px in range(x, x + width):
                self.set_cell(px, py, tile_id)

    def get_used_cells(self) -> Set[Tuple[int, int]]:
        """Get all positions that have tiles."""
        return set(self.tiles.keys())

    def get_used_rect(self) -> Tuple[int, int, int, int]:
        """Get bounding rectangle of used cells (x, y, width, height)."""
        if not self.tiles:
            return (0, 0, 0, 0)
        xs = [pos[0] for pos in self.tiles.keys()]
        ys = [pos[1] for pos in self.tiles.keys()]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        return (min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)

    def world_to_map(self, world_x: float, world_y: float) -> Tuple[int, int]:
        """Convert world coordinates to grid coordinates."""
        mx = int(world_x / self.cell_size[0])
        my = int(world_y / self.cell_size[1])
        return (mx, my)

    def map_to_world(self, map_x: int, map_y: int) -> Tuple[float, float]:
        """Convert grid coordinates to world coordinates (center of cell)."""
        wx = map_x * self.cell_size[0] + self.cell_size[0] / 2
        wy = map_y * self.cell_size[1] + self.cell_size[1] / 2
        return (wx, wy)

    def set_tileset(self, tileset: TileSet) -> None:
        """Assign a tileset to this tilemap."""
        self.tileset = tileset
        self.cell_size = tileset.tile_size

    def get_collision_tiles(self) -> List[Tuple[int, int]]:
        """Get positions of tiles that have collision enabled."""
        if not self.tileset:
            return []
        return [
            pos for pos, tile in self.tiles.items()
            if self.tileset.has_collision(tile.tile_id)
        ]

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        data = super().to_dict()
        data.update({
            "cell_size": self.cell_size,
            "grid_size": self.grid_size,
            "tiles": {
                f"{x},{y}": {"id": t.tile_id, "flip_h": t.flip_h, "flip_v": t.flip_v}
                for (x, y), t in self.tiles.items()
            },
            "tileset": self.tileset.to_dict() if self.tileset else None,
            "show_grid_lines": self.show_grid_lines,
        })
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "TileMap":
        """Create from dictionary."""
        tm = cls(data.get("name", "TileMap"))
        tm.cell_size = tuple(data.get("cell_size", [32, 32]))
        tm.grid_size = tuple(data.get("grid_size", [10, 10]))
        tm.show_grid_lines = data.get("show_grid_lines", False)

        # Load tiles
        for key, tdata in data.get("tiles", {}).items():
            x, y = map(int, key.split(","))
            tm.set_cell(x, y, tdata.get("id", -1), tdata.get("flip_h", False), tdata.get("flip_v", False))

        # Load tileset
        ts_data = data.get("tileset")
        if ts_data:
            tm.tileset = TileSet.from_dict(ts_data)

        return tm
