# /**************************************************************************/
# /*  tilemap/__init__.py                                                   */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""TileMap system for 2D grid-based worlds."""

# Core types
from .types import Direction, Vector2i, Rect2i, Shape2D, RectangleShape2D

# TileSet resources
from .tile_set import TileSet, TileData, PhysicsLayer, NavigationPolygon, CustomDataLayer

# Terrain system
from .terrain_set import TerrainMode, TerrainSet

# TileMap layer
from .tile_map_layer import TileMapLayer, CellData

import logging


logger = logging.getLogger(__name__)


__all__ = [
    # Types
    "Direction",
    "Vector2i",
    "Rect2i",
    "Shape2D",
    "RectangleShape2D",
    # TileSet
    "TileSet",
    "TileData",
    "PhysicsLayer",
    "NavigationPolygon",
    "CustomDataLayer",
    # Terrain
    "TerrainMode",
    "TerrainSet",
    # TileMap
    "TileMapLayer",
    "CellData",
]
