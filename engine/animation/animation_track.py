# /**************************************************************************/
# /*  animation_track.py                                                    */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Animation tracks for keyframe animation."""

from typing import Any, Callable, List, Optional, Dict
from dataclasses import dataclass

import logging

logger = logging.getLogger(__name__)


@dataclass
class Keyframe:
    """A single keyframe with time and value."""
    time: float
    value: Any
    easing: str = "linear"


class AnimationTrack:
    """Base class for animation tracks."""

    def __init__(self, name: str):
        self.name = name
        self.keyframes: List[Keyframe] = []
        self._sorted: bool = True

    def add_keyframe(self, time: float, value: Any, easing: str = "linear") -> None:
        """Add a keyframe."""
        self.keyframes.append(Keyframe(time, value, easing))
        self._sorted = False

    def remove_keyframe(self, time: float) -> bool:
        """Remove keyframe at specific time."""
        for i, kf in enumerate(self.keyframes):
            if abs(kf.time - time) < 0.0001:
                self.keyframes.pop(i)
                return True
        return False

    def get_keyframe_at(self, time: float) -> Optional[Keyframe]:
        """Get keyframe closest to time."""
        self._sort_keyframes()
        if not self.keyframes:
            return None

        closest = self.keyframes[0]
        min_diff = abs(closest.time - time)

        for kf in self.keyframes:
            diff = abs(kf.time - time)
            if diff < min_diff:
                min_diff = diff
                closest = kf

        return closest

    def _sort_keyframes(self) -> None:
        """Sort keyframes by time."""
        if not self._sorted:
            self.keyframes.sort(key=lambda kf: kf.time)
            self._sorted = True

    def evaluate(self, time: float) -> Any:
        """Evaluate track at specific time."""
        self._sort_keyframes()

        if not self.keyframes:
            return None

        if time <= self.keyframes[0].time:
            return self.keyframes[0].value

        if time >= self.keyframes[-1].time:
            return self.keyframes[-1].value

        # Find surrounding keyframes
        for i in range(len(self.keyframes) - 1):
            kf1 = self.keyframes[i]
            kf2 = self.keyframes[i + 1]

            if kf1.time <= time <= kf2.time:
                # Interpolate
                t = (time - kf1.time) / (kf2.time - kf1.time) if kf2.time != kf1.time else 0
                return self._interpolate(kf1.value, kf2.value, t, kf1.easing)

        return self.keyframes[-1].value

    def _interpolate(self, a: Any, b: Any, t: float, easing: str) -> Any:
        """Interpolate between two values."""
        from engine.animation.tween import Easing
        t = Easing.apply(easing, t)
        return a + (b - a) * t


class PropertyTrack(AnimationTrack):
    """Track that animates a property on the target."""

    def __init__(self, name: str, property_path: str):
        super().__init__(name)
        self.property_path = property_path  # e.g., "position:x"

    def apply(self, target: Any, time: float) -> None:
        """Apply animation value to target property."""
        value = self.evaluate(time)
        if value is None:
            return

        # Navigate property path
        parts = self.property_path.split(":")
        obj = target

        for part in parts[:-1]:
            obj = getattr(obj, part, None)
            if obj is None:
                return

        prop_name = parts[-1]
        if hasattr(obj, prop_name):
            setattr(obj, prop_name, value)


class EventTrack(AnimationTrack):
    """Track that triggers events at specific times."""

    def __init__(self, name: str):
        super().__init__(name)
        self._last_time: float = 0.0
        self._callbacks: Dict[str, Callable[[], None]] = {}

    def add_event(self, time: float, event_name: str, callback: Optional[Callable[[], None]] = None) -> None:
        """Add an event at specific time."""
        self.add_keyframe(time, event_name)
        if callback:
            self._callbacks[event_name] = callback

    def apply(self, target: Any, time: float) -> None:
        """Trigger events that passed in this frame."""
        self._sort_keyframes()

        for kf in self.keyframes:
            if self._last_time < kf.time <= time:
                event_name = kf.value
                if event_name in self._callbacks:
                    self._callbacks[event_name]()

        self._last_time = time

    def reset(self) -> None:
        """Reset event track state."""
        self._last_time = 0.0


class TransformTrack(AnimationTrack):
    """Track specifically for transform animation."""

    def __init__(self, name: str, transform_type: str = "position"):
        super().__init__(name)
        self.transform_type = transform_type  # position, rotation, scale

    def apply(self, target: Any, time: float) -> None:
        """Apply transform animation."""
        value = self.evaluate(time)
        if value is None:
            return

        if self.transform_type == "position" and hasattr(target, "set_position"):
            if isinstance(value, (list, tuple)) and len(value) >= 2:
                target.set_position(value[0], value[1])
        elif self.transform_type == "rotation" and hasattr(target, "set_rotation"):
            target.set_rotation(value)
        elif self.transform_type == "scale" and hasattr(target, "set_scale"):
            if isinstance(value, (list, tuple)) and len(value) >= 2:
                target.set_scale(value[0], value[1])
