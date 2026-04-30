# /**************************************************************************/
# /*  physics_controller.py                                                 */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Native physics controller for engine."""

from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass

@dataclass
class PhysicsBody:
    """Physics body data."""
    node_id: str
    mass: float = 1.0
    velocity: Tuple[float, float] = (0.0, 0.0)
    acceleration: Tuple[float, float] = (0.0, 0.0)
    is_static: bool = False
    is_kinematic: bool = False
    friction: float = 0.5
    restitution: float = 0.5


@dataclass
class CollisionShape:
    """Collision shape data."""
    body_id: str
    shape_type: str  # "box", "circle", "polygon"
    dimensions: Tuple[float, ...] = (1.0, 1.0)  # width, height or radius
    offset: Tuple[float, float] = (0.0, 0.0)


class PhysicsController:
    """Native engine physics controller for managing game physics."""

    def __init__(self):
        self._bodies: Dict[str, PhysicsBody] = {}
        self._shapes: Dict[str, CollisionShape] = {}
        self._gravity: Tuple[float, float] = (0.0, 9.8)
        self._time_scale: float = 1.0
        self._collision_pairs: List[Tuple[str, str]] = []

    def add_body(self, node_id: str, mass: float = 1.0, is_static: bool = False) -> PhysicsBody:
        """Add a physics body to the simulation."""
        body = PhysicsBody(
            node_id=node_id,
            mass=mass,
            is_static=is_static
        )
        self._bodies[node_id] = body
        return body

    def remove_body(self, node_id: str) -> bool:
        """Remove a physics body from the simulation."""
        if node_id in self._bodies:
            del self._bodies[node_id]
            return True
        return False

    def add_shape(self, node_id: str, shape_type: str, dimensions: Tuple[float, ...]) -> CollisionShape:
        """Add a collision shape to a body."""
        shape = CollisionShape(
            body_id=node_id,
            shape_type=shape_type,
            dimensions=dimensions
        )
        self._shapes[node_id] = shape
        return shape

    def set_gravity(self, x: float, y: float) -> None:
        """Set global gravity."""
        self._gravity = (x, y)

    def get_gravity(self) -> Tuple[float, float]:
        """Get current gravity."""
        return self._gravity

    def set_time_scale(self, scale: float) -> None:
        """Set physics time scale."""
        self._time_scale = max(0.0, scale)

    def get_time_scale(self) -> float:
        """Get current time scale."""
        return self._time_scale

    def apply_force(self, node_id: str, force_x: float, force_y: float) -> bool:
        """Apply force to a body."""
        if node_id not in self._bodies:
            return False

        body = self._bodies[node_id]
        if body.is_static:
            return False

        # F = ma → a = F/m
        ax = force_x / body.mass
        ay = force_y / body.mass
        body.acceleration = (ax, ay)

        return True

    def set_velocity(self, node_id: str, vx: float, vy: float) -> bool:
        """Set velocity of a body."""
        if node_id not in self._bodies:
            return False

        body = self._bodies[node_id]
        body.velocity = (vx, vy)
        return True

    def get_velocity(self, node_id: str) -> Optional[Tuple[float, float]]:
        """Get velocity of a body."""
        if node_id in self._bodies:
            return self._bodies[node_id].velocity
        return None

    def update(self, delta_time: float) -> None:
        """Update physics simulation."""
        dt = delta_time * self._time_scale

        for body in self._bodies.values():
            if body.is_static or body.is_kinematic:
                continue

            # Apply gravity
            ax, ay = body.acceleration
            ax += self._gravity[0]
            ay += self._gravity[1]

            # Update velocity: v = v + a * dt
            vx, vy = body.velocity
            vx += ax * dt
            vy += ay * dt
            body.velocity = (vx, vy)

            # Reset acceleration
            body.acceleration = (0.0, 0.0)

    def check_collisions(self) -> List[Tuple[str, str]]:
        """Check for collisions between bodies."""
        self._collision_pairs.clear()

        # Simple AABB collision detection
        body_ids = list(self._bodies.keys())
        for i in range(len(body_ids)):
            for j in range(i + 1, len(body_ids)):
                id1, id2 = body_ids[i], body_ids[j]

                if self._check_collision(id1, id2):
                    self._collision_pairs.append((id1, id2))

        return self._collision_pairs.copy()

    def _check_collision(self, id1: str, id2: str) -> bool:
        """Check collision between two bodies."""
        # Simplified collision check - in real implementation would use proper physics engine
        return False

    def get_body(self, node_id: str) -> Optional[PhysicsBody]:
        """Get a physics body by node ID."""
        return self._bodies.get(node_id)

    def get_shape(self, node_id: str) -> Optional[CollisionShape]:
        """Get a collision shape by node ID."""
        return self._shapes.get(node_id)
