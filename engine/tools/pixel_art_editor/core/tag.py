# /**************************************************************************/
# /*  tag.py                                                                */
# /**************************************************************************/

"""Frame tags for animation (e.g., "walk", "run", "idle").

Equivalent to Aseprite's doc::Tag class.
"""

from typing import Optional, Tuple
from enum import IntEnum
from dataclasses import dataclass


class TagRepeat(IntEnum):
    """Tag repeat mode."""
    NO_REPEAT = 0
    FORWARD = 1
    REVERSE = 2
    PING_PONG = 3


@dataclass
class Tag:
    """A frame tag marking a range of frames.
    
    Used for animation loops and organization.
    Example: Tag "walk" from frame 0 to 7.
    """
    
    name: str
    from_frame: int
    to_frame: int
    color: Tuple[int, int, int] = (128, 128, 128)  # RGB
    repeat: TagRepeat = TagRepeat.NO_REPEAT
    ani_dir: int = 0  # Animation direction (0=forward, 1=reverse, 2=ping-pong)
    
    def __post_init__(self):
        # Ensure from <= to
        if self.from_frame > self.to_frame:
            self.from_frame, self.to_frame = self.to_frame, self.from_frame
    
    @property
    def frame_count(self) -> int:
        """Get number of frames in this tag."""
        return self.to_frame - self.from_frame + 1
    
    def contains(self, frame: int) -> bool:
        """Check if frame is within this tag's range."""
        return self.from_frame <= frame <= self.to_frame
    
    def overlaps(self, other: 'Tag') -> bool:
        """Check if this tag overlaps with another."""
        return (self.from_frame <= other.to_frame and 
                other.from_frame <= self.to_frame)
    
    def move(self, offset: int) -> None:
        """Move tag by offset frames."""
        self.from_frame += offset
        self.to_frame += offset
        
        # Ensure non-negative
        if self.from_frame < 0:
            diff = -self.from_frame
            self.from_frame = 0
            self.to_frame += diff
    
    def extend(self, new_to_frame: int) -> None:
        """Extend tag to new frame."""
        if new_to_frame >= self.from_frame:
            self.to_frame = new_to_frame
    
    def copy(self) -> 'Tag':
        """Create a copy of this tag."""
        return Tag(
            self.name,
            self.from_frame,
            self.to_frame,
            self.color,
            self.repeat,
            self.ani_dir
        )
    
    @classmethod
    def create_loop(cls, name: str, start: int, length: int, 
                    color: Tuple[int, int, int] = (128, 128, 128)) -> 'Tag':
        """Create a looping animation tag."""
        return cls(name, start, start + length - 1, color, TagRepeat.FORWARD)
