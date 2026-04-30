# /**************************************************************************/
# /*  scripting/__init__.py                                                 */
# /**************************************************************************/

"""Scripting support for pixel art editor."""

import logging

logger = logging.getLogger(__name__)

# Import from the new modular api package
from .api import (
    AsepriteAPI,
    run_lua_test,
    # Core classes
    Color,
    ColorMode,
    Palette,
    BlendMode,
    Rectangle,
    Point,
    Size,
    Image,
    ImageSpec,
    ColorSpace,
    Sprite,
    Layer,
    Frame,
    Cel,
    App,
    CommandAPI,
    FileSystem,
    Clipboard,
    Version,
    Uuid,
    Brush,
    BrushType,
    Selection,
    Tag,
    Slice,
    Tileset,
    Site,
    PixelColor,
    LuaListWrapper,
)

__all__ = [
    "AsepriteAPI",
    "run_lua_test",
    # Core classes
    "Color",
    "ColorMode",
    "Palette",
    "BlendMode",
    "Rectangle",
    "Point",
    "Size",
    "Image",
    "ImageSpec",
    "ColorSpace",
    "Sprite",
    "Layer",
    "Frame",
    "Cel",
    "App",
    "CommandAPI",
    "FileSystem",
    "Clipboard",
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
    "LuaListWrapper",
]
