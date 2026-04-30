# /**************************************************************************/
# /*  body2d.py                                                             */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Physics body types for 2D physics simulation."""

from typing import List, Optional, Tuple, Callable
from dataclasses import dataclass
from engine.core.node_base import Node2D
from engine.core.types import NodeType

import logging

logger = logging.getLogger(__name__)


class PhysicsBody2D(Node2D):
    """Base class for all physics bodies."""

    def __init__(self, name: str = "PhysicsBody2D"):
        super().__init__(name)
        self.shapes: List["CollisionShape2D"] = []
        self._world: Optional["PhysicsWorld"] = None
        self._collision_callback: Optional[Callable[["PhysicsBody2D"], None]] = None

    def add_shape(self, shape: "CollisionShape2D") -> None:
        """Add a collision shape."""
        self.shapes.append(shape)
        shape.body = self

    def remove_shape(self, shape: "CollisionShape2D") -> None:
        """Remove a collision shape."""
        if shape in self.shapes:
            self.shapes.remove(shape)
            shape.body = None

    def contains_point(self, x: float, y: float) -> bool:
        """Check if point is inside any shape."""
        for shape in self.shapes:
            if shape.contains_point(x, y):
                return True
        return False

    def intersects_rect(self, x: float, y: float, width: float, height: float) -> bool:
        """Check if body intersects rectangle."""
        for shape in self.shapes:
            if shape.intersects_rect(x, y, width, height):
                return True
        return False

    def raycast(self, start: Tuple[float, float], end: Tuple[float, float]) -> Optional[float]:
        """Cast ray against body shapes. Returns hit fraction or None."""
        closest = None
        for shape in self.shapes:
            hit = shape.raycast(start, end)
            if hit is not None and (closest is None or hit < closest):
                closest = hit
        return closest

    def connect_collision(self, callback: Callable[["PhysicsBody2D"], None]) -> None:
        """Connect collision event callback."""
        self._collision_callback = callback

    def _on_collision(self, other: "PhysicsBody2D") -> None:
        """Called when collision occurs."""
        if self._collision_callback:
            self._collision_callback(other)


class RigidBody2D(PhysicsBody2D):
    """Dynamic physics body affected by forces."""

    def __init__(self, name: str = "RigidBody2D"):
        super().__init__(name)
        self.node_type = NodeType.RIGIDBODY2D

        # Physics properties
        self.mass: float = 1.0
        self.velocity: Tuple[float, float] = (0.0, 0.0)
        self.angular_velocity: float = 0.0
        self.force: Tuple[float, float] = (0.0, 0.0)
        self.torque: float = 0.0

        # Material properties
        self.friction: float = 0.5
        self.bounce: float = 0.0
        self.gravity_scale: float = 1.0
        self.linear_damping: float = 0.0
        self.angular_damping: float = 0.0

        # State
        self.sleeping: bool = False
        self.can_sleep: bool = True
        self.fixed_rotation: bool = False

    def apply_force(self, fx: float, fy: float) -> None:
        """Apply force to body."""
        self.force = (self.force[0] + fx, self.force[1] + fy)

    def apply_impulse(self, ix: float, iy: float) -> None:
        """Apply instant impulse (changes velocity directly)."""
        self.velocity = (
            self.velocity[0] + ix / self.mass,
            self.velocity[1] + iy / self.mass
        )

    def apply_torque(self, torque: float) -> None:
        """Apply rotational force."""
        self.torque += torque

    def set_linear_velocity(self, vx: float, vy: float) -> None:
        """Set linear velocity directly."""
        self.velocity = (vx, vy)

    def get_linear_velocity(self) -> Tuple[float, float]:
        """Get current linear velocity."""
        return self.velocity

    def set_angular_velocity(self, omega: float) -> None:
        """Set angular velocity."""
        self.angular_velocity = omega

    def _integrate_velocity(self, dt: float) -> None:
        """Integrate velocity into position (internal use)."""
        if self.sleeping:
            return

        # Linear movement
        ax = self.force[0] / self.mass if self.mass > 0 else 0
        ay = self.force[1] / self.mass if self.mass > 0 else 0

        self.velocity = (
            (self.velocity[0] + ax * dt) * (1 - self.linear_damping * dt),
            (self.velocity[1] + ay * dt) * (1 - self.linear_damping * dt)
        )

        # Angular movement
        self.angular_velocity += (self.torque / self.mass) * dt
        self.angular_velocity *= (1 - self.angular_damping * dt)

        # Clear forces
        self.force = (0.0, 0.0)
        self.torque = 0.0

    def _update_transform(self) -> None:
        """Update transform from physics state."""
        if self.sleeping:
            return

        # Update position
        pos = self.get_position()
        self.set_position(
            pos[0] + self.velocity[0] * (1/60),  # Assuming 60fps
            pos[1] + self.velocity[1] * (1/60)
        )

        # Update rotation
        if not self.fixed_rotation:
            rot = self.get_rotation()
            self.set_rotation(rot + self.angular_velocity * (1/60))

    def put_to_sleep(self) -> None:
        """Put body to sleep (stop simulation)."""
        if self.can_sleep:
            self.sleeping = True
            self.velocity = (0.0, 0.0)
            self.angular_velocity = 0.0

    def wake_up(self) -> None:
        """Wake up body for simulation."""
        self.sleeping = False


class StaticBody2D(PhysicsBody2D):
    """Static body that doesn't move (walls, ground)."""

    def __init__(self, name: str = "StaticBody2D"):
        super().__init__(name)
        self.node_type = NodeType.STATICBODY2D
        self.bounce: float = 0.0
        self.friction: float = 1.0


class KinematicBody2D(PhysicsBody2D):
    """Body moved by code, not physics simulation."""

    def __init__(self, name: str = "KinematicBody2D"):
        super().__init__(name)
        self.node_type = NodeType.KINEMATICBODY2D
        self.velocity: Tuple[float, float] = (0.0, 0.0)
        self.sync_to_physics: bool = True

    def move_and_collide(self, velocity: Tuple[float, float]) -> Optional["CollisionResult"]:
        """Move body and detect collisions."""
        # This would integrate with the physics world for collision detection
        self.velocity = velocity
        # Placeholder - actual implementation needs physics world reference
        return None

    def move_and_slide(self, velocity: Tuple[float, float]) -> Tuple[float, float]:
        """Move body with sliding along surfaces."""
        # Placeholder implementation
        pos = self.get_position()
        self.set_position(pos[0] + velocity[0], pos[1] + velocity[1])
        return velocity

    def _update(self, dt: float) -> None:
        """Update kinematic body (internal)."""
        if self.sync_to_physics:
            pos = self.get_position()
            self.set_position(
                pos[0] + self.velocity[0] * dt,
                pos[1] + self.velocity[1] * dt
            )


@dataclass
class CollisionResult:
    """Result of a collision check."""
    body: PhysicsBody2D
    position: Tuple[float, float]
    normal: Tuple[float, float]
    penetration: float
