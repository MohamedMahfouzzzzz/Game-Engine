# /**************************************************************************/
# /*  collision_shape.py                                                    */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Collision shapes for physics bodies."""

import math
from typing import Optional, Tuple, List
from dataclasses import dataclass

import logging

logger = logging.getLogger(__name__)


@dataclass
class AABB:
    """Axis-aligned bounding box."""
    min_x: float
    min_y: float
    max_x: float
    max_y: float


class CollisionShape2D:
    """Base class for collision shapes."""

    def __init__(self):
        self.body: Optional["PhysicsBody2D"] = None
        self.offset: Tuple[float, float] = (0.0, 0.0)
        self._disabled: bool = False

    def get_aabb(self) -> AABB:
        """Get axis-aligned bounding box."""
        raise NotImplementedError

    def contains_point(self, x: float, y: float) -> bool:
        """Check if point is inside shape."""
        raise NotImplementedError

    def intersects(self, other: "CollisionShape2D") -> bool:
        """Check if this shape intersects another."""
        # Quick AABB rejection
        aabb1 = self.get_aabb()
        aabb2 = other.get_aabb()

        if (aabb1.max_x < aabb2.min_x or aabb1.min_x > aabb2.max_x or
            aabb1.max_y < aabb2.min_y or aabb1.min_y > aabb2.max_y):
            return False

        # Detailed intersection check
        return self._intersects_detailed(other)

    def _intersects_detailed(self, other: "CollisionShape2D") -> bool:
        """Detailed intersection check. Override in subclasses."""
        return True  # Conservative default

    def intersects_rect(self, x: float, y: float, width: float, height: float) -> bool:
        """Check if shape intersects rectangle."""
        raise NotImplementedError

    def raycast(self, start: Tuple[float, float], end: Tuple[float, float]) -> Optional[float]:
        """Cast ray against shape. Returns hit fraction or None."""
        raise NotImplementedError

    @property
    def disabled(self) -> bool:
        return self._disabled

    def set_disabled(self, disabled: bool) -> None:
        self._disabled = disabled


class RectangleShape(CollisionShape2D):
    """Rectangle collision shape."""

    def __init__(self, width: float = 32.0, height: float = 32.0):
        super().__init__()
        self.size: Tuple[float, float] = (width, height)

    def get_aabb(self) -> AABB:
        """Get axis-aligned bounding box."""
        if self.body:
            pos = self.body.get_position()
            ox, oy = self.offset
            hw, hh = self.size[0] / 2, self.size[1] / 2
            return AABB(
                pos[0] + ox - hw,
                pos[1] + oy - hh,
                pos[0] + ox + hw,
                pos[1] + oy + hh
            )
        return AABB(0, 0, self.size[0], self.size[1])

    def contains_point(self, x: float, y: float) -> bool:
        """Check if point is inside rectangle."""
        if not self.body:
            return False

        aabb = self.get_aabb()
        return aabb.min_x <= x <= aabb.max_x and aabb.min_y <= y <= aabb.max_y

    def _intersects_detailed(self, other: "CollisionShape2D") -> bool:
        """Detailed intersection with another shape."""
        if isinstance(other, RectangleShape):
            return self._intersects_rectangle(other)
        elif isinstance(other, CircleShape):
            return other._intersects_rectangle(self)
        return True  # Conservative for unknown types

    def _intersects_rectangle(self, other: "RectangleShape") -> bool:
        """Rectangle-rectangle intersection."""
        aabb1 = self.get_aabb()
        aabb2 = other.get_aabb()
        return not (
            aabb1.max_x < aabb2.min_x or aabb1.min_x > aabb2.max_x or
            aabb1.max_y < aabb2.min_y or aabb1.min_y > aabb2.max_y
        )

    def intersects_rect(self, x: float, y: float, width: float, height: float) -> bool:
        """Check if intersects with rectangle."""
        aabb = self.get_aabb()
        return not (
            aabb.max_x < x or aabb.min_x > x + width or
            aabb.max_y < y or aabb.min_y > y + height
        )

    def raycast(self, start: Tuple[float, float], end: Tuple[float, float]) -> Optional[float]:
        """Cast ray against rectangle."""
        aabb = self.get_aabb()
        x1, y1 = start
        x2, y2 = end
        dx = x2 - x1
        dy = y2 - y1

        # Handle zero-length ray
        if dx == 0 and dy == 0:
            return 0.0 if self.contains_point(x1, y1) else None

        tmin = 0.0
        tmax = 1.0

        # Check X
        if dx != 0:
            tx1 = (aabb.min_x - x1) / dx
            tx2 = (aabb.max_x - x1) / dx
            tmin = max(tmin, min(tx1, tx2))
            tmax = min(tmax, max(tx1, tx2))
        elif x1 < aabb.min_x or x1 > aabb.max_x:
            return None

        # Check Y
        if dy != 0:
            ty1 = (aabb.min_y - y1) / dy
            ty2 = (aabb.max_y - y1) / dy
            tmin = max(tmin, min(ty1, ty2))
            tmax = min(tmax, max(ty1, ty2))
        elif y1 < aabb.min_y or y1 > aabb.max_y:
            return None

        if tmin <= tmax:
            return tmin if tmin >= 0 else None
        return None


