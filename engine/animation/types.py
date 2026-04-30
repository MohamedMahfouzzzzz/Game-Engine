# /**************************************************************************/
# /*  types.py                                                              */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Animation types and helpers."""

from enum import IntEnum
from dataclasses import dataclass
from typing import Any


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
