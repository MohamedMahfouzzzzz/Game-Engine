# /**************************************************************************/
# /*  __init__.py                                                           */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Animation system for the game engine."""

from engine.animation.animation import Animation, Track, TrackType, AnimationLoopMode, InterpolationType, Keyframe
from engine.animation.animation_player import AnimationPlayer
from engine.animation.animation_library import AnimationLibrary
from engine.animation.animation_mixer import AnimationMixer
from engine.animation.animation_tree import (
    AnimationTree, AnimationNode,
    AnimationNodeStateMachine, AnimationNodeStateMachinePlayback,
    AnimationNodeBlendTree, AnimationNodeBlend2, AnimationNodeBlend3,
    AnimationNodeOneShot
)
from engine.animation.animation_track import AnimationTrack, PropertyTrack, EventTrack
from engine.animation.animation_clip import AnimationClip
from engine.animation.tween import Tween, Easing
from engine.animation.skeleton2d import Skeleton2D, Bone2D

import logging


logger = logging.getLogger(__name__)


__all__ = [
    # Core animation
    "Animation",
    "Track",
    "TrackType",
    "AnimationLoopMode",
    "InterpolationType",
    "Keyframe",
    # Players
    "AnimationPlayer",
    "AnimationMixer",
    "AnimationTree",
    "AnimationNode",
    "AnimationNodeStateMachine",
    "AnimationNodeStateMachinePlayback",
    "AnimationNodeBlendTree",
    "AnimationNodeBlend2",
    "AnimationNodeBlend3",
    "AnimationNodeOneShot",
    # Library
    "AnimationLibrary",
    # Legacy tracks
    "AnimationTrack",
    "PropertyTrack",
    "EventTrack",
    "AnimationClip",
    # Tweening
    "Tween",
    "Easing",
    # Skeleton
    "Skeleton2D",
    "Bone2D",
]