class CircleShape(CollisionShape2D):
    """Circle collision shape."""

    def __init__(self, radius: float = 16.0):
        super().__init__()
        self.radius: float = radius

    def get_aabb(self) -> AABB:
        """Get axis-aligned bounding box."""
        if self.body:
            pos = self.body.get_position()
            ox, oy = self.offset
            return AABB(
                pos[0] + ox - self.radius,
                pos[1] + oy - self.radius,
                pos[0] + ox + self.radius,
                pos[1] + oy + self.radius
            )
        return AABB(-self.radius, -self.radius, self.radius, self.radius)

    def contains_point(self, x: float, y: float) -> bool:
        """Check if point is inside circle."""
        if not self.body:
            return False

        center = self.body.get_position()
        ox, oy = self.offset
        cx, cy = center[0] + ox, center[1] + oy

        dx = x - cx
        dy = y - cy
        return dx * dx + dy * dy <= self.radius * self.radius

    def _intersects_detailed(self, other: "CollisionShape2D") -> bool:
        """Detailed intersection with another shape."""
        if isinstance(other, CircleShape):
            return self._intersects_circle(other)
        elif isinstance(other, RectangleShape):
            return self._intersects_rectangle(other)
        return True

    def _intersects_circle(self, other: "CircleShape") -> bool:
        """Circle-circle intersection."""
        if not self.body or not other.body:
            return False

        pos1 = self.body.get_position()
        pos2 = other.body.get_position()
        ox1, oy1 = self.offset
        ox2, oy2 = other.offset

        dx = (pos1[0] + ox1) - (pos2[0] + ox2)
        dy = (pos1[1] + oy1) - (pos2[1] + oy2)
        distance_sq = dx * dx + dy * dy
        radius_sum = self.radius + other.radius

        return distance_sq <= radius_sum * radius_sum

    def _intersects_rectangle(self, rect: RectangleShape) -> bool:
        """Circle-rectangle intersection."""
        if not self.body:
            return False

        center = self.body.get_position()
        ox, oy = self.offset
        cx, cy = center[0] + ox, center[1] + oy

        aabb = rect.get_aabb()

        # Find closest point on rectangle to circle center
        closest_x = max(aabb.min_x, min(cx, aabb.max_x))
        closest_y = max(aabb.min_y, min(cy, aabb.max_y))

        dx = cx - closest_x
        dy = cy - closest_y
        return dx * dx + dy * dy <= self.radius * self.radius

    def intersects_rect(self, x: float, y: float, width: float, height: float) -> bool:
        """Check if intersects with rectangle."""
        if not self.body:
            return False

        center = self.body.get_position()
        ox, oy = self.offset
        cx, cy = center[0] + ox, center[1] + oy

        closest_x = max(x, min(cx, x + width))
        closest_y = max(y, min(cy, y + height))

        dx = cx - closest_x
        dy = cy - closest_y
        return dx * dx + dy * dy <= self.radius * self.radius

    def raycast(self, start: Tuple[float, float], end: Tuple[float, float]) -> Optional[float]:
        """Cast ray against circle."""
        if not self.body:
            return None

        center = self.body.get_position()
        ox, oy = self.offset
        cx, cy = center[0] + ox, center[1] + oy

        x1, y1 = start
        x2, y2 = end
        dx = x2 - x1
        dy = y2 - y1

        # Vector from ray start to circle center
        fx = cx - x1
        fy = cy - y1

        # Project onto ray direction
        dot = fx * dx + fy * dy
        if dot < 0:
            return None  # Circle behind ray

        # Closest point on ray to circle center
        ray_len_sq = dx * dx + dy * dy
        if ray_len_sq == 0:
            return 0.0 if math.hypot(fx, fy) <= self.radius else None

        t = dot / ray_len_sq
        closest_x = x1 + dx * t
        closest_y = y1 + dy * t

        # Distance from closest point to circle center
        dist_sq = (cx - closest_x) ** 2 + (cy - closest_y) ** 2

        if dist_sq > self.radius * self.radius:
            return None  # Ray misses circle

        # Calculate entry and exit points
        offset = math.sqrt(self.radius * self.radius - dist_sq) / math.sqrt(ray_len_sq)
        t1 = t - offset
        t2 = t + offset

        # Return closest hit in [0, 1]
        if 0 <= t1 <= 1:
            return t1
        if 0 <= t2 <= 1:
            return t2
        return None


