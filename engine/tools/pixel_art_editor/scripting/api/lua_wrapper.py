# /**************************************************************************/
# /*  api/lua_wrapper.py                                                    */
# /**************************************************************************/

"""Lua integration and wrapper classes for Aseprite API."""

from __future__ import annotations

import sys
import io
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import logging


try:
    import lupa
    from lupa import LuaRuntime
    LUPA_AVAILABLE = True
except ImportError:
    LUPA_AVAILABLE = False


logger = logging.getLogger(__name__)

def as_lua_table(items: List[Any], lua_runtime):
    """Convert Python list to Lua table that supports # operator."""
    # Create a Lua table with items at 1-based indices
    table = lua_runtime.table_from({i+1: item for i, item in enumerate(items)})
    return table


class LuaListWrapper:
    """Wrapper to make Python lists work with Lua # operator and indexing."""
    
    def __init__(self, items: List[Any], name_attr: str = "name"):
        self._items = items
        self._name_attr = name_attr  # Attribute to use for string lookup
    
    def __len__(self) -> int:
        return len(self._items)
    
    def len(self) -> int:
        """Explicit length method for Lua compatibility."""
        return len(self._items)
    
    def __getitem__(self, index) -> Any:
        # String indexing: s.layers["Layer 1"]
        if isinstance(index, str):
            for item in self._items:
                if hasattr(item, self._name_attr) and getattr(item, self._name_attr) == index:
                    return item
            return None
        
        # Lua uses 1-based indexing
        if isinstance(index, int):
            if index >= 1:
                index -= 1
            if 0 <= index < len(self._items):
                return self._items[index]
        return None
    
    def get(self, index: int) -> Any:
        """Get item at 1-based index for Lua."""
        if index >= 1:
            index -= 1
        if 0 <= index < len(self._items):
            return self._items[index]
        return None
    
    def __setitem__(self, index, value: Any) -> None:
        if isinstance(index, int):
            if index >= 1:
                index -= 1
            if 0 <= index < len(self._items):
                self._items[index] = value
    
    def append(self, item: Any) -> None:
        self._items.append(item)
    
    def remove(self, item: Any) -> None:
        if item in self._items:
            self._items.remove(item)
    
    def index(self, item: Any) -> int:
        try:
            return self._items.index(item) + 1  # 1-based
        except ValueError:
            return -1
    
    def __iter__(self):
        return iter(self._items)
    
    def as_table(self, lua_runtime):
        """Return as actual Lua table."""
        return as_lua_table(self._items, lua_runtime)


class JsonModule:
    """JSON module for Lua."""
    
    @staticmethod
    def decode(s: str) -> Any:
        return json.loads(s)
    
    @staticmethod
    def encode(obj: Any) -> str:
        return json.dumps(obj)


