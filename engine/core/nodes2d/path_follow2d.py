# /**************************************************************************/
# /*  path_follow2d.py                                                      */
# /**************************************************************************/

"""PathFollow2D - Follows a 2D path curve."""

from __future__ import annotations
from typing import Optional
from .node2d import Node2D
from engine.core.types import NodeType

import logging


logger = logging.getLogger(__name__)



class Curve2D:
    """2D curve resource."""
    
    def get_point_count(self) -> int:
        return 0
    
    def interpolate_baked(self, offset: float) -> tuple:
        return (0.0, 0.0)
    
    def get_baked_length(self) -> float:
        return 0.0


class PathFollow2D(Node2D):
    """Follows a parent Path2D curve.
    
    Properties:
        progress: float - Distance along path
        progress_ratio: float - 0.0-1.0 along path
        h_offset: float - Horizontal offset from path
        v_offset: float - Vertical offset from path
        rotates: bool - Rotate with path tangent
        cubic_interp: bool - Use cubic interpolation
        loop: bool - Loop at ends
        lookahead: float - Distance to look ahead for rotation
    """
    
    __slots__ = [
        "progress",
        "progress_ratio",
        "h_offset",
        "v_offset",
        "rotates",
        "cubic_interp",
        "loop",
        "lookahead"
    ]
    
    def __init__(self, name: str = "PathFollow2D"):
        super().__init__(name)
        self.node_type = NodeType.PATH_FOLLOW2D
        
        self.progress: float = 0.0
        self.progress_ratio: float = 0.0
        self.h_offset: float = 0.0
        self.v_offset: float = 0.0
        self.rotates: bool = True
        self.cubic_interp: bool = True
        self.loop: bool = False
        self.lookahead: float = 4.0
    
    def set_progress(self, progress: float) -> None:
        """Set distance along path."""
        self.progress = max(0.0, progress)
        self._update_transform()
    
    def set_progress_ratio(self, ratio: float) -> None:
        """Set 0.0-1.0 progress."""
        self.progress_ratio = max(0.0, min(1.0, ratio))
        # Would calculate actual progress from curve length
        self._update_transform()
    
    def _update_transform(self) -> None:
        """Update position from path."""
        # Would get curve from parent Path2D and position accordingly
        pass


__all__ = ["PathFollow2D", "Curve2D"]
