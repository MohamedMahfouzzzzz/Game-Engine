# /**************************************************************************/
# /*  __init__.py                                                           */
# /**************************************************************************/

"""Godot Engine scene/animation port - Complete animation system."""

# Types
from engine.godot_animation.types import (
    TrackType, AnimationLoopMode, InterpolationType,
    Keyframe, AnimationMethod, AnimationBezierTrack
)

# Core
from engine.godot_animation.animation import Animation
from engine.godot_animation.animation_library import AnimationLibrary
from engine.godot_animation.animation_player import AnimationPlayer, AnimationPlayerPlaybackProcessCallback
from engine.godot_animation.animation_mixer import AnimationMixer

# Tree
from engine.godot_animation.animation_tree import AnimationTree
from engine.godot_animation.animation_node import (
    AnimationNode, AnimationNodeBlend2, AnimationNodeBlend3,
    AnimationNodeOneShot, AnimationNodeStateMachine, AnimationNodeStateMachineTransition,
    AnimationNodeStateMachinePlayback, AnimationNodeTransition
)

# Tween
from engine.godot_animation.tween import Tween, TweenTransitionType, TweenEaseType

# Cache
from engine.godot_animation.cache_node_path import CacheNodePath

__all__ = [
    "TrackType", "AnimationLoopMode", "InterpolationType", "Keyframe",
    "AnimationMethod", "AnimationBezierTrack",
    "Animation", "AnimationLibrary", "AnimationPlayer", "AnimationPlayerPlaybackProcessCallback",
    "AnimationMixer", "AnimationTree", "AnimationNode", "AnimationNodeBlend2",
    "AnimationNodeBlend3", "AnimationNodeOneShot", "AnimationNodeStateMachine",
    "AnimationNodeStateMachineTransition", "AnimationNodeStateMachinePlayback",
    "AnimationNodeTransition", "Tween", "TweenTransitionType", "TweenEaseType",
    "CacheNodePath",
]
