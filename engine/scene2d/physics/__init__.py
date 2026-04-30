# /**************************************************************************/
# /*  __init__.py                                                           */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""2D physics nodes and collision shapes."""

from engine.scene2d.physics.physics_body import PhysicsBody2D
from engine.scene2d.physics.static_body import StaticBody2D, AnimatableBody2D
from engine.scene2d.physics.rigid_body import RigidBody2D, RigidBody2DMode
from engine.scene2d.physics.character_body import CharacterBody2D
from engine.scene2d.physics.collision_shape import (
    CollisionShape2D,
    Shape2D, WorldBoundaryShape2D, SeparationRayShape2D,
    SegmentShape2D, CircleShape2D, RectangleShape2D, CapsuleShape2D
)
from engine.scene2d.physics.collision_polygon import CollisionPolygon2D

__all__ = [
    # Bodies
    "PhysicsBody2D",
    "StaticBody2D",
    "AnimatableBody2D",
    "RigidBody2D",
    "RigidBody2DMode",
    "CharacterBody2D",
    # Shapes
    "CollisionShape2D",
    "Shape2D",
    "WorldBoundaryShape2D",
    "SeparationRayShape2D",
    "SegmentShape2D",
    "CircleShape2D",
    "RectangleShape2D",
    "CapsuleShape2D",
    "CollisionPolygon2D",
]