class PolygonShape(CollisionShape2D):
    """Polygon collision shape."""

    def __init__(self, points: List[Tuple[float, float]] = None):
        super().__init__()
        self.points: List[Tuple[float, float]] = points or []

    def get_aabb(self) -> AABB:
        """Get axis-aligned bounding box."""
        if not self.points:
            return AABB(0, 0, 0, 0)

        if self.body:
            pos = self.body.get_position()
            ox, oy = self.offset
            transformed = [(p[0] + pos[0] + ox, p[1] + pos[1] + oy) for p in self.points]
        else:
            transformed = self.points

        xs = [p[0] for p in transformed]
        ys = [p[1] for p in transformed]
        return AABB(min(xs), min(ys), max(xs), max(ys))

    def contains_point(self, x: float, y: float) -> bool:
        """Check if point is inside polygon using ray casting."""
        if not self.points or not self.body:
            return False

        pos = self.body.get_position()
        ox, oy = self.offset

        # Transform point to local space
        lx = x - pos[0] - ox
        ly = y - pos[1] - oy

        # Ray casting algorithm
        n = len(self.points)
        inside = False
        j = n - 1

        for i in range(n):
            xi, yi = self.points[i]
            xj, yj = self.points[j]

            if ((yi > ly) != (yj > ly)) and (lx < (xj - xi) * (ly - yi) / (yj - yi) + xi):
                inside = not inside
            j = i

        return inside

    def _intersects_detailed(self, other: "CollisionShape2D") -> bool:
        """Detailed intersection check."""
        # Simplified - use AABB for now
        aabb1 = self.get_aabb()
        aabb2 = other.get_aabb()
        return not (
            aabb1.max_x < aabb2.min_x or aabb1.min_x > aabb2.max_x or
            aabb1.max_y < aabb2.min_y or aabb1.min_y > aabb2.max_y
        )

    def intersects_rect(self, x: float, y: float, width: float, height: float) -> bool:
        """Check if intersects with rectangle."""
        aabb = self.get_aabb()
        return not (
            aabb.max_x < x or aabb.min_x > x + width or
            aabb.max_y < y or aabb.min_y > y + height
        )

    def raycast(self, start: Tuple[float, float], end: Tuple[float, float]) -> Optional[float]:
        """Cast ray against polygon."""
        if not self.points or not self.body:
            return None

        pos = self.body.get_position()
        ox, oy = self.offset

        x1, y1 = start
        x2, y2 = end
        dx = x2 - x1
        dy = y2 - y1

        closest_t = None
        n = len(self.points)

        for i in range(n):
            x3, y3 = self.points[i]
            x4, y4 = self.points[(i + 1) % n]

            # Transform to world space
            x3 += pos[0] + ox
            y3 += pos[1] + oy
            x4 += pos[0] + ox
            y4 += pos[1] + oy

            # Line segment intersection
            denom = (y4 - y3) * dx - (x4 - x3) * dy
            if denom == 0:
                continue  # Parallel

            ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denom
            ub = (dx * (y1 - y3) - dy * (x1 - x3)) / denom

            if 0 <= ua <= 1 and 0 <= ub <= 1:
                if closest_t is None or ua < closest_t:
                    closest_t = ua

        return closest_t
