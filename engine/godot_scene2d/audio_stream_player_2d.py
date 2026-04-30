# /**************************************************************************/
# /*  audio_stream_player_2d.py                                             */
# /**************************************************************************/

"""Godot AudioStreamPlayer2D port - 2D positional audio."""

from typing import Optional, Callable, List
from engine.core.nodes2d import Node2D
from engine.godot_scene2d.types import Point2


class AudioStreamPlayer2D(Node2D):
    """2D positional audio player."""
    
    def __init__(self, name: str = "AudioStreamPlayer2D"):
        super().__init__(name)
        self._stream: Optional[any] = None
        self._volume_db: float = 0.0
        self._pitch_scale: float = 1.0
        self._playing: bool = False
        self._autoplay: bool = False
        self._max_distance: float = 2000.0
        self._attenuation: float = 1.0
        self._area_mask: int = 1
        self._bus: str = "Master"
        
        self._finished_callbacks: List[Callable] = []
    
    def set_stream(self, stream: Optional[any]) -> None:
        self._stream = stream
    
    def get_stream(self) -> Optional[any]:
        return self._stream
    
    def set_volume_db(self, volume_db: float) -> None:
        self._volume_db = volume_db
    
    def get_volume_db(self) -> float:
        return self._volume_db
    
    def set_pitch_scale(self, pitch_scale: float) -> None:
        self._pitch_scale = max(0.01, pitch_scale)
    
    def get_pitch_scale(self) -> float:
        return self._pitch_scale
    
    def play(self, from_position: float = 0.0) -> None:
        self._playing = True
    
    def stop(self) -> None:
        self._playing = False
    
    def pause(self) -> None:
        self._playing = False
    
    def is_playing(self) -> bool:
        return self._playing
    
    def set_autoplay(self, autoplay: bool) -> None:
        self._autoplay = autoplay
    
    def is_autoplay_enabled(self) -> bool:
        return self._autoplay
    
    def set_max_distance(self, max_distance: float) -> None:
        self._max_distance = max(0.0, max_distance)
    
    def get_max_distance(self) -> float:
        return self._max_distance
    
    def set_attenuation(self, attenuation: float) -> None:
        self._attenuation = max(0.0, attenuation)
    
    def get_attenuation(self) -> float:
        return self._attenuation
    
    def set_area_mask(self, mask: int) -> None:
        self._area_mask = mask
    
    def get_area_mask(self) -> int:
        return self._area_mask
    
    def set_bus(self, bus: str) -> None:
        self._bus = bus
    
    def get_bus(self) -> str:
        return self._bus
    
    def get_playback_position(self) -> float:
        return 0.0
    
    def seek(self, to_position: float) -> None:
        pass
    
    def connect_finished(self, callback: Callable) -> None:
        self._finished_callbacks.append(callback)
    
    def __repr__(self) -> str:
        return f"AudioStreamPlayer2D('{self.name}', playing={self._playing}, bus='{self._bus}')"
