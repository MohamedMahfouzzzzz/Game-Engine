# /**************************************************************************/
# /*  animation_player.py                                                   */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Animation player for controlling animation playback."""

import logging
from typing import Dict, List, Optional, Callable
from engine.animation.animation_clip import AnimationClip

logger = logging.getLogger(__name__)


class AnimationPlayer:
    """Controls animation playback for a node or scene."""

    def __init__(self, target=None):
        self.target = target  # The node/scene being animated
        self._clips: Dict[str, AnimationClip] = {}
        self._current_clip: Optional[AnimationClip] = None
        self._current_name: str = ""

        # Playback state
        self._playing: bool = False
        self._paused: bool = False
        self._time: float = 0.0
        self._speed: float = 1.0
        self._loop: bool = false

        # Callbacks
        self._on_finished: Optional[Callable[[str], None]] = None
        self._on_started: Optional[Callable[[str], None]] = None
        self._on_looped: Optional[Callable[[str], None]] = None

    def add_clip(self, name: str, clip: AnimationClip) -> None:
        """Add an animation clip."""
        self._clips[name] = clip
        logger.info("Added animation clip: %s", name)

    def remove_clip(self, name: str) -> None:
        """Remove an animation clip."""
        if name in self._clips:
            del self._clips[name]
            logger.info("Removed animation clip: %s", name)
            if self._current_name == name:
                self.stop()

    def play(self, name: str, blend_time: float = 0.0) -> bool:
        """Play an animation clip."""
        if name not in self._clips:
            return False

        # Handle blending (simplified)
        if blend_time > 0 and self._current_clip:
            # Would blend from current to new
            pass

        self._current_clip = self._clips[name]
        self._current_name = name
        self._time = 0.0
        self._playing = True
        self._paused = False

        if self._on_started:
            self._on_started(name)

        return True

    def stop(self) -> None:
        """Stop playback."""
        self._playing = False
        self._paused = False
        self._time = 0.0

        if self._current_clip:
            self._current_clip.reset(self.target)

    def pause(self) -> None:
        """Pause playback."""
        if self._playing:
            self._paused = True

    def resume(self) -> None:
        """Resume playback."""
        if self._paused:
            self._paused = False
            self._playing = True

    def update(self, delta_time: float) -> None:
        """Update animation state."""
        if not self._playing or self._paused or not self._current_clip:
            return

        self._time += delta_time * self._speed
        duration = self._current_clip.duration

        # Handle loop
        if self._time >= duration:
            if self._loop:
                self._time = self._time % duration
                if self._on_looped:
                    self._on_looped(self._current_name)
            else:
                self._time = duration
                self._playing = False
                if self._on_finished:
                    self._on_finished(self._current_name)

        # Apply animation
        self._current_clip.apply(self.target, self._time)

    def seek(self, time: float) -> None:
        """Seek to specific time."""
        if self._current_clip:
            self._time = max(0.0, min(time, self._current_clip.duration))
            self._current_clip.apply(self.target, self._time)

    def set_speed(self, speed: float) -> None:
        """Set playback speed."""
        self._speed = speed

    @property
    def current_time(self) -> float:
        return self._time

    @property
    def current_duration(self) -> float:
        if self._current_clip:
            return self._current_clip.duration
        return 0.0

    @property
    def is_playing(self) -> bool:
        return self._playing and not self._paused

    @property
    def is_paused(self) -> bool:
        return self._paused

    def get_clip_names(self) -> List[str]:
        """Get list of available clip names."""
        return list(self._clips.keys())

    def connect_finished(self, callback: Callable[[str], None]) -> None:
        """Connect animation finished callback."""
        self._on_finished = callback

    def connect_started(self, callback: Callable[[str], None]) -> None:
        """Connect animation started callback."""
        self._on_started = callback

    def connect_looped(self, callback: Callable[[str], None]) -> None:
        """Connect animation looped callback."""
        self._on_looped = callback
