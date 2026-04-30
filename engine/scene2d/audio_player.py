# /**************************************************************************/
# /*  audio_player.py                                                       */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""2D positional audio playback."""

from typing import Optional
from engine.core.nodes2d import Node2D, Vector2


class AudioStream:
    """Audio stream resource base class."""
    pass


class AudioStreamPlayer2D(Node2D):
    """2D positional audio player.
    
    Sound volume changes based on distance to listener.
    """
    
    def __init__(self, name: str = "AudioStreamPlayer2D"):
        super().__init__(name)
        self._stream: Optional[AudioStream] = None
        self._volume_db: float = 0.0
        self._pitch_scale: float = 1.0
        self._playing: bool = False
        self._autoplay: bool = False
        self._stream_paused: bool = False
        self._max_distance: float = 2000.0
        self._attenuation: float = 1.0
        self._panning_strength: float = 1.0
        self._area_mask: int = 1
        self._playback_type: int = 0
        self._playback_position: float = 0.0
    
    def set_stream(self, stream: Optional[AudioStream]) -> None:
        """Set the audio stream to play."""
        self._stream = stream
    
    def get_stream(self) -> Optional[AudioStream]:
        return self._stream
    
    def set_volume_db(self, volume_db: float) -> None:
        """Set volume in decibels (0 = normal, -80 = silent)."""
        self._volume_db = volume_db
    
    def get_volume_db(self) -> float:
        return self._volume_db
    
    def set_pitch_scale(self, pitch_scale: float) -> None:
        """Playback speed/pitch (1.0 = normal)."""
        self._pitch_scale = max(0.001, pitch_scale)
    
    def get_pitch_scale(self) -> float:
        return self._pitch_scale
    
    def play(self, from_position: float = 0.0) -> None:
        """Start playback."""
        self._playing = True
        self._stream_paused = False
        self._playback_position = from_position
    
    def stop(self) -> None:
        """Stop playback."""
        self._playing = False
        self._playback_position = 0.0
    
    def pause(self) -> None:
        """Pause playback."""
        self._stream_paused = True
    
    def unpause(self) -> None:
        """Unpause playback."""
        self._stream_paused = False
    
    def is_playing(self) -> bool:
        return self._playing and not self._stream_paused
    
    def is_paused(self) -> bool:
        return self._stream_paused
    
    def set_autoplay(self, autoplay: bool) -> None:
        """Auto-play when node enters tree."""
        self._autoplay = autoplay
    
    def has_autoplay(self) -> bool:
        return self._autoplay
    
    def set_max_distance(self, distance: float) -> None:
        """Maximum distance where sound is audible."""
        self._max_distance = max(0.0, distance)
    
    def get_max_distance(self) -> float:
        return self._max_distance
    
    def set_attenuation(self, attenuation: float) -> None:
        """How quickly sound fades with distance."""
        self._attenuation = max(0.0, attenuation)
    
    def get_attenuation(self) -> float:
        return self._attenuation
    
    def set_panning_strength(self, strength: float) -> None:
        """Left/right panning intensity."""
        self._panning_strength = max(0.0, min(3.0, strength))
    
    def get_panning_strength(self) -> float:
        return self._panning_strength
    
    def get_playback_position(self) -> float:
        """Current playback position in seconds."""
        return self._playback_position
    
    def seek(self, position: float) -> None:
        """Seek to position in seconds."""
        self._playback_position = max(0.0, position)
    
    def set_area_mask(self, mask: int) -> None:
        """Which areas affect this player."""
        self._area_mask = mask
    
    def get_area_mask(self) -> int:
        return self._area_mask
    
    def __repr__(self) -> str:
        return f"AudioStreamPlayer2D('{self.name}', playing={self._playing})"
