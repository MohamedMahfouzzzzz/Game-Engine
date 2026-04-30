# /**************************************************************************/
# /*  particles.py                                                          */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""2D particle emitter using CPU calculations."""

import math
import random
from enum import IntEnum
from typing import List, Tuple, Optional
from engine.core.nodes2d import Node2D, Vector2, Color


class ParticleProcessMaterial:
    """Material defining particle behavior."""
    
    def __init__(self):
        self.initial_velocity_min = 0.0
        self.initial_velocity_max = 0.0
        self.angular_velocity_min = 0.0
        self.angular_velocity_max = 0.0
        self.orbit_velocity_min = 0.0
        self.orbit_velocity_max = 0.0
        self.linear_accel_min = 0.0
        self.linear_accel_max = 0.0
        self.radial_accel_min = 0.0
        self.radial_accel_max = 0.0
        self.tangential_accel_min = 0.0
        self.tangential_accel_max = 0.0
        self.damping_min = 0.0
        self.damping_max = 0.0
        self.scale_min = 1.0
        self.scale_max = 1.0
        self.scale_curve = None
        self.color = Color(1, 1, 1, 1)
        self.color_ramp = None
        self.hue_variation_min = 0.0
        self.hue_variation_max = 0.0
        self.emission_shape = 0
        self.emission_rect_extents = Vector2(1, 1)


