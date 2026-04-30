# /**************************************************************************/
# /*  animation.py                                                          */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Core animation resource with tracks and keyframes."""

from enum import IntEnum
from dataclasses import dataclass
from typing import Any, List, Dict, Optional


class TrackType(IntEnum):
    """Types of animation tracks."""
    TYPE_VALUE = 0
    TYPE_POSITION_2D = 1
    TYPE_ROTATION_2D = 2
    TYPE_SCALE_2D = 3
    TYPE_METHOD = 4
    TYPE_BEZIER = 5
    TYPE_AUDIO = 6
    TYPE_ANIMATION = 7


class AnimationLoopMode(IntEnum):
    """How animation loops."""
    LOOP_NONE = 0
    LOOP_LINEAR = 1
    LOOP_PINGPONG = 2


class InterpolationType(IntEnum):
    """Keyframe interpolation methods."""
    INTERPOLATION_NEAREST = 0
    INTERPOLATION_LINEAR = 1
    INTERPOLATION_CUBIC = 2


@dataclass
class Keyframe:
    """Single keyframe with value and timing."""
    time: float = 0.0
    value: Any = None
    transition: float = 1.0
    in_handle: float = 0.0
    out_handle: float = 0.0


@dataclass
class AnimationMethod:
    """Method call for method tracks."""
    method: str = ""
    args: tuple = ()


@dataclass
class AnimationBezierTrack:
    """Bezier curve control points."""
    value: float = 0.0
    in_handle: float = 0.0
    out_handle: float = 0.0


class Track:
    """Single animation track with keyframes."""
    
    def __init__(self, track_type: TrackType = TrackType.TYPE_VALUE):
        self.track_type: TrackType = track_type
        self.path: str = ""
        self.interp: InterpolationType = InterpolationType.INTERPOLATION_LINEAR
        self.loop_wrap: bool = True
        self.enabled: bool = True
        self.keyframes: List[Keyframe] = []
    
    def insert_key(self, time: float, value: Any, transition: float = 1.0) -> int:
        """Insert keyframe and return its index."""
        keyframe = Keyframe(time=time, value=value, transition=transition)
        self.keyframes.append(keyframe)
        self.keyframes.sort(key=lambda k: k.time)
        return self.keyframes.index(keyframe)
    
    def remove_key(self, index: int) -> bool:
        """Remove keyframe at index."""
        if 0 <= index < len(self.keyframes):
            del self.keyframes[index]
            return True
        return False


class Animation:
    """Animation resource containing tracks and keyframes.
    
    Features:
    - Multiple track types (value, method, audio, etc.)
    - Keyframe interpolation (nearest, linear, cubic)
    - Loop modes (none, linear, ping-pong)
    - Compression for smaller file size
    """
    
    def __init__(self, name: str = ""):
        self._name: str = name
        self._length: float = 1.0
        self._loop_mode: AnimationLoopMode = AnimationLoopMode.LOOP_NONE
        self._step: float = 0.0
        self._tracks: List[Track] = []
        self._data: Dict[str, Any] = {}
        self._compression_mode: int = 0
        self._capture_included: bool = False
    
    # Length and timing
    def set_length(self, time: float) -> None:
        """Set animation duration in seconds."""
        self._length = max(0.0, time)
    
    def get_length(self) -> float:
        return self._length
    
    def set_loop_mode(self, mode: AnimationLoopMode) -> None:
        self._loop_mode = mode
    
    def get_loop_mode(self) -> AnimationLoopMode:
        return self._loop_mode
    
    def set_step(self, step: float) -> None:
        """Set step value for snapping."""
        self._step = max(0.0, step)
    
    def get_step(self) -> float:
        return self._step
    
    # Track management
    def add_track(self, track_type: TrackType, at_position: int = -1) -> int:
        """Add track and return its index."""
        track = Track(track_type)
        if at_position < 0:
            self._tracks.append(track)
            return len(self._tracks) - 1
        else:
            self._tracks.insert(at_position, track)
            return at_position
    
    def remove_track(self, track_idx: int) -> None:
        if 0 <= track_idx < len(self._tracks):
            del self._tracks[track_idx]
    
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
    
    def track_set_interpolation_type(self, track_idx: int, interp: InterpolationType) -> None:
        if 0 <= track_idx < len(self._tracks):
            self._tracks[track_idx].interp = interp
    
    def track_get_interpolation_type(self, track_idx: int) -> InterpolationType:
        if 0 <= track_idx < len(self._tracks):
            return self._tracks[track_idx].interp
        return InterpolationType.INTERPOLATION_LINEAR
    
    # Keyframe operations
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
    
    def track_set_key_time(self, track_idx: int, key_idx: int, time: float) -> None:
        if 0 <= track_idx < len(self._tracks):
            if 0 <= key_idx < len(self._tracks[track_idx].keyframes):
                self._tracks[track_idx].keyframes[key_idx].time = time
                self._tracks[track_idx].keyframes.sort(key=lambda k: k.time)
    
    def track_set_key_value(self, track_idx: int, key_idx: int, value: Any) -> None:
        if 0 <= track_idx < len(self._tracks):
            if 0 <= key_idx < len(self._tracks[track_idx].keyframes):
                self._tracks[track_idx].keyframes[key_idx].value = value
    
    def track_set_key_transition(self, track_idx: int, key_idx: int, transition: float) -> None:
        if 0 <= track_idx < len(self._tracks):
            if 0 <= key_idx < len(self._tracks[track_idx].keyframes):
                self._tracks[track_idx].keyframes[key_idx].transition = transition
    
    def clear(self) -> None:
        """Remove all tracks."""
        self._tracks.clear()
    
    def find_track(self, path: str, track_type: TrackType) -> int:
        """Find track by path and type. Returns index or -1."""
        for i, track in enumerate(self._tracks):
            if track.path == path and track.track_type == track_type:
                return i
        return -1
    
    def copy_track(self, track_idx: int, to_animation: 'Animation') -> None:
        """Copy track to another animation."""
        if 0 <= track_idx < len(self._tracks):
            source = self._tracks[track_idx]
            target_idx = to_animation.add_track(source.track_type)
            target = to_animation._tracks[target_idx]
            target.path = source.path
            target.interp = source.interp
            target.loop_wrap = source.loop_wrap
            target.enabled = source.enabled
            target.keyframes = [Keyframe(k.time, k.value, k.transition) for k in source.keyframes]
    
    def __repr__(self) -> str:
        return f"Animation('{self._name}', length={self._length}, tracks={len(self._tracks)}, loop={self._loop_mode.name})"
