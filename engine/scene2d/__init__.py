# /**************************************************************************/
# /*  __init__.py                                                           */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""2D scene nodes and components.

This module provides all 2D scene graph nodes:
- Visual nodes (Sprite, AnimatedSprite, TileMap)
- Physics nodes (RigidBody, StaticBody, CharacterBody)
- Effect nodes (Particles, Lights, Line2D)
- Utility nodes (Camera, Marker, Path)
"""

# Base types
from engine.core.nodes2d import Node2D, Vector2, Color, Rect2

# Visual nodes
from engine.scene2d.sprite import Sprite2D
from engine.scene2d.animated_sprite import AnimatedSprite2D
from engine.scene2d.tile_map import TileMap
from engine.scene2d.tile_set import TileSet, TileData
from engine.scene2d.polygon import Polygon2D
from engine.scene2d.line import Line2D
from engine.scene2d.mesh_instance import MeshInstance2D
from engine.scene2d.multimesh_instance import MultiMeshInstance2D

# Lighting
from engine.scene2d.light import Light2D, LightOccluder2D

# Camera
from engine.scene2d.camera import Camera2D

# Effects
from engine.scene2d.particles import CPUParticles2D
from engine.scene2d.marker import Marker2D
from engine.scene2d.visible_notifier import VisibleOnScreenNotifier2D

# Physics
from engine.scene2d.physics.physics_body import PhysicsBody2D
from engine.scene2d.physics.static_body import StaticBody2D
from engine.scene2d.physics.rigid_body import RigidBody2D
from engine.scene2d.physics.character_body import CharacterBody2D
from engine.scene2d.physics.collision_shape import CollisionShape2D
from engine.scene2d.physics.collision_polygon import CollisionPolygon2D

# Ray casting
from engine.scene2d.ray_cast import RayCast2D
from engine.scene2d.shape_cast import ShapeCast2D

# Path
from engine.scene2d.path import Path2D, PathFollow2D, Curve2D

# Parallax
from engine.scene2d.parallax import ParallaxBackground, ParallaxLayer, Parallax2D

# Transform
from engine.scene2d.remote_transform import RemoteTransform2D

# Joints
from engine.scene2d.joint import (
    Joint2D, PinJoint2D, DampedSpringJoint2D,
    GrooveJoint2D, MotorJoint2D
)

# Skeleton
from engine.scene2d.skeleton import Skeleton2D, Bone2D

# Audio
from engine.scene2d.audio_player import AudioStreamPlayer2D
from engine.scene2d.audio_listener import AudioListener2D

# Navigation
from engine.scene2d.navigation.region import NavigationRegion2D
from engine.scene2d.navigation.agent import NavigationAgent2D
from engine.scene2d.navigation.obstacle import NavigationObstacle2D

# UI
from engine.scene2d.touch_button import TouchScreenButton

__all__ = [
    # Re-export core types
    "Vector2", "Color", "Rect2", "Node2D",
    
    # Visual
    "Sprite2D",
    "AnimatedSprite2D",
    "TileMap",
    "TileSet",
    "TileData",
    "Polygon2D",
    "Line2D",
    "MeshInstance2D",
    "MultiMeshInstance2D",
    
    # Lighting
    "Light2D",
    "LightOccluder2D",
    
    # Camera
    "Camera2D",
    
    # Effects
    "CPUParticles2D",
    "Marker2D",
    "VisibleOnScreenNotifier2D",
    
    # Physics
    "PhysicsBody2D",
    "StaticBody2D",
    "RigidBody2D",
    "CharacterBody2D",
    "CollisionShape2D",
    "CollisionPolygon2D",
    
    # Ray casting
    "RayCast2D",
    "ShapeCast2D",
    
    # Path
    "Path2D",
    "PathFollow2D",
    "Curve2D",
    
    # Parallax
    "ParallaxBackground",
    "ParallaxLayer",
    "Parallax2D",
    
    # Transform
    "RemoteTransform2D",
    
    # Joints
    "Joint2D",
    "PinJoint2D",
    "DampedSpringJoint2D",
    "GrooveJoint2D",
    "MotorJoint2D",
    
    # Skeleton
    "Skeleton2D",
    "Bone2D",
    
    # Audio
    "AudioStreamPlayer2D",
    "AudioListener2D",
    
    # Navigation
    "NavigationRegion2D",
    "NavigationAgent2D",
    "NavigationObstacle2D",
    
    # UI
    "TouchScreenButton",
]