class AsepriteAPI:
    """Main Aseprite API class for Lua integration."""
    
    def __init__(self):
        if not LUPA_AVAILABLE:
            raise RuntimeError("lupa is required for Lua scripting")
        
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.app = self._create_app()
        self._setup_lua_globals()
    
    def _create_app(self):
        """Create the app instance."""
        from .app import App
        return App()
    
    def _setup_lua_globals(self):
        """Setup Lua global environment."""
        from .color import Color, ColorMode, Palette, BlendMode
        from .geometry import Rectangle, Point, Size
        from .image import Image, ImageSpec, ColorSpace, Cel
        from .sprite import Sprite, Layer, Frame
        from .utils import (
            Version, Uuid, Brush, BrushType,
            Selection, Tag, Slice, Tileset,
            Site, PixelColor
        )
        
        lua = self.lua
        
        # Expose ColorMode as enum
        lua.globals().ColorMode = ColorMode
        
        # Expose BlendMode
        lua.globals().BlendMode = BlendMode
        
        # Expose BrushType
        lua.globals().BrushType = BrushType
        
        # Expose classes as constructors
        def make_color(*args, **kwargs):
            if len(args) == 1 and isinstance(args[0], dict):
                d = args[0]
                return Color(d.get('r', 0), d.get('g', 0), d.get('b', 0), d.get('a', 255))
            return Color(*args, **kwargs)
        
        lua.globals().Color = make_color
        
        def make_palette(*args, **kwargs):
            if len(args) == 1 and isinstance(args[0], int):
                p = Palette()
                p.resize(args[0])
                return p
            return Palette(*args, **kwargs)
        
        lua.globals().Palette = make_palette
        
        def make_rect(*args, **kwargs):
            if len(args) == 1 and isinstance(args[0], dict):
                d = args[0]
                # Handle both array-style {1,2,3,4} and dict-style {x=1,y=2,...}
                keys = list(d.keys())
                if keys == [1, 2, 3, 4] or (len(keys) == 4 and all(isinstance(k, int) for k in keys)):
                    # Array style: Rectangle{6, 7, 8, 9}
                    return Rectangle(d.get(1, 0), d.get(2, 0), d.get(3, 0), d.get(4, 0))
                else:
                    # Dict style: Rectangle{x=1, y=2, width=3, height=4}
                    return Rectangle(d.get('x', 0), d.get('y', 0), d.get('width', d.get('w', 0)), d.get('height', d.get('h', 0)))
            return Rectangle(*args, **kwargs)
        
        lua.globals().Rectangle = make_rect
        
        def make_size(*args, **kwargs):
            if len(args) == 1 and isinstance(args[0], dict):
                d = args[0]
                keys = list(d.keys())
                if keys == [1, 2] or (len(keys) == 2 and all(isinstance(k, int) for k in keys)):
                    # Array style: Size{32, 64}
                    return Size(d.get(1, 0), d.get(2, 0))
                else:
                    # Dict style: Size{width=32, height=64}
                    return Size(d.get('width', 0), d.get('height', 0))
            return Size(*args, **kwargs)
        
        lua.globals().Size = make_size
        
        def make_point(*args, **kwargs):
            if len(args) == 1 and isinstance(args[0], dict):
                d = args[0]
                keys = list(d.keys())
                if keys == [1, 2] or (len(keys) == 2 and all(isinstance(k, int) for k in keys)):
                    # Array style: Point{10, 20}
                    return Point(d.get(1, 0), d.get(2, 0))
                else:
                    # Dict style: Point{x=10, y=20}
                    return Point(d.get('x', 0), d.get('y', 0))
            return Point(*args, **kwargs)
        
        lua.globals().Point = make_point
        
        def make_uuid(value=""):
            return Uuid(value)
        
        lua.globals().Uuid = make_uuid
        
        def make_version(version_str="1.0"):
            return Version(version_str)
        
        lua.globals().Version = make_version
        
        def make_brush():
            return Brush()
        
        lua.globals().Brush = make_brush
        
        def make_selection():
            return Selection()
        
        lua.globals().Selection = make_selection
        
        def make_tag(name="", from_frame=1, to_frame=1):
            return Tag(name, from_frame, to_frame)
        
        lua.globals().Tag = make_tag
        
        def make_slice(name=""):
            return Slice(name)
        
        lua.globals().Slice = make_slice
        
        def make_tileset(name=""):
            return Tileset(name)
        
        lua.globals().Tileset = make_tileset
        
        def make_image_spec(**kwargs):
            return ImageSpec(**kwargs)
        
        lua.globals().ImageSpec = make_image_spec
        
        def make_color_space(name="sRGB"):
            return ColorSpace(name)
        
        lua.globals().ColorSpace = make_color_space
        lua.globals().ColorSpace.sRGB = ColorSpace.sRGB
        
        # Expose classes as constructors using proper functions
        def make_sprite(w=0, h=0, cm=0):
            return self.app.Sprite(w, h, cm)
        
        lua.globals().Sprite = make_sprite
        
        def make_layer(name=""):
            return Layer(name, self.app.sprite)
        
        lua.globals().Layer = make_layer
        
        def make_frame(num=1):
            return Frame(num, self.app.sprite)
        
        lua.globals().Frame = make_frame
        
        # Add app global
        lua.globals().app = self.app
        
        # Add version info
        self.app.version = Version("1.3.0")
        lua.globals().Version = make_version
        lua.globals()._G = lua.globals()
        
        # Add ImageSpec and ColorSpace
        lua.globals().ImageSpec = lambda **kwargs: ImageSpec(**kwargs)
        lua.globals().ColorSpace = lambda name="sRGB": ColorSpace(name)
        lua.globals().ColorSpace.sRGB = ColorSpace.sRGB
        
        # Add json module
        lua.globals().json = JsonModule()
        
        # Add missing constants
        lua.globals().GRAY = ColorMode.GRAYSCALE
        lua.globals().RGB = ColorMode.RGB
        lua.globals().INDEXED = ColorMode.INDEXED
        
        # Add __len metamethod support for Python objects
        lua.execute('''
            -- Helper function to safely get length of any object
            function __len(obj)
                if type(obj) == "table" then
                    return #obj
                end
                -- For Python objects, try various methods
                if obj then
                    local mt = getmetatable(obj)
                    if mt and mt.__len then
                        return mt.__len(obj)
                    end
                    -- Try __len method
                    local ok, len = pcall(function() return obj:__len() end)
                    if ok and type(len) == "number" then
                        return len
                    end
                end
                return 0
            end
        ''')
    
    def run_script(self, script: str) -> Dict[str, Any]:
        """Run a Lua script string."""
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        
        try:
            result = self.lua.execute(script)
            output = sys.stdout.getvalue()
            return {
                "success": True,
                "result": result,
                "output": output
            }
        except Exception as e:
            output = sys.stdout.getvalue()
            return {
                "success": False,
                "error": str(e),
                "output": output
            }
        finally:
            sys.stdout = old_stdout
    
    def run_script_file(self, path: Path) -> Dict[str, Any]:
        """Run a Lua script from file."""
        script = path.read_text(encoding="utf-8")
        return self.run_script(script)


def run_lua_test(script_path: Path) -> Dict[str, Any]:
    """Run a single Lua test file."""
    api = AsepriteAPI()
    return api.run_script_file(script_path)
