# /**************************************************************************/
# /*  tween.py                                                              */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Tweening/Easing functions for smooth animation."""

import math
from typing import Callable, Optional, Any

import logging


logger = logging.getLogger(__name__)



class Easing:
    """Collection of easing functions."""

    @staticmethod
    def linear(t: float) -> float:
        return t

    @staticmethod
    def ease_in_quad(t: float) -> float:
        return t * t

    @staticmethod
    def ease_out_quad(t: float) -> float:
        return 1 - (1 - t) * (1 - t)

    @staticmethod
    def ease_in_out_quad(t: float) -> float:
        return 2 * t * t if t < 0.5 else 1 - math.pow(-2 * t + 2, 2) / 2

    @staticmethod
    def ease_in_cubic(t: float) -> float:
        return t * t * t

    @staticmethod
    def ease_out_cubic(t: float) -> float:
        return 1 - math.pow(1 - t, 3)

    @staticmethod
    def ease_in_out_cubic(t: float) -> float:
        return 4 * t * t * t if t < 0.5 else 1 - math.pow(-2 * t + 2, 3) / 2

    @staticmethod
    def ease_in_sine(t: float) -> float:
        return 1 - math.cos(t * math.pi / 2)

    @staticmethod
    def ease_out_sine(t: float) -> float:
        return math.sin(t * math.pi / 2)

    @staticmethod
    def ease_in_out_sine(t: float) -> float:
        return -(math.cos(math.pi * t) - 1) / 2

    @staticmethod
    def ease_in_expo(t: float) -> float:
        return 0 if t == 0 else math.pow(2, 10 * (t - 1))

    @staticmethod
    def ease_out_expo(t: float) -> float:
        return 1 if t == 1 else 1 - math.pow(2, -10 * t)

    @staticmethod
    def ease_in_out_expo(t: float) -> float:
        if t == 0:
            return 0
        if t == 1:
            return 1
        return math.pow(2, 10 * (t * 2 - 1)) / 2 if t < 0.5 else (2 - math.pow(2, -10 * (t * 2 - 1))) / 2

    @staticmethod
    def ease_in_elastic(t: float) -> float:
        if t == 0:
            return 0
        if t == 1:
            return 1
        return -math.pow(2, 10 * (t - 1)) * math.sin((t - 1.1) * 5 * math.pi)

    @staticmethod
    def ease_out_elastic(t: float) -> float:
        if t == 0:
            return 0
        if t == 1:
            return 1
        return math.pow(2, -10 * t) * math.sin((t - 0.1) * 5 * math.pi) + 1

    @staticmethod
    def ease_in_bounce(t: float) -> float:
        return 1 - Easing.ease_out_bounce(1 - t)

    @staticmethod
    def ease_out_bounce(t: float) -> float:
        if t < 1 / 2.75:
            return 7.5625 * t * t
        elif t < 2 / 2.75:
            t -= 1.5 / 2.75
            return 7.5625 * t * t + 0.75
        elif t < 2.5 / 2.75:
            t -= 2.25 / 2.75
            return 7.5625 * t * t + 0.9375
        else:
            t -= 2.625 / 2.75
            return 7.5625 * t * t + 0.984375

    @staticmethod
    def ease_in_out_bounce(t: float) -> float:
        return (1 - Easing.ease_out_bounce(1 - 2 * t)) / 2 if t < 0.5 else (1 + Easing.ease_out_bounce(2 * t - 1)) / 2

    @classmethod
    def apply(cls, easing_name: str, t: float) -> float:
        """Apply easing function by name."""
        methods = {
            "linear": cls.linear,
            "ease_in_quad": cls.ease_in_quad,
            "ease_out_quad": cls.ease_out_quad,
            "ease_in_out_quad": cls.ease_in_out_quad,
            "ease_in_cubic": cls.ease_in_cubic,
            "ease_out_cubic": cls.ease_out_cubic,
            "ease_in_out_cubic": cls.ease_in_out_cubic,
            "ease_in_sine": cls.ease_in_sine,
            "ease_out_sine": cls.ease_out_sine,
            "ease_in_out_sine": cls.ease_in_out_sine,
            "ease_in_expo": cls.ease_in_expo,
            "ease_out_expo": cls.ease_out_expo,
            "ease_in_out_expo": cls.ease_in_out_expo,
            "ease_in_elastic": cls.ease_in_elastic,
            "ease_out_elastic": cls.ease_out_elastic,
            "ease_in_bounce": cls.ease_in_bounce,
            "ease_out_bounce": cls.ease_out_bounce,
            "ease_in_out_bounce": cls.ease_in_out_bounce,
        }
        method = methods.get(easing_name, cls.linear)
        return method(t)


class Tween:
    """Simple tween for interpolating values over time."""

    def __init__(
        self,
        target: Any,
        property_name: str,
        end_value: Any,
        duration: float,
        easing: str = "ease_in_out_quad"
    ):
        self.target = target
        self.property_name = property_name
        self.end_value = end_value
        self.duration = duration
        self.easing = easing

        self.start_value = None
        self._time: float = 0.0
        self._playing: bool = False
        self._on_complete: Optional[Callable[[], None]] = None

    def start(self) -> None:
        """Start the tween."""
        if self.target and hasattr(self.target, self.property_name):
            self.start_value = getattr(self.target, self.property_name)
            self._time = 0.0
            self._playing = True

    def update(self, delta_time: float) -> bool:
        """Update tween. Returns True if complete."""
        if not self._playing:
            return True

        self._time += delta_time
        t = min(1.0, self._time / self.duration) if self.duration > 0 else 1.0

        # Apply easing
        eased_t = Easing.apply(self.easing, t)

        # Interpolate
        if self.start_value is not None:
            value = self.start_value + (self.end_value - self.start_value) * eased_t
            setattr(self.target, self.property_name, value)

        if t >= 1.0:
            self._playing = False
            if self._on_complete:
                self._on_complete()
            return True

        return False

    def connect_complete(self, callback: Callable[[], None]) -> None:
        """Connect completion callback."""
        self._on_complete = callback
