# /**************************************************************************/
# /*  slice.py                                                              */
# /**************************************************************************/

"""Sprite slices for 9-patch scaling and regions.

Equivalent to Aseprite's doc::Slice class.
"""

from typing import List, Optional, Tuple, Dict
from dataclasses import dataclass, field
from enum import Enum, auto


class SlicePivot(Enum):
    """Pivot point for slice."""
    TOP_LEFT = auto()
    TOP_CENTER = auto()
    TOP_RIGHT = auto()
    CENTER_LEFT = auto()
    CENTER = auto()
    CENTER_RIGHT = auto()
    BOTTOM_LEFT = auto()
    BOTTOM_CENTER = auto()
    BOTTOM_RIGHT = auto()


@dataclass
class SliceKey:
    """A slice key defines the slice bounds at a specific frame."""
    frame: int
    x: int
    y: int
    width: int
    height: int
    center_x: Optional[int] = None  # 9-patch center
    center_y: Optional[int] = None
    center_width: Optional[int] = None
    center_height: Optional[int] = None
    pivot_x: Optional[int] = None
    pivot_y: Optional[int] = None


class Slice:
    """A slice defines a rectangular region in the sprite.
    
    Slices can be animated (different bounds per frame) and
    support 9-patch scaling with center region.
    """
    
    def __init__(self, name: str = "Slice"):
        self.name = name
        self._keys: Dict[int, SliceKey] = {}
        self.pivot = SlicePivot.CENTER
        self.data = ""  # User data string
    
    def add_key(self, key: SliceKey) -> None:
        """Add or replace a slice key."""
        self._keys[key.frame] = key
    
    def get_key(self, frame: int) -> Optional[SliceKey]:
        """Get slice key at frame."""
        # Return exact match or previous frame's key
        if frame in self._keys:
            return self._keys[frame]
        
        # Find most recent key before this frame
        prev_frames = [f for f in self._keys.keys() if f < frame]
        if prev_frames:
            return self._keys[max(prev_frames)]
        
        return None
    
    def remove_key(self, frame: int) -> None:
        """Remove slice key at frame."""
        if frame in self._keys:
            del self._keys[frame]
    
    def get_bounds(self, frame: int = 0) -> Optional[Tuple[int, int, int, int]]:
        """Get slice bounds at frame."""
        key = self.get_key(frame)
        if key:
            return (key.x, key.y, key.width, key.height)
        return None
    
    def set_bounds(self, frame: int, x: int, y: int, 
                   width: int, height: int) -> None:
        """Set slice bounds at frame."""
        key = SliceKey(frame, x, y, width, height)
        self.add_key(key)
    
    @property
    def is_9patch(self) -> bool:
        """Check if slice has 9-patch center defined."""
        key = self.get_key(0)
        if key:
            return (key.center_x is not None and 
                    key.center_width is not None)
        return False
    
    def set_center(self, frame: int, x: int, y: int, 
                   width: int, height: int) -> None:
        """Set 9-patch center region."""
        key = self.get_key(frame)
        if not key:
            # Create default key
            key = SliceKey(frame, 0, 0, 100, 100)
        
        key.center_x = x
        key.center_y = y
        key.center_width = width
        key.center_height = height
        self.add_key(key)
    
    def get_center(self, frame: int = 0) -> Optional[Tuple[int, int, int, int]]:
        """Get 9-patch center bounds."""
        key = self.get_key(frame)
        if key and key.center_x is not None:
            return (key.center_x, key.center_y, 
                    key.center_width, key.center_height)
        return None
    
    def get_patch_regions(self, frame: int = 0) -> Optional[List[Tuple[int, int, int, int]]]:
        """Get 9-patch regions (9 regions for scaling).
        
        Returns: [top-left, top, top-right,
                  left, center, right,
                  bottom-left, bottom, bottom-right]
        """
        bounds = self.get_bounds(frame)
        center = self.get_center(frame)
        
        if not bounds or not center:
            return None
        
        x, y, w, h = bounds
        cx, cy, cw, ch = center
        
        # Calculate patch regions
        left_width = cx - x
        right_width = (x + w) - (cx + cw)
        top_height = cy - y
        bottom_height = (y + h) - (cy + ch)
        
        return [
            # Top row
            (x, y, left_width, top_height),           # top-left
            (cx, y, cw, top_height),                  # top
            (cx + cw, y, right_width, top_height),    # top-right
            # Middle row
            (x, cy, left_width, ch),                  # left
            (cx, cy, cw, ch),                         # center
            (cx + cw, cy, right_width, ch),           # right
            # Bottom row
            (x, cy + ch, left_width, bottom_height),  # bottom-left
            (cx, cy + ch, cw, bottom_height),         # bottom
            (cx + cw, cy + ch, right_width, bottom_height),  # bottom-right
        ]
    
    def copy(self) -> 'Slice':
        """Create a copy of this slice."""
        new_slice = Slice(f"{self.name} copy")
        new_slice.pivot = self.pivot
        new_slice.data = self.data
        for key in self._keys.values():
            new_slice.add_key(SliceKey(
                key.frame, key.x, key.y, key.width, key.height,
                key.center_x, key.center_y, 
                key.center_width, key.center_height,
                key.pivot_x, key.pivot_y
            ))
        return new_slice
