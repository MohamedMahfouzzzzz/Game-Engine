# /**************************************************************************/
# /*  api/utils.py                                                          */
# /**************************************************************************/

"""Utility classes for Aseprite API."""

from __future__ import annotations

from typing import List, Optional, Any, Dict
from enum import IntEnum

import logging


logger = logging.getLogger(__name__)



class Version:
    """Aseprite Version class."""
    
    def __init__(self, version: str):
        self._version = version
        parts = version.split(".")
        self.major = int(parts[0]) if parts else 0
        self.minor = int(parts[1]) if len(parts) > 1 else 0
        self.patch = int(parts[2]) if len(parts) > 2 else 0
    
    def __str__(self) -> str:
        return self._version
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Version):
            return False
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)
    
    def __lt__(self, other) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)
    
    def __le__(self, other) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major, self.minor, self.patch) <= (other.major, other.minor, other.patch)
    
    def __gt__(self, other) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major, self.minor, self.patch) > (other.major, other.minor, other.patch)
    
    def __ge__(self, other) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major, self.minor, self.patch) >= (other.major, other.minor, other.patch)


class Uuid:
    """Aseprite UUID class."""
    
    def __init__(self, value: str = ""):
        self.value = value or self._generate()
    
    def _generate(self) -> str:
        import uuid
        return str(uuid.uuid4())
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Uuid):
            return False
        return self.value == other.value
    
    def __ne__(self, other) -> bool:
        return not self.__eq__(other)
    
    def __len__(self) -> int:
        return len(self.value)
    
    def __getitem__(self, index):
        return self.value[index]


class BrushType(IntEnum):
    """Brush types."""
    CIRCLE = 0
    SQUARE = 1
    LINE = 2


class Brush:
    """Aseprite Brush class."""
    
    def __init__(self, type: BrushType = BrushType.CIRCLE, size: int = 1):
        self.type = type
        self.size = size
        self.color = None


class Selection:
    """Aseprite Selection class."""
    
    def __init__(self):
        from .geometry import Rectangle, Point
        self.isEmpty = True
        self.bounds = Rectangle()
        self.origin = Point()
    
    def select(self, x: int = 0, y: int = 0, width: int = 0, height: int = 0) -> None:
        """Set selection rectangle."""
        from .geometry import Rectangle, Point
        self.bounds = Rectangle(x, y, width, height)
        self.origin = Point(x, y)
        self.isEmpty = (width == 0 or height == 0)
    
    def deselect(self) -> None:
        """Clear selection."""
        from .geometry import Rectangle, Point
        self.isEmpty = True
        self.bounds = Rectangle()
        self.origin = Point()
    
    def contains(self, x: int, y: int) -> bool:
        """Check if point is in selection."""
        if self.isEmpty:
            return True
        return (self.bounds.x <= x < self.bounds.x + self.bounds.width and
                self.bounds.y <= y < self.bounds.y + self.bounds.height)


class Tag:
    """Aseprite Tag class for animation."""
    
    def __init__(self, name: str = "", from_frame: int = 1, to_frame: int = 1):
        self.name = name
        self.fromFrame = from_frame
        self.toFrame = to_frame
        self.color = None
        self.aniDir = 0  # Animation direction


class Slice:
    """Aseprite Slice class."""
    
    def __init__(self, name: str = ""):
        from .geometry import Rectangle
        self.name = name
        self.bounds = Rectangle()
        self.center = Rectangle()
        self.sprite = None


class Tileset:
    """Aseprite Tileset class."""
    
    def __init__(self, name: str = ""):
        self.name = name
        self.grid = None


class Site:
    """Aseprite Site class for current context."""
    
    def __init__(self):
        self.sprite = None
        self.layer = None
        self.frame = None
        self.frameNumber = 1
        self.layerIndex = 0


class PixelColor:
    """Pixel color utilities."""
    
    def __init__(self):
        self.rgba = 0
        self.gray = 0
        self.index = 0
