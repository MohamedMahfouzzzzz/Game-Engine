# /**************************************************************************/
# /*  physics_world.py                                                      */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Physics world for managing 2D physics simulation."""

from typing import List, Optional, Set, Tuple
from dataclasses import dataclass

from engine.physics.body2d import RigidBody2D, StaticBody2D, KinematicBody2D

import logging

logger = logging.getLogger(__name__)


@dataclass
class PhysicsConfig:
    """Configuration for physics simulation."""
    gravity: Tuple[float, float] = (0.0, -9.8)
    time_step: float = 1.0 / 60.0
    velocity_iterations: int = 8
    position_iterations: int = 3
    max_bodies: int = 1000


class PhysicsWorld:
    """Manages all physics bodies and simulation."""

    def __init__(self, config: Optional[PhysicsConfig] = None):
        self.config = config or PhysicsConfig()
        self.bodies: List[RigidBody2D] = []
        self.static_bodies: List[StaticBody2D] = []
        self.kinematic_bodies: List[KinematicBody2D] = []
        self.areas: List["Area2D"] = []

        self._paused = False
        self._time_accumulator = 0.0

    def add_body(self, body: RigidBody2D) -> None:
        """Add a rigid body to the world."""
        if len(self.bodies) < self.config.max_bodies:
            self.bodies.append(body)
            body._world = self

    def remove_body(self, body: RigidBody2D) -> None:
        """Remove a body from the world."""
        if body in self.bodies:
            self.bodies.remove(body)
            body._world = None

    def add_static_body(self, body: StaticBody2D) -> None:
        """Add a static body (walls, ground, etc)."""
        self.static_bodies.append(body)
        body._world = self

    def add_kinematic_body(self, body: KinematicBody2D) -> None:
        """Add a kinematic body (moving platforms, etc)."""
        self.kinematic_bodies.append(body)
        body._world = self

    def add_area(self, area: "Area2D") -> None:
        """Add an area for collision detection."""
        self.areas.append(area)
        area._world = self

    def step(self, delta_time: float) -> None:
        """Advance physics simulation by one step."""
        if self._paused:
            return

        self._time_accumulator += delta_time

        while self._time_accumulator >= self.config.time_step:
            self._simulate_step()
            self._time_accumulator -= self.config.time_step

    def _simulate_step(self) -> None:
        """Run one physics step."""
        # Apply gravity
        for body in self.bodies:
            if body.gravity_scale > 0 and not body.sleeping:
                body.apply_force(
                    self.config.gravity[0] * body.mass * body.gravity_scale,
                    self.config.gravity[1] * body.mass * body.gravity_scale
                )

        # Integrate velocities
        for body in self.bodies:
            body._integrate_velocity(self.config.time_step)

        # Detect and resolve collisions
        collisions = self._detect_collisions()
        self._resolve_collisions(collisions)

        # Update kinematic bodies
        for body in self.kinematic_bodies:
            body._update(self.config.time_step)

        # Check area overlaps
        self._update_areas()

        # Update transforms
        for body in self.bodies:
            body._update_transform()

    def _detect_collisions(self) -> List[Tuple[RigidBody2D, "CollisionShape2D", RigidBody2D, "CollisionShape2D"]]:
        """Detect all collisions between bodies."""
        collisions = []

        # Check body vs body
        for i, body_a in enumerate(self.bodies):
            for body_b in self.bodies[i+1:]:
                for shape_a in body_a.shapes:
                    for shape_b in body_b.shapes:
                        if shape_a.intersects(shape_b):
                            collisions.append((body_a, shape_a, body_b, shape_b))

        # Check body vs static
        for body in self.bodies:
            for static in self.static_bodies:
                for shape_a in body.shapes:
                    for shape_b in static.shapes:
                        if shape_a.intersects(shape_b):
                            collisions.append((body, shape_a, static, shape_b))

        return collisions

    def _resolve_collisions(
        self,
        collisions: List[Tuple[RigidBody2D, "CollisionShape2D", RigidBody2D, "CollisionShape2D"]]
    ) -> None:
        """Resolve detected collisions."""
        for body_a, shape_a, body_b, shape_b in collisions:
            # Calculate collision response
            if hasattr(body_b, "velocity"):  # RigidBody2D
                # Elastic collision response
                self._resolve_body_collision(body_a, body_b)
            else:  # StaticBody2D
                self._resolve_static_collision(body_a, body_b)

            # Emit collision events
            body_a._on_collision(body_b)
            if hasattr(body_b, "_on_collision"):
                body_b._on_collision(body_a)

    def _resolve_body_collision(self, body_a: RigidBody2D, body_b: RigidBody2D) -> None:
        """Resolve collision between two rigid bodies."""
        # Simple elastic collision
        v1 = body_a.velocity
        v2 = body_b.velocity
        m1 = body_a.mass
        m2 = body_b.mass

        # Conservation of momentum
        new_v1 = ((m1 - m2) * v1 + 2 * m2 * v2) / (m1 + m2)
        new_v2 = ((m2 - m1) * v2 + 2 * m1 * v1) / (m1 + m2)

        body_a.velocity = new_v1
        body_b.velocity = new_v2

    def _resolve_static_collision(self, body: RigidBody2D, static: StaticBody2D) -> None:
        """Resolve collision with static body (bounce)."""
        body.velocity = (-body.velocity[0] * body.bounce, -body.velocity[1] * body.bounce)

    def _update_areas(self) -> None:
        """Update area overlaps."""
        for area in self.areas:
            overlapping: Set[RigidBody2D] = set()

            for body in self.bodies:
                if area.overlaps_body(body):
                    overlapping.add(body)

            area._update_overlaps(overlapping)

    def query_point(self, x: float, y: float) -> List[RigidBody2D]:
        """Query which bodies overlap a point."""
        results = []
        for body in self.bodies:
            if body.contains_point(x, y):
                results.append(body)
        return results

    def query_rect(self, x: float, y: float, width: float, height: float) -> List[RigidBody2D]:
        """Query which bodies overlap a rectangle."""
        results = []
        for body in self.bodies:
            if body.intersects_rect(x, y, width, height):
                results.append(body)
        return results

    def raycast(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
        ignore_bodies: Optional[List[RigidBody2D]] = None
    ) -> Optional[Tuple[RigidBody2D, float]]:
        """Cast a ray and return first hit."""
        ignore = set(ignore_bodies or [])

        closest_hit = None
        closest_fraction = 1.0

        for body in self.bodies:
            if body in ignore:
                continue

            hit = body.raycast(start, end)
            if hit is not None and hit < closest_fraction:
                closest_fraction = hit
                closest_hit = body

        return (closest_hit, closest_fraction) if closest_hit else None

    def pause(self) -> None:
        """Pause physics simulation."""
        self._paused = True

    def resume(self) -> None:
        """Resume physics simulation."""
        self._paused = False

    def clear(self) -> None:
        """Remove all bodies from world."""
        self.bodies.clear()
        self.static_bodies.clear()
        self.kinematic_bodies.clear()
        self.areas.clear()
