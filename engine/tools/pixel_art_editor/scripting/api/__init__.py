# /**************************************************************************/
# /*  api/__init__.py                                                       */
# /**************************************************************************/

"""Aseprite-compatible Lua API - Modular Package.

This package provides an Aseprite-compatible API for running
Aseprite Lua scripts and tests within the engine's pixel art editor.
"""

from .color import Color, ColorMode, Palette, BlendMode
from .geometry import Rectangle, Point, Size
from .image import Image, ImageSpec, ColorSpace
from .sprite import Sprite, Layer, Frame, Cel
from .app import App, CommandAPI, FileSystem, Clipboard
from .utils import (
    Version, Uuid, Brush, BrushType, 
    Selection, Tag, Slice, Tileset, 
    Site, PixelColor
)
from .lua_wrapper import LuaListWrapper, AsepriteAPI, run_lua_test

import logging


logger = logging.getLogger(__name__)


__all__ = [
    # Color
    "Color",
    "ColorMode",
    "Palette",
    "BlendMode",
    # Geometry
    "Rectangle",
    "Point",
    "Size",
    # Image
    "Image",
    "ImageSpec",
    "ColorSpace",
    # Sprite
    "Sprite",
    "Layer",
    "Frame",
    "Cel",
    # App
    "App",
    "CommandAPI",
    "FileSystem",
    "Clipboard",
    # Utils
    "Version",
    "Uuid",
    "Brush",
    "BrushType",
    "Selection",
    "Tag",
    "Slice",
    "Tileset",
    "Site",
    "PixelColor",
    # Lua
    "LuaListWrapper",
    "AsepriteAPI",
    "run_lua_test",
]
