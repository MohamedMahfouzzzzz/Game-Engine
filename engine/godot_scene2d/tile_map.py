# /**************************************************************************/
# /*  tile_map.py                                                           */
# /**************************************************************************/

"""Godot TileMap port - 2D tile-based map."""

from typing import Dict, List, Optional, Tuple
from engine.core.nodes2d import Node2D
from engine.godot_scene2d.types import Point2, Vector2i, Rect2


class TileMapLayer:
    """Single layer in a TileMap."""
    
    def __init__(self, name: str = "Layer"):
        self.name = name
        self._cells: Dict[Tuple[int, int], int] = {}
        self._enabled: bool = True
        self._modulate: 'Color' = None  # Would be Color
    
    def set_cell(self, x: int, y: int, tile_id: int) -> None:
        if tile_id >= 0:
            self._cells[(x, y)] = tile_id
        elif (x, y) in self._cells:
            del self._cells[(x, y)]
    
    def erase_cell(self, x: int, y: int) -> None:
        if (x, y) in self._cells:
            del self._cells[(x, y)]
    
    def get_cell(self, x: int, y: int) -> int:
        return self._cells.get((x, y), -1)
    
    def get_used_cells(self) -> List[Vector2i]:
        return [Vector2i(x, y) for (x, y) in self._cells.keys()]
    
    def get_used_cells_count(self) -> int:
        return len(self._cells)
    
    def clear(self) -> None:
        self._cells.clear()


class TileMap(Node2D):
    """2D tile-based map system."""
    
    def __init__(self, name: str = "TileMap"):
        super().__init__(name)
        self._layers: List[TileMapLayer] = [TileMapLayer("Layer0")]
        self._cell_size: Vector2i = Vector2i(16, 16)
        self._tile_set: Optional['TileSet'] = None
        self._rendering_quadrant_size: int = 16
        self._collision_visibility_mode: int = 0
        self._navigation_visibility_mode: int = 0
    
    def set_cell_size(self, size: Vector2i) -> None:
        self._cell_size = size
    
    def get_cell_size(self) -> Vector2i:
        return self._cell_size
    
    def set_tileset(self, tileset: Optional['TileSet']) -> None:
        self._tile_set = tileset
    
    def get_tileset(self) -> Optional['TileSet']:
        return self._tile_set
    
    def add_layer(self, layer_index: int = -1) -> int:
        layer = TileMapLayer(f"Layer{len(self._layers)}")
        if layer_index < 0 or layer_index >= len(self._layers):
            self._layers.append(layer)
            return len(self._layers) - 1
        else:
            self._layers.insert(layer_index, layer)
            return layer_index
    
    def remove_layer(self, layer_index: int) -> None:
        if 0 <= layer_index < len(self._layers):
            del self._layers[layer_index]
    
    def get_layers_count(self) -> int:
        return len(self._layers)
    
    def set_layer_name(self, layer: int, name: str) -> None:
        if 0 <= layer < len(self._layers):
            self._layers[layer].name = name
    
    def get_layer_name(self, layer: int) -> str:
        if 0 <= layer < len(self._layers):
            return self._layers[layer].name
        return ""
    
    def set_layer_enabled(self, layer: int, enabled: bool) -> None:
        if 0 <= layer < len(self._layers):
            self._layers[layer]._enabled = enabled
    
    def is_layer_enabled(self, layer: int) -> bool:
        if 0 <= layer < len(self._layers):
            return self._layers[layer]._enabled
        return False
    
    def set_cell(self, layer: int, coords: Vector2i, tile_id: int, alternative_id: int = 0) -> None:
        if 0 <= layer < len(self._layers):
            self._layers[layer].set_cell(coords.x, coords.y, tile_id)
    
    def erase_cell(self, layer: int, coords: Vector2i) -> None:
        if 0 <= layer < len(self._layers):
            self._layers[layer].erase_cell(coords.x, coords.y)
    
    def get_cell_atlas_coords(self, layer: int, coords: Vector2i, use_proxies: bool = False) -> Vector2i:
        return Vector2i()
    
    def get_cell_source_id(self, layer: int, coords: Vector2i, use_proxies: bool = False) -> int:
        if 0 <= layer < len(self._layers):
            return self._layers[layer].get_cell(coords.x, coords.y)
        return -1
    
    def get_used_cells(self, layer: int) -> List[Vector2i]:
        if 0 <= layer < len(self._layers):
            return self._layers[layer].get_used_cells()
        return []
    
    def get_used_cells_count(self, layer: int) -> int:
        if 0 <= layer < len(self._layers):
            return self._layers[layer].get_used_cells_count()
        return 0
    
    def get_used_rect(self, layer: int = -1) -> Rect2:
        cells = []
        if layer < 0:
            for l in self._layers:
                cells.extend(l.get_used_cells())
        elif layer < len(self._layers):
            cells = self._layers[layer].get_used_cells()
        
        if not cells:
            return Rect2()
        
        min_x = min(c.x for c in cells)
        max_x = max(c.x for c in cells)
        min_y = min(c.y for c in cells)
        max_y = max(c.y for c in cells)
        
        from engine.godot_scene2d.types import Point2, Size2
        return Rect2(
            Point2(min_x * self._cell_size.x, min_y * self._cell_size.y),
            Size2((max_x - min_x + 1) * self._cell_size.x, (max_y - min_y + 1) * self._cell_size.y)
        )
    
    def map_to_local(self, map_position: Vector2i) -> Point2:
        return Point2(
            map_position.x * self._cell_size.x,
            map_position.y * self._cell_size.y
        )
    
    def local_to_map(self, local_position: Point2) -> Vector2i:
        return Vector2i(
            int(local_position.x / self._cell_size.x),
            int(local_position.y / self._cell_size.y)
        )
    
    def clear_layer(self, layer: int) -> None:
        if 0 <= layer < len(self._layers):
            self._layers[layer].clear()
    
    def clear(self) -> None:
        for layer in self._layers:
            layer.clear()
    
    def __repr__(self) -> str:
        layer_info = ", ".join(f"L{i}:{l.get_used_cells_count()}" for i, l in enumerate(self._layers))
        return f"TileMap('{self.name}', {layer_info})"
