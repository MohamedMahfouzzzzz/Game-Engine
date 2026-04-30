# /**************************************************************************/
# /*  __init__.py                                                           */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Physics system for 2D games."""

from engine.physics.physics_world import PhysicsWorld
from engine.physics.body2d import RigidBody2D, StaticBody2D, KinematicBody2D
from engine.physics.collision_shape import CollisionShape2D, RectangleShape, CircleShape
from engine.physics.area2d import Area2D

import logging


logger = logging.getLogger(__name__)


__all__ = [
    "PhysicsWorld",
    "RigidBody2D",
    "StaticBody2D",
    "KinematicBody2D",
    "CollisionShape2D",
    "RectangleShape",
    "CircleShape",
    "Area2D",
]
