# /**************************************************************************/
# /*  nodes2d.py                                                            */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Godot-inspired 2D Node Hierarchy

Core 2D nodes:
- Node2D: Base transform class
- Sprite2D: Texture rendering
- CharacterBody2D: Kinematic physics body
- Area2D: Detection and influence zones
- Camera2D: Viewport control
- CanvasLayer: Layered rendering
"""

from __future__ import annotations

import math
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Optional, List, Set, Dict, Any, Callable
from pathlib import Path

from engine.core.node_base import Node
from engine.core.types import NodeType
from engine.core.transform import Transform2D
from engine.core.signals import SignalBus
from engine.core.uid_registry import generate_uid

import logging


logger = logging.getLogger(__name__)



# =============================================================================
# Vector2 Helper
# =============================================================================

class Vector2:
    """2D vector with math operations."""
    
    def __init__(self, x: float = 0, y: float = 0):
        self.x = float(x)
        self.y = float(y)
    
    def __add__(self, other: Vector2) -> Vector2:
        return Vector2(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: Vector2) -> Vector2:
        return Vector2(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar: float) -> Vector2:
        return Vector2(self.x * scalar, self.y * scalar)
    
    def __truediv__(self, scalar: float) -> Vector2:
        return Vector2(self.x / scalar, self.y / scalar)
    
    def dot(self, other: Vector2) -> float:
        return self.x * other.x + self.y * other.y
    
    def length(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y)
    
    def normalized(self) -> Vector2:
        length = self.length()
        if length == 0:
            return Vector2(0, 0)
        return Vector2(self.x / length, self.y / length)
    
    def angle(self) -> float:
        return math.atan2(self.y, self.x)
    
    def slide(self, normal: Vector2) -> Vector2:
        """Slide vector along a normal (remove component into surface)."""
        return self - normal * self.dot(normal)
    
    def lerp(self, target: Vector2, t: float) -> Vector2:
        """Linear interpolate toward target."""
        return Vector2(
            self.x + (target.x - self.x) * t,
            self.y + (target.y - self.y) * t
        )
    
    def copy(self) -> Vector2:
        return Vector2(self.x, self.y)
    
    def __repr__(self) -> str:
        return f"Vector2({self.x:.2f}, {self.y:.2f})"


# =============================================================================
# Color Helper
# =============================================================================

class Color:
    """RGBA color."""
    
    def __init__(self, r: float = 1.0, g: float = 1.0, b: float = 1.0, a: float = 1.0):
        self.r = max(0.0, min(1.0, r))
        self.g = max(0.0, min(1.0, g))
        self.b = max(0.0, min(1.0, b))
        self.a = max(0.0, min(1.0, a))
    
    def to_ints(self) -> tuple:
        """Convert to 0-255 integers."""
        return (
            int(self.r * 255),
            int(self.g * 255),
            int(self.b * 255),
            int(self.a * 255)
        )
    
    @classmethod
    def from_ints(cls, r: int, g: int, b: int, a: int = 255) -> Color:
        return cls(r / 255, g / 255, b / 255, a / 255)
    
    @classmethod
    def white(cls) -> Color:
        return cls(1, 1, 1, 1)
    
    @classmethod
    def black(cls) -> Color:
        return cls(0, 0, 0, 1)
    
    @classmethod
    def red(cls) -> Color:
        return cls(1, 0, 0, 1)
    
    @classmethod
    def green(cls) -> Color:
        return cls(0, 1, 0, 1)
    
    @classmethod
    def blue(cls) -> Color:
        return cls(0, 0, 1, 1)
    
    @classmethod
    def transparent(cls) -> Color:
        return cls(0, 0, 0, 0)


# =============================================================================
# Texture Resource
# =============================================================================

class Texture2D:
    """2D texture reference."""
    
    def __init__(self, path: str = "", width: int = 0, height: int = 0):
        self.path = path
        self.width = width
        self.height = height
        self._loaded = False
    
    def load(self) -> bool:
        """Load texture from disk."""
        if not self.path or not Path(self.path).exists():
            return False
        # Actual loading would happen here
        self._loaded = True
        return True
    
    def is_loaded(self) -> bool:
        return self._loaded


# =============================================================================
# Base Node2D
# =============================================================================

class Node2D(Node):
    """Base class for all 2D game objects with transform support.
    
    Properties:
        position: Local position relative to parent (Vector2)
        rotation: Rotation in degrees (float)
        scale: Scale factors (Vector2)
        z_index: Draw order, higher = on top (int)
        z_relative: If True, z_index is relative to parent (bool)
        visible: If False, skip rendering (bool)
        modulate: Color tint applied to this and children (Color)
        self_modulate: Color tint applied only to this node (Color)
    
    Signals:
        transform_changed: Emitted when position/rotation/scale changes
        visibility_changed: Emitted when visibility toggles
    """
    
    # Additional slots for 2D properties
    __slots__ = [
        "_position", "_rotation", "_scale",
        "z_index", "z_relative", 
        "visible", 
        "modulate", "self_modulate",
        "_transform", "_global_transform", "_transform_dirty"
    ]
    
    # Built-in signals (class-level declaration)
    _SIGNALS = ["transform_changed", "visibility_changed", "z_index_changed"]
    
    def __init__(self, name: str = "Node2D"):
        super().__init__(name, NodeType.NODE2D)
        
        # Transform properties
        self._position = Vector2(0, 0)
        self._rotation = 0.0  # Degrees
        self._scale = Vector2(1, 1)
        
        # Rendering properties
        self.z_index = 0
        self.z_relative = False
        self.visible = True
        self.modulate = Color.white()
        self.self_modulate = Color.white()
        
        # Cached transforms
        self._transform = Transform2D()
        self._global_transform: Optional[Transform2D] = None
        self._transform_dirty = True
        
        self._update_transform_matrix()
    
    # === Position Property ===
    @property
    def position(self) -> Vector2:
        return self._position.copy()
    
    @position.setter
    def position(self, value: Vector2) -> None:
        self._position = value.copy() if hasattr(value, 'copy') else Vector2(value[0], value[1])
        self._mark_transform_dirty()
    
    # === Rotation Property ===
    @property
    def rotation(self) -> float:
        return self._rotation
    
    @rotation.setter
    def rotation(self, value: float) -> None:
        self._rotation = value
        self._mark_transform_dirty()
    
    # === Scale Property ===
    @property
    def scale(self) -> Vector2:
        return self._scale.copy()
    
    @scale.setter
    def scale(self, value: Vector2) -> None:
        self._scale = value.copy() if hasattr(value, 'copy') else Vector2(value[0], value[1])
        self._mark_transform_dirty()
    
    # === Transform Methods ===
    def _mark_transform_dirty(self) -> None:
        """Mark transform as needing recalculation."""
        self._transform_dirty = True
        self._global_transform = None
        self.signals.emit("transform_changed")
        
        # Propagate to children (their global transforms depend on us)
        for child in self.children:
            if isinstance(child, Node2D):
                child._transform_dirty = True
                child._global_transform = None
    
    def _update_transform_matrix(self) -> None:
        """Rebuild local transform matrix."""
        self._transform = Transform2D.from_components(
            translation=(self._position.x, self._position.y),
            rotation=math.radians(self._rotation),
            scale=(self._scale.x, self._scale.y)
        )
        self._transform_dirty = False
    
    def get_transform(self) -> Transform2D:
        """Get local transform matrix."""
        if self._transform_dirty:
            self._update_transform_matrix()
        return self._transform
    
    def get_global_transform(self) -> Transform2D:
        """Get transform in world space (combines all parent transforms)."""
        if not self._transform_dirty and self._global_transform is not None:
            return self._global_transform
        
        local = self.get_transform()
        
        if self.parent and isinstance(self.parent, Node2D):
            parent_global = self.parent.get_global_transform()
            # Combine: global = parent × local
            self._global_transform = parent_global * local
        else:
            self._global_transform = local
        
        return self._global_transform
    
    def get_global_position(self) -> Vector2:
        """Get position in world coordinates."""
        global_xform = self.get_global_transform()
        origin = global_xform.origin
        return Vector2(origin[0], origin[1])
    
    def set_global_position(self, pos: Vector2) -> None:
        """Set position in world coordinates."""
        if self.parent and isinstance(self.parent, Node2D):
            parent_global = self.parent.get_global_transform()
            # local = parent_global⁻¹ × global
            parent_inv = parent_global.affine_inverse()
            local_pos = parent_inv * (pos.x, pos.y)
            self.position = Vector2(local_pos[0], local_pos[1])
        else:
            self.position = pos
    
    def to_local(self, global_point: Vector2) -> Vector2:
        """Convert world point to local coordinates."""
        global_xform = self.get_global_transform()
        inv = global_xform.affine_inverse()
        result = inv * (global_point.x, global_point.y)
        return Vector2(result[0], result[1])
    
    def to_global(self, local_point: Vector2) -> Vector2:
        """Convert local point to world coordinates."""
        global_xform = self.get_global_transform()
        result = global_xform * (local_point.x, local_point.y)
        return Vector2(result[0], result[1])
    
    # === Transform Helpers ===
    def translate(self, offset: Vector2) -> None:
        """Move by offset in local space."""
        self.position = self._position + offset
    
    def rotate(self, degrees: float) -> None:
        """Rotate by degrees."""
        self.rotation = self._rotation + degrees
    
    def look_at(self, target: Vector2) -> None:
        """Rotate to face target position."""
        direction = target - self.get_global_position()
        self.rotation = math.degrees(direction.angle())
    
    # === Visibility ===
    def show(self) -> None:
        """Make visible."""
        if not self.visible:
            self.visible = True
            self.signals.emit("visibility_changed", True)
    
    def hide(self) -> None:
        """Make invisible."""
        if self.visible:
            self.visible = False
            self.signals.emit("visibility_changed", False)
    
    # === Drawing ===
    def _draw(self, renderer) -> None:
        """Override to render this node. Called by renderer."""
        pass


# =============================================================================
# Sprite2D
# =============================================================================

class Sprite2D(Node2D):
    """2D sprite for displaying textures.
    
    Properties:
        texture: Texture2D to display
        offset: Pixel offset from transform position (Vector2)
        flip_h: Flip horizontally (bool)
        flip_v: Flip vertically (bool)
        centered: If True, texture center at position (bool)
        modulate: Color tint (Color)
        hframes: Horizontal frames for animation (int)
        vframes: Vertical frames for animation (int)
        frame: Current frame index (int)
    
    Signals:
        texture_changed: When texture is changed
        frame_changed: When animation frame changes
    """
    
    __slots__ = [
        "texture", "offset", "flip_h", "flip_v", "centered",
        "hframes", "vframes", "_frame", "region_enabled", "region_rect"
    ]
    
    _SIGNALS = ["texture_changed", "frame_changed"]
    
    def __init__(self, name: str = "Sprite2D"):
        super().__init__(name)
        self.node_type = NodeType.SPRITE
        
        self.texture: Optional[Texture2D] = None
        self.offset = Vector2(0, 0)
        self.flip_h = False
        self.flip_v = False
        self.centered = True
        
        # Animation
        self.hframes = 1
        self.vframes = 1
        self._frame = 0
        
        # Region
        self.region_enabled = False
        self.region_rect = (0, 0, 16, 16)  # x, y, width, height
    
    @property
    def frame(self) -> int:
        return self._frame
    
    @frame.setter
    def frame(self, value: int) -> None:
        if value != self._frame:
            self._frame = value
            self.signals.emit("frame_changed", value)
    
    def set_texture(self, texture: Texture2D) -> None:
        """Set the texture."""
        self.texture = texture
        self.signals.emit("texture_changed", texture)
    
    def get_frame_size(self) -> Vector2:
        """Get size of single frame."""
        if not self.texture or self.texture.width == 0:
            return Vector2(16, 16)
        
        frame_w = self.texture.width / self.hframes
        frame_h = self.texture.height / self.vframes
        return Vector2(frame_w, frame_h)
    
    def _draw(self, renderer) -> None:
        """Render the sprite."""
        if not self.texture or not self.visible:
            return
        
        global_pos = self.get_global_position()
        draw_pos = global_pos + self.offset
        
        # Calculate texture region
        if self.hframes > 1 or self.vframes > 1:
            frame_size = self.get_frame_size()
            frame_x = (self._frame % self.hframes) * frame_size.x
            frame_y = (self._frame // self.hframes) * frame_size.y
            src_rect = (frame_x, frame_y, frame_size.x, frame_size.y)
        elif self.region_enabled:
            src_rect = self.region_rect
        else:
            src_rect = (0, 0, self.texture.width, self.texture.height)
        
        # Apply centering
        if self.centered:
            draw_pos = draw_pos - Vector2(src_rect[2] / 2, src_rect[3] / 2)
        
        # Apply flipping via scale
        scale = self.scale
        if self.flip_h:
            scale = Vector2(-scale.x, scale.y)
        if self.flip_v:
            scale = Vector2(scale.x, -scale.y)
        
        # Submit to renderer
        if hasattr(renderer, 'draw_sprite'):
            renderer.draw_sprite(
                texture=self.texture,
                position=draw_pos,
                source_rect=src_rect,
                scale=scale,
                rotation=self.rotation,
                modulate=self.modulate
            )


# =============================================================================
# CollisionShape2D (Component for physics)
# =============================================================================

class CollisionShape2D(Node2D):
    """Collision shape component. Must be child of physics body.
    
    This uses COMPOSITION pattern - add this as child to CharacterBody2D
    or Area2D instead of inheriting.
    """
    
    __slots__ = ["shape", "disabled"]
    
    def __init__(self, name: str = "CollisionShape2D"):
        super().__init__(name)
        self.shape: Optional[Any] = None  # Circle, Rectangle, Polygon
        self.disabled = False
    
    def get_global_shape(self) -> Any:
        """Get shape transformed to world space."""
        if not self.shape:
            return None
        # Transform shape by global transform
        # This would return transformed shape
        return self.shape


# =============================================================================
# CharacterBody2D
# =============================================================================

class CharacterBody2D(Node2D):
    """Kinematic character body with collision detection.
    
    Uses move_and_slide() for collision response without physics simulation.
    Perfect for player characters and NPCs.
    
    Properties:
        velocity: Current velocity (Vector2)
        up_direction: Direction considered "up" for floor detection (Vector2)
        floor_max_angle: Max slope angle in degrees (float)
        motion_mode: GROUNDED or FLOATING (MotionMode)
    
    State:
        is_on_floor: Standing on floor (bool)
        is_on_wall: Touching wall (bool)
        is_on_ceiling: Touching ceiling (bool)
        floor_normal: Normal vector of floor (Vector2)
    
    Signals:
        motion_changed: When velocity changes
        floor_state_changed: When floor/wall/ceiling state changes
    """
    
    class MotionMode(Enum):
        GROUNDED = auto()   # Uses floor/slope detection
        FLOATING = auto()   # Free movement
    
    __slots__ = [
        "velocity", "up_direction", "floor_max_angle", "motion_mode",
        "floor_snap_length", "floor_stop_on_slope",
        "is_on_floor", "is_on_wall", "is_on_ceiling", "floor_normal",
        "_collision_shape"
    ]
    
    _SIGNALS = ["motion_changed", "floor_state_changed"]
    
    def __init__(self, name: str = "CharacterBody2D"):
        super().__init__(name)
        self.node_type = NodeType.CHARACTER_BODY
        
        # Motion
        self.velocity = Vector2(0, 0)
        self.up_direction = Vector2(0, -1)  # Y-up
        self.floor_max_angle = 45.0
        self.motion_mode = self.MotionMode.GROUNDED
        
        # Floor snapping
        self.floor_snap_length = 18.0
        self.floor_stop_on_slope = True
        
        # State
        self.is_on_floor = False
        self.is_on_wall = False
        self.is_on_ceiling = False
        self.floor_normal = Vector2(0, 0)
        
        # Reference to collision shape (set via composition)
        self._collision_shape: Optional[CollisionShape2D] = None
    
    def set_collision_shape(self, shape: CollisionShape2D) -> None:
        """Set the collision shape component."""
        self._collision_shape = shape
    
    def move_and_slide(self, velocity: Vector2) -> Vector2:
        """Move with collision detection and sliding.
        
        This is THE Godot method for character movement.
        Returns the actual velocity after collision response.
        """
        self.velocity = velocity
        
        # This is a simplified version - real implementation would
        # integrate with physics server
        delta = 1.0 / 60.0  # Assume 60 FPS
        motion = velocity * delta
        
        # Move and check collisions
        new_pos = self.position + motion
        self.position = new_pos
        
        # Update floor detection (simplified)
        self._update_floor_detection()
        
        self.signals.emit("motion_changed", self.velocity)
        return self.velocity
    
    def _update_floor_detection(self) -> None:
        """Check if on floor/wall/ceiling."""
        was_on_floor = self.is_on_floor
        
        # Simplified floor check
        # Real implementation would raycast downward
        self.is_on_floor = False  # Placeholder
        self.is_on_wall = False
        self.is_on_ceiling = False
        
        if was_on_floor != self.is_on_floor:
            self.signals.emit("floor_state_changed", self.is_on_floor)
    
    def get_real_velocity(self) -> Vector2:
        """Get actual velocity from last move_and_slide()."""
        return self.velocity
    
    def is_on_floor_only(self) -> bool:
        """True if on floor but not wall or ceiling."""
        return self.is_on_floor and not self.is_on_wall and not self.is_on_ceiling


# =============================================================================
# Area2D
# =============================================================================

class Area2D(Node2D):
    """Non-solid region for detection and triggers.
    
    Detects bodies entering/exiting without blocking movement.
    Perfect for: triggers, powerup zones, damage areas, gravity zones.
    
    Properties:
        monitoring: Detect other bodies entering (bool)
        monitorable: Can be detected by other areas (bool)
        priority: Higher priority wins in overlaps (int)
    
    Signals:
        body_entered(body): When physics body enters
        body_exited(body): When physics body exits
        area_entered(area): When area enters
        area_exited(area): When area exits
    """
    
    class SpaceOverride(Enum):
        DISABLED = 0
        COMBINE = 1
        REPLACE = 2
    
    __slots__ = [
        "monitoring", "monitorable", "priority",
        "gravity_space_override", "gravity_direction", "gravity_strength",
        "_overlapping_bodies", "_overlapping_areas",
        "_collision_shape"
    ]
    
    _SIGNALS = [
        "body_entered", "body_exited",
        "area_entered", "area_exited"
    ]
    
    def __init__(self, name: str = "Area2D"):
        super().__init__(name)
        self.node_type = NodeType.AREA
        
        self.monitoring = True
        self.monitorable = True
        self.priority = 0
        
        # Physics overrides
        self.gravity_space_override = self.SpaceOverride.DISABLED
        self.gravity_direction = Vector2(0, 1)
        self.gravity_strength = 0.0
        
        # Tracking
        self._overlapping_bodies: Set[Node2D] = set()
        self._overlapping_areas: Set[Area2D] = set()
        
        self._collision_shape: Optional[CollisionShape2D] = None
    
    def set_collision_shape(self, shape: CollisionShape2D) -> None:
        """Set collision shape."""
        self._collision_shape = shape
    
    def get_overlapping_bodies(self) -> List[Node2D]:
        """Get list of bodies currently inside."""
        return list(self._overlapping_bodies)
    
    def get_overlapping_areas(self) -> List[Area2D]:
        """Get list of overlapping areas."""
        return list(self._overlapping_areas)
    
    def has_overlapping_bodies(self) -> bool:
        """Quick check if any bodies inside."""
        return len(self._overlapping_bodies) > 0
    
    def overlaps_body(self, body: Node2D) -> bool:
        """Check if specific body is inside."""
        return body in self._overlapping_bodies
    
    def _on_body_enter(self, body: Node2D) -> None:
        """Called when body enters."""
        if not self.monitoring:
            return
        if body not in self._overlapping_bodies:
            self._overlapping_bodies.add(body)
            self.signals.emit("body_entered", body)
    
    def _on_body_exit(self, body: Node2D) -> None:
        """Called when body exits."""
        if body in self._overlapping_bodies:
            self._overlapping_bodies.remove(body)
            self.signals.emit("body_exited", body)


# =============================================================================
# Camera2D
# =============================================================================

class Camera2D(Node2D):
    """2D camera for viewport control.
    
    Properties:
        zoom: Zoom level, (1,1) = normal, (2,2) = 2x zoomed in (Vector2)
        offset: Camera offset from position (Vector2)
        limit_left/right/top/bottom: View bounds (int)
        smoothing_enabled: Smooth camera follow (bool)
        smoothing_speed: Follow speed (float)
    
    Signals:
        camera_moved: When camera position changes
    """
    
    class AnchorMode(Enum):
        FIXED_TOP_LEFT = 0
        FIXED_CENTER = 1
    
    __slots__ = [
        "zoom", "offset",
        "limit_left", "limit_right", "limit_top", "limit_bottom",
        "limit_smoothed",
        "smoothing_enabled", "smoothing_speed",
        "anchor_mode",
        "follow_target", "follow_smoothing",
        "_camera_position"
    ]
    
    _SIGNALS = ["camera_moved"]
    
    def __init__(self, name: str = "Camera2D"):
        super().__init__(name)
        self.node_type = NodeType.CAMERA2D
        
        self.zoom = Vector2(1, 1)
        self.offset = Vector2(0, 0)
        
        # Limits
        self.limit_left = -10000000
        self.limit_right = 10000000
        self.limit_top = -10000000
        self.limit_bottom = 10000000
        self.limit_smoothed = False
        
        # Smoothing
        self.smoothing_enabled = False
        self.smoothing_speed = 5.0
        
        self.anchor_mode = self.AnchorMode.FIXED_CENTER
        
        # Following
        self.follow_target: Optional[Node2D] = None
        self.follow_smoothing = 0.0
        
        self._camera_position = Vector2(0, 0)
    
    def get_screen_center_position(self) -> Vector2:
        """Get world position at center of screen."""
        return self.get_global_position() + self.offset
    
    def set_follow_target(self, target: Optional[Node2D]) -> None:
        """Set node to automatically follow."""
        self.follow_target = target
    
    def align(self) -> None:
        """Update camera position - call every frame."""
        if self.follow_target:
            target_pos = self.follow_target.get_global_position()
        else:
            target_pos = self.get_global_position()
        
        # Apply smoothing
        if self.smoothing_enabled:
            self._camera_position = self._camera_position.lerp(
                target_pos, 
                self.smoothing_speed / 60.0
            )
        else:
            self._camera_position = target_pos
        
        # Apply limits
        self._apply_limits()
        
        self.signals.emit("camera_moved", self._camera_position)
    
    def _apply_limits(self) -> None:
        """Clamp position to limits."""
        if not self.limit_smoothed:
            self._camera_position.x = max(self.limit_left, 
                min(self._camera_position.x, self.limit_right))
            self._camera_position.y = max(self.limit_top,
                min(self._camera_position.y, self.limit_bottom))
    
    def force_update_scroll(self) -> None:
        """Immediately snap to target."""
        if self.follow_target:
            self._camera_position = self.follow_target.get_global_position()
    
    def is_position_visible(self, world_pos: Vector2) -> bool:
        """Check if world position is in camera view."""
        # Simplified - real implementation would use viewport rect
        center = self.get_screen_center_position()
        # Assume 800x600 viewport at zoom 1
        half_w = 400 / self.zoom.x
        half_h = 300 / self.zoom.y
        
        return (
            world_pos.x >= center.x - half_w and
            world_pos.x <= center.x + half_w and
            world_pos.y >= center.y - half_h and
            world_pos.y <= center.y + half_h
        )


# =============================================================================
# CanvasLayer
# =============================================================================

class CanvasLayer(Node2D):
    """Layer for UI and HUD separation.
    
    Renders children in separate layer with independent transform.
    Useful for: UI, HUD, parallax backgrounds.
    
    Properties:
        layer: Draw order, higher = on top (int)
        follow_viewport: Parallax follow (bool)
        follow_viewport_scale: Parallax factor (float)
        offset: Layer offset (Vector2)
    
    Signals:
        layer_changed: When layer order changes
    """
    
    __slots__ = [
        "layer_value", "offset", "rotation", "scale_value",
        "follow_viewport", "follow_viewport_scale"
    ]
    
    _SIGNALS = ["layer_changed"]
    
    def __init__(self, name: str = "CanvasLayer"):
        super().__init__(name)
        
        self.layer_value = 1
        self.offset = Vector2(0, 0)
        self.rotation = 0.0
        self.scale_value = Vector2(1, 1)
        
        self.follow_viewport = False
        self.follow_viewport_scale = 1.0
    
    @property
    def layer(self) -> int:
        return self.layer_value
    
    @layer.setter
    def layer(self, value: int) -> None:
        if value != self.layer_value:
            self.layer_value = value
            self.signals.emit("layer_changed", value)
    
    def get_final_transform(self, camera_position: Vector2 = Vector2(0, 0)) -> Transform2D:
        """Get layer transform accounting for parallax."""
        if self.follow_viewport:
            # Parallax: move slower than camera
            parallax_offset = camera_position * self.follow_viewport_scale
            effective_offset = self.offset - parallax_offset
        else:
            effective_offset = self.offset
        
        return Transform2D.from_components(
            translation=(effective_offset.x, effective_offset.y),
            rotation=math.radians(self.rotation),
            scale=(self.scale_value.x, self.scale_value.y)
        )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "Vector2",
    "Color",
    "Texture2D",
    "Node2D",
    "Sprite2D",
    "CollisionShape2D",
    "CharacterBody2D",
    "Area2D",
    "Camera2D",
    "CanvasLayer",
]