class CPUParticles2D(Node2D):
    """CPU-based particle emitter for 2D effects.
    
    Features:
    - Configurable emission shapes (point, box, circle, ring)
    - Velocity, acceleration, and damping control
    - Scale and color animation over lifetime
    - Emission masks and sub-emitters
    """
    
    def __init__(self, name: str = "CPUParticles2D"):
        super().__init__(name)
        self._emitting: bool = True
        self._amount: int = 32
        self._lifetime: float = 1.0
        self._one_shot: bool = False
        self._preprocess: float = 0.0
        self._speed_scale: float = 1.0
        self._explosiveness: float = 0.0
        self._randomness: float = 0.0
        self._lifetime_randomness: float = 0.0
        self._fixed_fps: int = 0
        self._fract_delta: bool = True
        
        # Local coords
        self._local_coords: bool = False
        self._draw_order: int = 0
        
        # Particles
        self._particles: List[dict] = []
        self._emission_shape: int = 0
        self._emission_rect_extents: Vector2 = Vector2(1, 1)
        self._emission_sphere_radius: float = 1.0
        self._emission_ring_inner_radius: float = 0.0
        self._emission_ring_outer_radius: float = 1.0
        self._emission_ring_axis: Vector2 = Vector2(0, 1)
        self._emission_points: List[Vector2] = []
        self._emission_normals: List[Vector2] = []
        self._emission_colors: List[Color] = []
        
        # Particle params
        self._gravity: Vector2 = Vector2(0, 98)
        self._particle_flag_align_y: bool = False
        self._particle_flag_rotate_y: bool = False
        self._particle_flag_disable_z: bool = True
        self._direction: Vector2 = Vector2(1, 0)
        self._spread: float = 45.0
        self._flatness: float = 0.0
        self._initial_velocity_min: float = 0.0
        self._initial_velocity_max: float = 0.0
        self._angular_velocity_min: float = 0.0
        self._angular_velocity_max: float = 0.0
        self._orbit_velocity_min: float = 0.0
        self._orbit_velocity_max: float = 0.0
        self._linear_accel_min: float = 0.0
        self._linear_accel_max: float = 0.0
        self._radial_accel_min: float = 0.0
        self._radial_accel_max: float = 0.0
        self._tangential_accel_min: float = 0.0
        self._tangential_accel_max: float = 0.0
        self._damping_min: float = 0.0
        self._damping_max: float = 0.0
        self._scale_amount_min: float = 1.0
        self._scale_amount_max: float = 1.0
        self._scale_amount_curve = None
        self._split_scale = False
        self._scale_curve_x = None
        self._scale_curve_y = None
        self._color = Color(1, 1, 1, 1)
        self._color_ramp = None
        self._color_initial_ramp = None
        self._hue_variation_min: float = 0.0
        self._hue_variation_max: float = 0.0
        self._hue_variation_curve = None
        self._anim_speed_min: float = 0.0
        self._anim_speed_max: float = 0.0
        self._anim_speed_curve = None
        self._anim_offset_min: float = 0.0
        self._anim_offset_max: float = 1.0
        self._anim_offset_curve = None
        
        # Trail
        self._trail_enabled: bool = False
        self._trail_length_secs: float = 0.3
        self._trail_sections: int = 5
        self._trail_section_subdivisions: int = 4
        
        # Collision
        self._collision_enabled: bool = False
        self._collision_use_scale: bool = False
        self._collision_friction: float = 0.0
        self._collision_bounce: float = 0.0
        
        # Sub-emitter
        self._sub_emitter = None
        self._attractor_interaction_enabled: bool = True
    
    def set_emitting(self, emitting: bool) -> None:
        self._emitting = emitting
    
    def is_emitting(self) -> bool:
        return self._emitting
    
    def set_amount(self, amount: int) -> None:
        self._amount = max(1, amount)
        self._resize_particles()
    
    def get_amount(self) -> int:
        return self._amount
    
    def set_lifetime(self, lifetime: float) -> None:
        self._lifetime = max(0.01, lifetime)
    
    def get_lifetime(self) -> float:
        return self._lifetime
    
    def set_one_shot(self, one_shot: bool) -> None:
        self._one_shot = one_shot
    
    def get_one_shot(self) -> bool:
        return self._one_shot
    
    def set_speed_scale(self, speed_scale: float) -> None:
        self._speed_scale = max(0.0001, speed_scale)
    
    def get_speed_scale(self) -> float:
        return self._speed_scale
    
    def set_explosiveness(self, explosiveness: float) -> None:
        self._explosiveness = max(0.0, min(1.0, explosiveness))
    
    def get_explosiveness(self) -> float:
        return self._explosiveness
    
    def set_randomness(self, randomness: float) -> None:
        self._randomness = max(0.0, min(1.0, randomness))
    
    def get_randomness(self) -> float:
        return self._randomness
    
    def set_gravity(self, gravity: Vector2) -> None:
        self._gravity = gravity
    
    def get_gravity(self) -> Vector2:
        return self._gravity
    
    def set_direction(self, direction: Vector2) -> None:
        self._direction = direction.normalized() if direction.length() > 0 else Vector2(1, 0)
    
    def get_direction(self) -> Vector2:
        return self._direction
    
    def set_spread(self, spread: float) -> None:
        self._spread = max(0.0, min(180.0, spread))
    
    def get_spread(self) -> float:
        return self._spread
    
    def set_initial_velocity_min(self, velocity: float) -> None:
        self._initial_velocity_min = velocity
    
    def get_initial_velocity_min(self) -> float:
        return self._initial_velocity_min
    
    def set_initial_velocity_max(self, velocity: float) -> None:
        self._initial_velocity_max = velocity
    
    def get_initial_velocity_max(self) -> float:
        return self._initial_velocity_max
    
    def set_scale_amount_min(self, scale: float) -> None:
        self._scale_amount_min = max(0, scale)
    
    def get_scale_amount_min(self) -> float:
        return self._scale_amount_min
    
    def set_scale_amount_max(self, scale: float) -> None:
        self._scale_amount_max = max(0, scale)
    
    def get_scale_amount_max(self) -> float:
        return self._scale_amount_max
    
    def set_color(self, color: Color) -> None:
        self._color = color
    
    def get_color(self) -> Color:
        return self._color
    
    def _resize_particles(self) -> None:
        """Resize particle array to match amount."""
        current = len(self._particles)
        if current < self._amount:
            for _ in range(self._amount - current):
                self._particles.append({
                    'active': False,
                    'time': 0.0,
                    'lifetime': 0.0,
                    'position': Vector2(),
                    'velocity': Vector2(),
                    'rotation': 0.0,
                    'scale': 1.0,
                    'color': Color(1, 1, 1, 1)
                })
        elif current > self._amount:
            self._particles = self._particles[:self._amount]
    
    def restart(self) -> None:
        """Restart emission."""
        for p in self._particles:
            p['active'] = False
        self._emitting = not self._one_shot
    
    def emit_particle(self, xform, velocity, color, custom, flags) -> None:
        """Emit a single particle programmatically."""
        for p in self._particles:
            if not p['active']:
                p['active'] = True
                p['time'] = 0.0
                p['lifetime'] = self._lifetime * random.uniform(1.0 - self._lifetime_randomness, 1.0)
                p['position'] = Vector2()
                p['velocity'] = velocity
                p['rotation'] = 0.0
                p['scale'] = random.uniform(self._scale_amount_min, self._scale_amount_max)
                p['color'] = color
                break
    
    def __repr__(self) -> str:
        return f"CPUParticles2D('{self.name}', amount={self._amount}, emitting={self._emitting})"
