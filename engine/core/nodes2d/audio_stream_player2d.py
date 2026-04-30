# /**************************************************************************/
# /*  audio_stream_player2d.py                                              */
# /**************************************************************************/

"""AudioStreamPlayer2D - Positional 2D audio playback."""

from __future__ import annotations
from typing import Optional
from .node2d import Node2D
from engine.core.types import NodeType

class AudioStream:
    """Audio stream resource."""
    pass


class AudioStreamPlayer2D(Node2D):
    """Positional 2D audio playback.
    
    Properties:
        stream: AudioStream - Audio resource
        volume_db: float - Volume in decibels
        pitch_scale: float - Playback speed
        playing: bool - Currently playing
        autoplay: bool - Auto-start on ready
        stream_paused: bool - Paused state
        max_distance: float - Audible distance
        attenuation: float - Distance attenuation curve
        bus: str - Audio bus name
        area_mask: int - Area detection mask
    
    Signals:
        finished - Playback complete
    """
    
    __slots__ = [
        "stream",
        "volume_db",
        "pitch_scale",
        "playing",
        "autoplay",
        "stream_paused",
        "max_distance",
        "attenuation",
        "bus",
        "area_mask"
    ]
    
    _SIGNALS = ["finished"]
    
    def __init__(self, name: str = "AudioStreamPlayer2D"):
        super().__init__(name)
        self.node_type = NodeType.AUDIO_STREAM_PLAYER2D
        
        self.stream: Optional[AudioStream] = None
        self.volume_db: float = 0.0
        self.pitch_scale: float = 1.0
        self.playing: bool = False
        self.autoplay: bool = False
        self.stream_paused: bool = False
        self.max_distance: float = 2000.0
        self.attenuation: float = 1.0
        self.bus: str = "Master"
        self.area_mask: int = 1
    
    def play(self, from_position: float = 0.0) -> None:
        """Start playback."""
        self.playing = True
        self.stream_paused = False
    
    def stop(self) -> None:
        """Stop playback."""
        self.playing = False
    
    def pause(self) -> None:
        """Pause playback."""
        self.stream_paused = True
    
    def is_playing(self) -> bool:
        """Check if playing."""
        return self.playing and not self.stream_paused
    
    def get_playback_position(self) -> float:
        """Get current playback position."""
        return 0.0
    
    def seek(self, to_position: float) -> None:
        """Seek to position."""
        pass


__all__ = ["AudioStreamPlayer2D", "AudioStream"]
