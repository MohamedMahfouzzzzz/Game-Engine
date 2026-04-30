# /**************************************************************************/
# /*  animation_controller.py                                              */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Native animation controller for engine."""

from typing import Dict, Optional, List, Callable
from dataclasses import dataclass
from enum import Enum

class AnimationState(Enum):
    """Animation playback states."""
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"
    FINISHED = "finished"


@dataclass
class AnimationKeyframe:
    """Single animation keyframe."""
    time: float
    value: float
    easing: str = "linear"


@dataclass
class AnimationTrack:
    """Animation track for a single property."""
    property_name: str
    keyframes: List[AnimationKeyframe]
    loop: bool = False


@dataclass
class Animation:
    """Animation data."""
    name: str
    duration: float
    tracks: Dict[str, AnimationTrack]
    loop: bool = False


class AnimationController:
    """Native engine animation controller for managing animations."""

    def __init__(self):
        self._animations: Dict[str, Animation] = {}
        self._current_animation: Optional[str] = None
        self._playback_time: float = 0.0
        self._state: AnimationState = AnimationState.STOPPED
        self._playback_speed: float = 1.0
        self._animation_finished_callbacks: Dict[str, List[Callable]] = {}

    def add_animation(self, animation: Animation) -> None:
        """Add an animation to the controller."""
        self._animations[animation.name] = animation
        self._animation_finished_callbacks[animation.name] = []

    def remove_animation(self, name: str) -> bool:
        """Remove an animation."""
        if name in self._animations:
            del self._animations[name]
            if name in self._animation_finished_callbacks:
                del self._animation_finished_callbacks[name]
            return True
        return False

    def play(self, name: str) -> bool:
        """Play an animation."""
        if name not in self._animations:
            return False

        self._current_animation = name
        self._playback_time = 0.0
        self._state = AnimationState.PLAYING
        return True

    def pause(self) -> None:
        """Pause current animation."""
        if self._state == AnimationState.PLAYING:
            self._state = AnimationState.PAUSED

    def resume(self) -> None:
        """Resume paused animation."""
        if self._state == AnimationState.PAUSED:
            self._state = AnimationState.PLAYING

    def stop(self) -> None:
        """Stop current animation."""
        self._state = AnimationState.STOPPED
        self._playback_time = 0.0

    def update(self, delta_time: float) -> None:
        """Update animation playback."""
        if self._state != AnimationState.PLAYING:
            return

        if not self._current_animation:
            return

        anim = self._animations[self._current_animation]
        self._playback_time += delta_time * self._playback_speed

        # Check if animation finished
        if self._playback_time >= anim.duration:
            if anim.loop:
                self._playback_time = 0.0
            else:
                self._state = AnimationState.FINISHED
                self._playback_time = anim.duration
                self._trigger_finished(self._current_animation)

    def get_value(self, property_name: str) -> Optional[float]:
        """Get current interpolated value for a property."""
        if not self._current_animation:
            return None

        anim = self._animations[self._current_animation]
        if property_name not in anim.tracks:
            return None

        track = anim.tracks[property_name]
        return self._interpolate(track.keyframes, self._playback_time)

    def _interpolate(self, keyframes: List[AnimationKeyframe], time: float) -> float:
        """Interpolate value at given time."""
        if not keyframes:
            return 0.0

        # Find surrounding keyframes
        prev_kf = None
        next_kf = None

        for kf in keyframes:
            if kf.time <= time:
                prev_kf = kf
            else:
                next_kf = kf
                break

        if prev_kf is None:
            return keyframes[0].value
        if next_kf is None:
            return prev_kf.value

        # Linear interpolation
        t = (time - prev_kf.time) / (next_kf.time - prev_kf.time)
        return prev_kf.value + (next_kf.value - prev_kf.value) * t

    def set_playback_speed(self, speed: float) -> None:
        """Set animation playback speed."""
        self._playback_speed = max(0.1, speed)

    def get_playback_speed(self) -> float:
        """Get current playback speed."""
        return self._playback_speed

    def get_state(self) -> AnimationState:
        """Get current animation state."""
        return self._state

    def get_current_animation(self) -> Optional[str]:
        """Get current animation name."""
        return self._current_animation

    def get_playback_time(self) -> float:
        """Get current playback time."""
        return self._playback_time

    def on_animation_finished(self, name: str, callback: Callable) -> None:
        """Register callback for when animation finishes."""
        if name in self._animation_finished_callbacks:
            self._animation_finished_callbacks[name].append(callback)

    def _trigger_finished(self, name: str) -> None:
        """Trigger animation finished callbacks."""
        if name in self._animation_finished_callbacks:
            for callback in self._animation_finished_callbacks[name]:
                callback()
