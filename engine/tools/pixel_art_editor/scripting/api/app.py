# /**************************************************************************/
# /*  api/app.py                                                            */
# /**************************************************************************/

"""App and system classes for Aseprite API."""

from __future__ import annotations

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path

import logging


if TYPE_CHECKING:
    from .sprite import Sprite, Layer, Frame
    from .image import Image
    from .utils import Site, Version, PixelColor


logger = logging.getLogger(__name__)

class Clipboard:
    """Aseprite clipboard API."""
    
    def __init__(self):
        self.image = None
    
    def clear(self) -> None:
        """Clear the clipboard."""
        self.image = None
    
    def setImage(self, image: "Image") -> None:
        """Set clipboard image."""
        self.image = image
    
    def getImage(self) -> Optional["Image"]:
        """Get clipboard image."""
        return self.image


class CommandAPI:
    """Aseprite command API."""
    
    def __init__(self):
        self._commands: Dict[str, Any] = {}
    
    def __getattr__(self, name: str):
        """Allow app.command.CommandName() syntax."""
        def method(*args, **kwargs):
            # Stub command execution
            return True
        return method
    
    def __getitem__(self, name: str):
        """Allow app.command['CommandName']() syntax."""
        def method(*args, **kwargs):
            return True
        return method


class FileSystem:
    """Aseprite file system API."""
    
    def __init__(self):
        self.pathSeparator = "/"
        self._fileList: List[str] = []
    
    def fileList(self, path: str) -> List[str]:
        """List files in directory."""
        import os
        try:
            return os.listdir(path)
        except:
            return []
    
    def isDirectory(self, path: str) -> bool:
        """Check if path is directory."""
        import os
        return os.path.isdir(path)
    
    def isFile(self, path: str) -> bool:
        """Check if path is file."""
        import os
        return os.path.isfile(path)


class App:
    """Aseprite app API."""
    
    def __init__(self):
        from .utils import PixelColor, Site, Version, Clipboard
        from .image import Image
        from .sprite import Sprite, Layer, Frame
        
        self.sprite: Optional["Sprite"] = None
        self.layer: Optional["Layer"] = None
        self.frame: Optional["Frame"] = None
        self.pixelColor = PixelColor()
        self.activeBrush = None  # Will be set by Brush import
        self.activeSprite: Optional["Sprite"] = None
        self.activeImage: Optional["Image"] = None
        self.activeLayer: Optional["Layer"] = None
        self.activeFrame: Optional["Frame"] = None
        self.site = Site()
        self.preferences: Dict[str, Any] = {}
        self._clipboards: List["Image"] = []
        self.fs = FileSystem()
        self.command = CommandAPI()
        self.activeTool = "pencil"
        self._version = Version("1.3.0")
        self.clipboard = Clipboard()
        self.params: Dict[str, Any] = {}
        self.isUIAvailable = False
        self.events: Dict[str, Any] = {}
        self.tool = "pencil"
        self.experimental: Dict[str, Any] = {}
        self.undoHistory: List[Any] = []
        self.transaction = False
    
    def Sprite(self, width: int = 0, height: int = 0, color_mode: int = 0) -> "Sprite":
        """Create a new sprite."""
        from .sprite import Sprite
        from .color import ColorMode
        # Handle case where only one arg is passed (square sprite)
        if height == 0 and width != 0:
            height = width
        sprite = Sprite(width, height, ColorMode(color_mode))
        self.sprite = sprite
        self.activeSprite = sprite
        self.layer = sprite.layers[0] if sprite.layers else None
        self.frame = sprite.frames[0] if sprite.frames else None
        self.activeLayer = self.layer
        self.activeFrame = self.frame
        self.site.sprite = sprite
        self.site.layer = self.layer
        self.site.frame = self.frame
        return sprite
    
    def Image(self, width: int, height: int) -> "Image":
        """Create a new image."""
        from .image import Image
        from .color import ColorMode
        return Image(width, height, ColorMode.RGB)
    
    def Brush(self):
        """Create a new brush."""
        from .utils import Brush
        return Brush()
    
    def isTileModeEnabled(self) -> bool:
        """Check if tile mode is enabled."""
        return False
    
    def useTool(self, tool: str) -> None:
        """Set active tool."""
        self.activeTool = tool
        self.tool = tool
    
    def undo(self) -> None:
        """Undo last action."""
        pass
    
    def redo(self) -> None:
        """Redo last undone action."""
        pass
    
    def open(self, filename: str):
        """Open a sprite file."""
        from .sprite import Sprite
        # Stub - would load from file
        return Sprite(32, 32)
    
    def exit(self) -> None:
        """Exit the application."""
        pass
    
    @property
    def version(self) -> "Version":
        """Get app version."""
        return self._version
    
    @version.setter
    def version(self, value):
        self._version = value
