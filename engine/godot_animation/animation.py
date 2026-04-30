# /**************************************************************************/
# /*  animation.py                                                          */
# /**************************************************************************/

"""Godot Animation resource - Keyframe animation data."""

from typing import List, Any
from engine.godot_animation.types import TrackType, AnimationLoopMode, InterpolationType, Keyframe


class Track:
    def __init__(self, track_type: TrackType = TrackType.TYPE_VALUE):
        self.track_type = track_type
        self.path = ""
        self.keyframes: List[Keyframe] = []
        self.interpolation = InterpolationType.INTERPOLATION_LINEAR
        self.enabled = True
        self.loop_wrap = True
        self.update_mode = 0
    
    def insert_key(self, time: float, value: Any, transition: float = 1.0) -> int:
        keyframe = Keyframe(time=time, value=value, transition=transition)
        for i, kf in enumerate(self.keyframes):
            if kf.time > time:
                self.keyframes.insert(i, keyframe)
                return i
        self.keyframes.append(keyframe)
        return len(self.keyframes) - 1
    
    def remove_key(self, index: int) -> bool:
        if 0 <= index < len(self.keyframes):
            del self.keyframes[index]
            return True
        return False


class Animation:
    """Animation resource with tracks and keyframes."""
    
    def __init__(self):
        self._length = 1.0
        self._loop_mode = AnimationLoopMode.LOOP_NONE
        self._step = 0.0
        self._speed_scale = 1.0
        self._tracks: List[Track] = []
    
    def set_length(self, length: float) -> None:
        self._length = max(0.000001, length)
    
    def get_length(self) -> float:
        return self._length
    
    def set_loop_mode(self, loop_mode: AnimationLoopMode) -> None:
        self._loop_mode = loop_mode
    
    def get_loop_mode(self) -> AnimationLoopMode:
        return self._loop_mode
    
    def set_step(self, step: float) -> None:
        self._step = max(0.0, step)
    
    def get_step(self) -> float:
        return self._step
    
    def set_speed_scale(self, scale: float) -> None:
        self._speed_scale = max(0.0, scale)
    
    def get_speed_scale(self) -> float:
        return self._speed_scale
    
    def add_track(self, track_type: TrackType) -> int:
        self._tracks.append(Track(track_type=track_type))
        return len(self._tracks) - 1
    
    def remove_track(self, track_idx: int) -> bool:
        if 0 <= track_idx < len(self._tracks):
            del self._tracks[track_idx]
            return True
        return False
    
    def get_track_count(self) -> int:
        return len(self._tracks)
    
    def track_get_type(self, track_idx: int) -> TrackType:
        if 0 <= track_idx < len(self._tracks):
            return self._tracks[track_idx].track_type
        return TrackType.TYPE_VALUE
    
    def track_set_path(self, track_idx: int, path: str) -> None:
        if 0 <= track_idx < len(self._tracks):
            self._tracks[track_idx].path = path
    
    def track_get_path(self, track_idx: int) -> str:
        if 0 <= track_idx < len(self._tracks):
            return self._tracks[track_idx].path
        return ""
    
    def track_set_enabled(self, track_idx: int, enabled: bool) -> None:
        if 0 <= track_idx < len(self._tracks):
            self._tracks[track_idx].enabled = enabled
    
    def track_is_enabled(self, track_idx: int) -> bool:
        if 0 <= track_idx < len(self._tracks):
            return self._tracks[track_idx].enabled
        return False
    
    def track_insert_key(self, track_idx: int, time: float, value: Any, transition: float = 1.0) -> int:
        if 0 <= track_idx < len(self._tracks):
            return self._tracks[track_idx].insert_key(time, value, transition)
        return -1
    
    def track_remove_key(self, track_idx: int, key_idx: int) -> bool:
        if 0 <= track_idx < len(self._tracks):
            return self._tracks[track_idx].remove_key(key_idx)
        return False
    
    def track_get_key_count(self, track_idx: int) -> int:
        if 0 <= track_idx < len(self._tracks):
            return len(self._tracks[track_idx].keyframes)
        return 0
    
    def track_get_key_time(self, track_idx: int, key_idx: int) -> float:
        if 0 <= track_idx < len(self._tracks):
            if 0 <= key_idx < len(self._tracks[track_idx].keyframes):
                return self._tracks[track_idx].keyframes[key_idx].time
        return 0.0
    
    def track_get_key_value(self, track_idx: int, key_idx: int) -> Any:
        if 0 <= track_idx < len(self._tracks):
            if 0 <= key_idx < len(self._tracks[track_idx].keyframes):
                return self._tracks[track_idx].keyframes[key_idx].value
        return None
    
    def clear(self) -> None:
        self._tracks.clear()
    
    def __repr__(self) -> str:
        return f"Animation(length={self._length}, tracks={len(self._tracks)}, loop={self._loop_mode.name})"
