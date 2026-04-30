# /**************************************************************************/
# /*  animation_clip.py                                                     */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Animation clip containing multiple tracks."""

from typing import Dict, List, Optional
from engine.animation.animation_track import AnimationTrack

import logging

logger = logging.getLogger(__name__)


class AnimationClip:
    """A complete animation with multiple tracks."""

    def __init__(self, name: str = "Animation", duration: float = 1.0):
        self.name = name
        self.duration = duration
        self.tracks: Dict[str, AnimationTrack] = {}
        self._loop_time: Optional[float] = None  # Time to loop back to

    def add_track(self, track: AnimationTrack) -> None:
        """Add an animation track."""
        self.tracks[track.name] = track

    def remove_track(self, name: str) -> None:
        """Remove a track by name."""
        if name in self.tracks:
            del self.tracks[name]

    def get_track(self, name: str) -> Optional[AnimationTrack]:
        """Get a track by name."""
        return self.tracks.get(name)

    def apply(self, target: any, time: float) -> None:
        """Apply all tracks to target at given time."""
        # Clamp time to duration
        clamped_time = max(0.0, min(time, self.duration))

        for track in self.tracks.values():
            track.apply(target, clamped_time)

    def reset(self, target: any) -> None:
        """Reset target to initial state."""
        # Apply first keyframe of each track
        for track in self.tracks.values():
            track.apply(target, 0.0)

    def set_loop(self, loop: bool, loop_time: Optional[float] = None) -> None:
        """Set loop behavior."""
        if loop:
            self._loop_time = loop_time or 0.0
        else:
            self._loop_time = None

    def get_loop_time(self) -> Optional[float]:
        """Get loop back time, or None if not looping."""
        return self._loop_time

    @property
    def is_looping(self) -> bool:
        return self._loop_time is not None

    def get_track_names(self) -> List[str]:
        """Get list of track names."""
        return list(self.tracks.keys())

    def optimize(self) -> None:
        """Optimize clip by removing redundant keyframes."""
        for track in self.tracks.values():
            if len(track.keyframes) < 3:
                continue

            # Remove keyframes that don't change value
            to_remove = []
            for i in range(1, len(track.keyframes) - 1):
                prev_kf = track.keyframes[i - 1]
                curr_kf = track.keyframes[i]
                next_kf = track.keyframes[i + 1]

                # If value is same as prev and next, and all linear, remove
                if (prev_kf.value == curr_kf.value == next_kf.value and
                    prev_kf.easing == curr_kf.easing == next_kf.easing == "linear"):
                    to_remove.append(curr_kf)

            for kf in to_remove:
                track.keyframes.remove(kf)

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "name": self.name,
            "duration": self.duration,
            "loop_time": self._loop_time,
            "tracks": [
                {
                    "name": track.name,
                    "keyframes": [
                        {
                            "time": kf.time,
                            "value": kf.value,
                            "easing": kf.easing
                        }
                        for kf in track.keyframes
                    ]
                }
                for track in self.tracks.values()
            ]
        }
