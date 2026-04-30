# /**************************************************************************/
# /*  frame.py                                                              */
# /**************************************************************************/

"""Animation frame metadata.

Equivalent to Aseprite's Frame concept.
"""

from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Frame:
    """A single frame of animation.
    
    Contains timing information and frame-specific data.
    """
    
    index: int
    duration_ms: int = 100  # Frame duration in milliseconds
    
    def __post_init__(self):
        # Ensure non-negative
        if self.duration_ms < 1:
            self.duration_ms = 1
    
    @property
    def duration_seconds(self) -> float:
        """Get duration in seconds."""
        return self.duration_ms / 1000.0
    
    @duration_seconds.setter
    def duration_seconds(self, seconds: float) -> None:
        """Set duration in seconds."""
        self.duration_ms = max(1, int(seconds * 1000))
    
    @property
    def fps(self) -> float:
        """Calculate FPS from duration."""
        if self.duration_ms <= 0:
            return 0.0
        return 1000.0 / self.duration_ms
    
    @fps.setter
    def fps(self, value: float) -> None:
        """Set FPS (updates duration)."""
        if value > 0:
            self.duration_ms = int(1000.0 / value)
    
    def copy(self) -> 'Frame':
        """Create a copy of this frame."""
        return Frame(self.index, self.duration_ms)
    
    @staticmethod
    def calculate_duration_from_fps(fps: float) -> int:
        """Calculate frame duration from FPS."""
        if fps <= 0:
            return 100
        return int(1000.0 / fps)
    
    @staticmethod
    def default_frame(index: int = 0) -> 'Frame':
        """Create a default frame (100ms)."""
        return Frame(index, 100)


class FrameSequence:
    """Sequence of frames for animation."""
    
    def __init__(self):
        self._frames: List[Frame] = []
    
    def add_frame(self, frame: Frame) -> None:
        """Add frame to sequence."""
        self._frames.append(frame)
        # Reindex
        for i, f in enumerate(self._frames):
            f.index = i
    
    def remove_frame(self, index: int) -> Optional[Frame]:
        """Remove frame at index."""
        if 0 <= index < len(self._frames):
            frame = self._frames.pop(index)
            # Reindex
            for i, f in enumerate(self._frames):
                f.index = i
            return frame
        return None
    
    def insert_frame(self, index: int, frame: Frame) -> None:
        """Insert frame at index."""
        self._frames.insert(index, frame)
        # Reindex
        for i, f in enumerate(self._frames):
            f.index = i
    
    def get_frame(self, index: int) -> Optional[Frame]:
        """Get frame at index."""
        if 0 <= index < len(self._frames):
            return self._frames[index]
        return None
    
    @property
    def count(self) -> int:
        """Get frame count."""
        return len(self._frames)
    
    @property
    def total_duration_ms(self) -> int:
        """Get total animation duration."""
        return sum(f.duration_ms for f in self._frames)
    
    @property
    def average_fps(self) -> float:
        """Get average FPS."""
        if not self._frames:
            return 0.0
        return len(self._frames) / (self.total_duration_ms / 1000.0)
    
    def set_all_duration(self, duration_ms: int) -> None:
        """Set all frames to same duration."""
        for frame in self._frames:
            frame.duration_ms = duration_ms
    
    def set_all_fps(self, fps: float) -> None:
        """Set all frames to same FPS."""
        duration = Frame.calculate_duration_from_fps(fps)
        self.set_all_duration(duration)
    
    def copy(self) -> 'FrameSequence':
        """Create a copy of this sequence."""
        new_seq = FrameSequence()
        for frame in self._frames:
            new_seq.add_frame(frame.copy())
        return new_seq
