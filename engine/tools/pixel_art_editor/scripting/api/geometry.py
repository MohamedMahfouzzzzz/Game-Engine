# /**************************************************************************/
# /*  api/geometry.py                                                       */
# /**************************************************************************/

"""Geometry classes for Aseprite API."""

from __future__ import annotations
from typing import Union

import logging


logger = logging.getLogger(__name__)



class Rectangle:
    """Aseprite Rectangle class."""
    
    def __init__(self, *args, **kwargs):
        # Handle different constructor forms:
        # Rectangle() - default
        # Rectangle(1, 2, 3, 4) - x, y, w, h
        # Rectangle(other_rect) - copy
        # Rectangle{x=1, y=2, width=3, height=4} - table
        # Rectangle(Point, Size) - point + size
        
        if len(args) == 1 and isinstance(args[0], Rectangle):
            # Copy constructor: Rectangle(other_rect)
            other = args[0]
            self.x = other.x
            self.y = other.y
            self.width = other.width
            self.height = other.height
        elif len(args) == 2 and hasattr(args[0], 'x') and hasattr(args[1], 'width'):
            # Point + Size constructor: Rectangle(Point(1,2), Size(3,4))
            self.x = args[0].x
            self.y = args[0].y
            self.width = args[1].width
            self.height = args[1].height
        elif len(args) == 4:
            # Rectangle(1, 2, 3, 4)
            self.x, self.y, self.width, self.height = args
        elif len(args) == 0:
            # Check for kwargs or table-style constructor
            if kwargs:
                self.x = kwargs.get('x', 0)
                self.y = kwargs.get('y', 0)
                self.width = kwargs.get('width', kwargs.get('w', 0))
                self.height = kwargs.get('height', kwargs.get('h', 0))
            else:
                self.x = self.y = self.width = self.height = 0
        else:
            self.x = self.y = self.width = self.height = 0
    
    @property
    def w(self) -> int:
        """Short form of width."""
        return self.width
    
    @w.setter
    def w(self, value: int) -> None:
        self.width = value
    
    @property
    def h(self) -> int:
        """Short form of height."""
        return self.height
    
    @h.setter
    def h(self, value: int) -> None:
        self.height = value
    
    @property
    def isEmpty(self) -> bool:
        """Check if rectangle has zero area."""
        return self.width == 0 or self.height == 0
    
    @property
    def origin(self) -> "Point":
        """Get origin as Point."""
        return Point(self.x, self.y)
    
    @origin.setter
    def origin(self, value: "Point") -> None:
        self.x = value.x
        self.y = value.y
    
    @property
    def size(self) -> "Size":
        """Get size as Size."""
        return Size(self.width, self.height)
    
    @size.setter
    def size(self, value: "Size") -> None:
        self.width = value.width
        self.height = value.height
    
    def contains(self, other: "Rectangle") -> bool:
        """Check if this rectangle contains another."""
        return (self.x <= other.x and 
                self.y <= other.y and
                self.x + self.width >= other.x + other.width and
                self.y + self.height >= other.y + other.height)
    
    def intersects(self, other: "Rectangle") -> bool:
        """Check if this rectangle intersects another."""
        return not (self.x + self.width <= other.x or
                   other.x + other.width <= self.x or
                   self.y + self.height <= other.y or
                   other.y + other.height <= self.y)
    
    def intersect(self, other: "Rectangle") -> "Rectangle":
        """Return intersection of two rectangles."""
        x1 = max(self.x, other.x)
        y1 = max(self.y, other.y)
        x2 = min(self.x + self.width, other.x + other.width)
        y2 = min(self.y + self.height, other.y + other.height)
        if x2 > x1 and y2 > y1:
            return Rectangle(x1, y1, x2 - x1, y2 - y1)
        return Rectangle()
    
    def union(self, other: "Rectangle") -> "Rectangle":
        """Return union of two rectangles."""
        x1 = min(self.x, other.x)
        y1 = min(self.y, other.y)
        x2 = max(self.x + self.width, other.x + other.width)
        y2 = max(self.y + self.height, other.y + other.height)
        return Rectangle(x1, y1, x2 - x1, y2 - y1)
    
    def __and__(self, other: "Rectangle") -> "Rectangle":
        """& operator for intersection."""
        return self.intersect(other)
    
    def __or__(self, other: "Rectangle") -> "Rectangle":
        """| operator for union."""
        return self.union(other)
    
    def __len__(self) -> int:
        return 4
    
    def __getitem__(self, index):
        if isinstance(index, int):
            return [self.x, self.y, self.width, self.height][index]
        elif isinstance(index, str):
            return getattr(self, index, None)
        return None
    
    def __setitem__(self, index, value):
        if isinstance(index, str):
            setattr(self, index, value)
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Rectangle):
            return False
        return (self.x == other.x and self.y == other.y and
                self.width == other.width and self.height == other.height)
    
    def __ne__(self, other) -> bool:
        return not self.__eq__(other)
    
    def __str__(self) -> str:
        return f"Rectangle{{ x={self.x}, y={self.y}, width={self.width}, height={self.height} }}"


class Size:
    """Aseprite Size class."""
    
    def __init__(self, width: int = 0, height: int = 0):
        self.width = width
        self.height = height
    
    def __len__(self) -> int:
        return 2
    
    def __getitem__(self, index):
        if isinstance(index, int):
            return [self.width, self.height][index]
        elif isinstance(index, str):
            return getattr(self, index, None)
        return None
    
    def __setitem__(self, index, value):
        if isinstance(index, str):
            setattr(self, index, value)
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Size):
            return False
        return self.width == other.width and self.height == other.height


class Point:
    """Aseprite Point class."""
    
    def __init__(self, x: int = 0, y: int = 0):
        self.x = x
        self.y = y
    
    def __len__(self) -> int:
        return 2
    
    def __getitem__(self, index):
        if isinstance(index, int):
            return [self.x, self.y][index]
        elif isinstance(index, str):
            return getattr(self, index, None)
        return None
    
    def __setitem__(self, index, value):
        if isinstance(index, str):
            setattr(self, index, value)
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Point):
            return False
        return self.x == other.x and self.y == other.y
