# /**************************************************************************/
# /*  tile_map.py                                                           */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""TileMap node for 2D tile-based games."""

from enum import IntEnum
from typing import Dict, List, Optional, Tuple
from engine.core.nodes2d import Node2D, Vector2, Color
from engine.scene2d.tile_set import TileSet, TileData


class TileMapLayer:
    """Single layer in a tilemap."""
    
    def __init__(self, name: str = "Layer"):
        self._name: str = name
        self._enabled: bool = True
        self._modulate: Color = Color(1, 1, 1, 1)
        self._y_sort_enabled: bool = False
        self._y_sort_origin: int = 0
        self._z_index: int = 0
        self._tint: Color = Color(1, 1, 1, 1)
        self._cells: Dict[Tuple[int, int], Dict] = {}
    
    def get_name(self) -> str:
        return self._name
    
    def set_name(self, name: str) -> None:
        self._name = name
    
    def is_enabled(self) -> bool:
        return self._enabled
    
    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled
    
    def get_modulate(self) -> Color:
        return self._modulate
    
    def set_modulate(self, color: Color) -> None:
        self._modulate = color
    
    def get_z_index(self) -> int:
        return self._z_index
    
    def set_z_index(self, z: int) -> None:
        self._z_index = z


class TileMap(Node2D):
    """Node for placing tiles from a TileSet on a grid.
    
    Features:
    - Multiple layers with individual settings
    - Y-sorting for isometric/top-down
    - Terrain auto-tiling system
    - Physics/navigation/collision integration
    """
    
    def __init__(self, name: str = "TileMap"):
        super().__init__(name)
        self._tile_set: Optional[TileSet] = None
        self._layers: List[TileMapLayer] = [TileMapLayer("Layer0")]
        self._rendering_quadrant_size: int = 16
        self._collision_animatable: bool = False
        self._collision_visibility_mode: int = 0
        self._navigation_visibility_mode: int = 0
        self._tile_shape: int = 0
        self._tile_layout: int = 0
        self._tile_offset_axis: int = 0
        
    def set_tile_set(self, tile_set: Optional[TileSet]) -> None:
        """Set the TileSet resource."""
        self._tile_set = tile_set
    
    def get_tile_set(self) -> Optional[TileSet]:
        """Get the TileSet resource."""
        return self._tile_set
    
    def get_layers_count(self) -> int:
        """Get number of layers."""
        return len(self._layers)
    
    def add_layer(self, to_position: int) -> None:
        """Add layer at position."""
        layer = TileMapLayer(f"Layer{len(self._layers)}")
        if 0 <= to_position <= len(self._layers):
            self._layers.insert(to_position, layer)
        else:
            self._layers.append(layer)
    
    def remove_layer(self, layer: int) -> None:
        """Remove layer by index."""
        if 0 <= layer < len(self._layers):
            del self._layers[layer]
    
    def move_layer(self, layer: int, to_position: int) -> None:
        """Move layer to new position."""
        if 0 <= layer < len(self._layers) and 0 <= to_position <= len(self._layers):
            l = self._layers.pop(layer)
            self._layers.insert(to_position, l)
    
    def set_layer_enabled(self, layer: int, enabled: bool) -> None:
        """Enable/disable layer."""
        if 0 <= layer < len(self._layers):
            self._layers[layer].set_enabled(enabled)
    
    def is_layer_enabled(self, layer: int) -> bool:
        if 0 <= layer < len(self._layers):
            return self._layers[layer].is_enabled()
        return False
    
    def set_layer_modulate(self, layer: int, color: Color) -> None:
        """Set layer color modulate."""
        if 0 <= layer < len(self._layers):
            self._layers[layer].set_modulate(color)
    
    def get_layer_modulate(self, layer: int) -> Color:
        if 0 <= layer < len(self._layers):
            return self._layers[layer].get_modulate()
        return Color(1, 1, 1, 1)
    
    def set_layer_z_index(self, layer: int, z: int) -> None:
        """Set layer Z index."""
        if 0 <= layer < len(self._layers):
            self._layers[layer].set_z_index(z)
    
    def get_layer_z_index(self, layer: int) -> int:
        if 0 <= layer < len(self._layers):
            return self._layers[layer].get_z_index()
        return 0
    
    def set_cell(self, layer: int, coords: Tuple[int, int], source_id: int,
                 atlas_coords: Tuple[int, int] = (-1, -1),
                 alternative_tile: int = 0) -> None:
        """Place tile at coordinates."""
        if not (0 <= layer < len(self._layers)):
            return
        
        self._layers[layer]._cells[coords] = {
            'source_id': source_id,
            'atlas_coords': atlas_coords,
            'alternative_tile': alternative_tile
        }
    
    def erase_cell(self, layer: int, coords: Tuple[int, int]) -> None:
        """Remove tile at coordinates."""
        if 0 <= layer < len(self._layers):
            if coords in self._layers[layer]._cells:
                del self._layers[layer]._cells[coords]
    
    def get_cell_source_id(self, layer: int, coords: Tuple[int, int]) -> int:
        """Get source ID of tile at coords."""
        if 0 <= layer < len(self._layers):
            cell = self._layers[layer]._cells.get(coords)
            if cell:
                return cell.get('source_id', -1)
        return -1
    
    def get_cell_atlas_coords(self, layer: int, coords: Tuple[int, int]) -> Tuple[int, int]:
        """Get atlas coords of tile."""
        if 0 <= layer < len(self._layers):
            cell = self._layers[layer]._cells.get(coords)
            if cell:
                return cell.get('atlas_coords', (-1, -1))
        return (-1, -1)
    
    def clear_layer(self, layer: int) -> None:
        """Clear all cells in layer."""
        if 0 <= layer < len(self._layers):
            self._layers[layer]._cells.clear()
    
    def clear(self) -> None:
        """Clear all layers."""
        for layer in self._layers:
            layer._cells.clear()
    
    def get_used_cells(self, layer: int) -> List[Tuple[int, int]]:
        """Get list of coordinates with tiles."""
        if 0 <= layer < len(self._layers):
            return list(self._layers[layer]._cells.keys())
        return []
    
    def get_used_rect(self, layer: int) -> Tuple[int, int, int, int]:
        """Get bounding rectangle of used cells as (x, y, w, h)."""
        cells = self.get_used_cells(layer)
        if not cells:
            return (0, 0, 0, 0)
        
        xs = [c[0] for c in cells]
        ys = [c[1] for c in cells]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        return (min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)
    
    def map_to_local(self, map_position: Tuple[int, int]) -> Vector2:
        """Convert map coordinates to local position."""
        tile_size = self._tile_set.get_tile_size() if self._tile_set else Vector2(16, 16)
        return Vector2(
            map_position[0] * tile_size.x,
            map_position[1] * tile_size.y
        )
    
    def local_to_map(self, local_position: Vector2) -> Tuple[int, int]:
        """Convert local position to map coordinates."""
        tile_size = self._tile_set.get_tile_size() if self._tile_set else Vector2(16, 16)
        return (
            int(local_position.x / tile_size.x),
            int(local_position.y / tile_size.y)
        )
    
    def __repr__(self) -> str:
        cells = sum(len(l._cells) for l in self._layers)
        return f"TileMap('{self.name}', layers={len(self._layers)}, cells={cells})"
