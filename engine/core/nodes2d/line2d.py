# /**************************************************************************/
# /*  line2d.py                                                             */
# /**************************************************************************/

"""Line2D - 2D polyline with variable width and textures."""

from __future__ import annotations
from typing import List, Optional, Tuple
from enum import IntEnum
from .node2d import Node2D
from .types import Vector2, Color, Texture2D
from engine.core.types import NodeType

import logging


logger = logging.getLogger(__name__)



class Line2D(Node2D):
    """2D polyline with styling.
    
    Properties:
        points: List[Vector2] - Line points
        width: float - Line width
        default_color: Color - Line color
        texture: Texture2D - Line texture
        texture_mode: int - 0=TILE, 1=STRETCH
        joint_mode: int - 0=SHARP, 1=BEVEL, 2=ROUND
        begin_cap_mode: int - 0=NONE, 1=BOX, 2=ROUND
        end_cap_mode: int - 0=NONE, 1=BOX, 2=ROUND
        sharp_limit: float - Miter limit for sharp joints
        round_precision: int - Round cap precision
    """
    
    class TextureMode(IntEnum):
        TILE = 0
        STRETCH = 1
    
    class JointMode(IntEnum):
        SHARP = 0
        BEVEL = 1
        ROUND = 2
    
    class CapMode(IntEnum):
        NONE = 0
        BOX = 1
        ROUND = 2
    
    __slots__ = [
        "points",
        "width",
        "default_color",
        "texture",
        "texture_mode",
        "joint_mode",
        "begin_cap_mode",
        "end_cap_mode",
        "sharp_limit",
        "round_precision"
    ]
    
    def __init__(self, name: str = "Line2D"):
        super().__init__(name)
        self.node_type = NodeType.LINE2D
        
        self.points: List[Vector2] = []
        self.width: float = 10.0
        self.default_color: Color = Color.white()
        self.texture: Optional[Texture2D] = None
        self.texture_mode: int = self.TextureMode.STRETCH
        self.joint_mode: int = self.JointMode.SHARP
        self.begin_cap_mode: int = self.CapMode.NONE
        self.end_cap_mode: int = self.CapMode.NONE
        self.sharp_limit: float = 2.0
        self.round_precision: int = 8
    
    def add_point(self, position: Vector2, at_position: int = -1) -> None:
        """Add point to line."""
        if at_position < 0 or at_position >= len(self.points):
            self.points.append(position)
        else:
            self.points.insert(at_position, position)
    
    def remove_point(self, i: int) -> None:
        """Remove point at index."""
        if 0 <= i < len(self.points):
            del self.points[i]
    
    def clear_points(self) -> None:
        """Remove all points."""
        self.points.clear()
    
    def get_point_count(self) -> int:
        return len(self.points)


__all__ = ["Line2D"]
