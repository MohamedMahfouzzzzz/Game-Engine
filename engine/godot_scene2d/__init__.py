# /**************************************************************************/
# /*  __init__.py                                                           */
# /**************************************************************************/

"""Godot Engine scene/2d port - Complete 2D node system."""

# Core 2D Nodes
from engine.core.nodes2d import Node2D, Vector2

# Visual Nodes
from engine.godot_scene2d.sprite_2d import Sprite2D, Texture2D
from engine.godot_scene2d.animated_sprite_2d import AnimatedSprite2D, SpriteFrames
from engine.godot_scene2d.light_2d import Light2D, Light2DShadowFilter
from engine.godot_scene2d.light_occluder_2d import LightOccluder2D, OccluderPolygon2D
from engine.godot_scene2d.line_2d import Line2D, Line2DJointMode, Line2DCapMode
from engine.godot_scene2d.polygon_2d import Polygon2D
from engine.godot_scene2d.mesh_instance_2d import MeshInstance2D
from engine.godot_scene2d.multimesh_instance_2d import MultiMeshInstance2D

# Particles
from engine.godot_scene2d.cpu_particles_2d import CPUParticles2D, CPUParticles2DEmissionShape

# Camera
from engine.godot_scene2d.camera_2d import Camera2D, Camera2DAnchorMode, Camera2DProcessCallback

# Tilemap
from engine.godot_scene2d.tile_map import TileMap, TileMapLayer
from engine.godot_scene2d.tile_set import TileSet
from engine.godot_scene2d.tile_data import TileData

# Parallax
from engine.godot_scene2d.parallax_background import ParallaxBackground
from engine.godot_scene2d.parallax_layer import ParallaxLayer
from engine.godot_scene2d.parallax_2d import Parallax2D

# Path
from engine.godot_scene2d.path_2d import Path2D, PathFollow2D

# Audio
from engine.godot_scene2d.audio_listener_2d import AudioListener2D
from engine.godot_scene2d.audio_stream_player_2d import AudioStreamPlayer2D

# Utilities
from engine.godot_scene2d.visible_on_screen_notifier_2d import VisibleOnScreenNotifier2D, VisibleOnScreenEnabler2D
from engine.godot_scene2d.remote_transform_2d import RemoteTransform2D
from engine.godot_scene2d.marker_2d import Marker2D
from engine.godot_scene2d.skeleton_2d import Skeleton2D, Bone2D
from engine.godot_scene2d.canvas_group import CanvasGroup
from engine.godot_scene2d.canvas_modulate import CanvasModulate
from engine.godot_scene2d.back_buffer_copy import BackBufferCopy

# Collision Detection
from engine.godot_scene2d.ray_cast_2d import RayCast2D
from engine.godot_scene2d.shape_cast_2d import ShapeCast2D

# Input
from engine.godot_scene2d.touch_screen_button import TouchScreenButton, TouchScreenButtonVisibilityMode

# Joints
from engine.godot_scene2d.joint_2d import Joint2D, PinJoint2D, DampedSpringJoint2D, GrooveJoint2D, MotorJoint2D

# Navigation
from engine.godot_scene2d.navigation import NavigationRegion2D, NavigationAgent2D, NavigationObstacle2D

# Physics (submodule)
from engine.godot_scene2d.physics import (
    PhysicsBody2D, StaticBody2D, AnimatableBody2D, RigidBody2D, RigidBody2DMode,
    CharacterBody2D, CollisionShape2D, CollisionPolygon2D,
    Shape2D, RectangleShape2D, CircleShape2D, CapsuleShape2D, SeparationRayShape2D, WorldBoundaryShape2D
)

# Types
from engine.godot_scene2d.types import Side, HorizontalAlignment, VerticalAlignment, Point2, Size2, Rect2, Vector2i, Color

__all__ = [
    "Node2D", "Vector2",
    "Sprite2D", "Texture2D", "AnimatedSprite2D", "SpriteFrames",
    "Light2D", "Light2DShadowFilter", "LightOccluder2D", "OccluderPolygon2D",
    "Line2D", "Line2DJointMode", "Line2DCapMode", "Polygon2D",
    "MeshInstance2D", "MultiMeshInstance2D",
    "CPUParticles2D", "CPUParticles2DEmissionShape",
    "Camera2D", "Camera2DAnchorMode", "Camera2DProcessCallback",
    "TileMap", "TileSet", "TileMapLayer", "TileData",
    "ParallaxBackground", "ParallaxLayer", "Parallax2D",
    "Path2D", "PathFollow2D",
    "AudioListener2D", "AudioStreamPlayer2D",
    "VisibleOnScreenNotifier2D", "VisibleOnScreenEnabler2D",
    "RemoteTransform2D", "Marker2D", "Skeleton2D", "Bone2D",
    "CanvasGroup", "CanvasModulate", "BackBufferCopy",
    "RayCast2D", "ShapeCast2D",
    "TouchScreenButton", "TouchScreenButtonVisibilityMode",
    "Joint2D", "PinJoint2D", "DampedSpringJoint2D", "GrooveJoint2D", "MotorJoint2D",
    "NavigationRegion2D", "NavigationAgent2D", "NavigationObstacle2D",
    "PhysicsBody2D", "StaticBody2D", "AnimatableBody2D", "RigidBody2D", "RigidBody2DMode",
    "CharacterBody2D", "CollisionShape2D", "CollisionPolygon2D",
    "Shape2D", "RectangleShape2D", "CircleShape2D", "CapsuleShape2D", "SeparationRayShape2D", "WorldBoundaryShape2D",
    "Side", "HorizontalAlignment", "VerticalAlignment", "Point2", "Size2", "Rect2", "Vector2i", "Color"
]
