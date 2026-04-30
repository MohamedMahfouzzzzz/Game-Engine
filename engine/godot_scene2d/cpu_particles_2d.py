# /**************************************************************************/
# /*  cpu_particles_2d.py                                                   */
# /**************************************************************************/

"""Godot CPUParticles2D port - CPU-based particle system."""

from enum import IntEnum
from typing import List, Optional
from engine.core.nodes2d import Node2D
from engine.godot_scene2d.types import Point2, Color


class CPUParticles2DEmissionShape(IntEnum):
    EMISSION_SHAPE_POINT = 0
    EMISSION_SHAPE_SPHERE = 1
    EMISSION_SHAPE_BOX = 2
    EMISSION_SHAPE_POINTS = 3
    EMISSION_SHAPE_DIRECTED_POINTS = 4
    EMISSION_SHAPE_RING = 5


class CPUParticles2D(Node2D):
    """CPU-based 2D particle system."""
    
    def __init__(self, name: str = "CPUParticles2D"):
        super().__init__(name)
        self._emitting: bool = True
        self._amount: int = 100
        self._lifetime: float = 2.0
        self._one_shot: bool = False
        self._preprocess: float = 0.0
        self._speed_scale: float = 1.0
        self._explosiveness: float = 0.0
        self._randomness: float = 0.0
        self._fixed_fps: int = 0
        
        # Emission
        self._emission_shape: CPUParticles2DEmissionShape = CPUParticles2DEmissionShape.EMISSION_SHAPE_POINT
        self._emission_sphere_radius: float = 20.0
        self._emission_rect_extents: Point2 = Point2(20, 20)
        self._emission_points: List[Point2] = []
        self._emission_normals: List[Point2] = []
        self._emission_ring_inner_radius: float = 10.0
        self._emission_ring_outer_radius: float = 20.0
        self._emission_ring_axis: Point2 = Point2(0, 0)
        
        # Physics
        self._direction: Point2 = Point2(0, -1)
        self._spread: float = 45.0
        self._gravity: Point2 = Point2(0, 98)
        self._initial_velocity_min: float = 0.0
        self._initial_velocity_max: float = 100.0
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
        self._angle_min: float = 0.0
        self._angle_max: float = 0.0
        self._scale_amount_min: float = 1.0
        self._scale_amount_max: float = 1.0
        
        # Color
        self._color: Color = Color(1, 1, 1)
        self._color_ramp: Optional[any] = None
        self._hue_variation_min: float = 0.0
        self._hue_variation_max: float = 0.0
        
        # Particles storage
        self._particles: List[dict] = []
        self._time: float = 0.0
    
    def set_emitting(self, emitting: bool) -> None:
        self._emitting = emitting
    
    def is_emitting(self) -> bool:
        return self._emitting
    
    def set_amount(self, amount: int) -> None:
        self._amount = max(1, amount)
    
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
    
    def set_preprocess(self, preprocess: float) -> None:
        self._preprocess = max(0.0, preprocess)
    
    def get_preprocess(self) -> float:
        return self._preprocess
    
    def set_speed_scale(self, scale: float) -> None:
        self._speed_scale = max(0.0, scale)
    
    def get_speed_scale(self) -> float:
        return self._speed_scale
    
    def set_explosiveness(self, explosiveness: float) -> None:
        self._explosiveness = max(0.0, min(1.0, explosiveness))
    
    def get_explosiveness(self) -> float:
        return self._explosiveness
    
    def set_emission_shape(self, shape: CPUParticles2DEmissionShape) -> None:
        self._emission_shape = shape
    
    def get_emission_shape(self) -> CPUParticles2DEmissionShape:
        return self._emission_shape
    
    def set_direction(self, direction: Point2) -> None:
        self._direction = direction
    
    def get_direction(self) -> Point2:
        return self._direction
    
    def set_spread(self, spread: float) -> None:
        self._spread = max(0.0, min(180.0, spread))
    
    def get_spread(self) -> float:
        return self._spread
    
    def set_gravity(self, gravity: Point2) -> None:
        self._gravity = gravity
    
    def get_gravity(self) -> Point2:
        return self._gravity
    
    def set_initial_velocity_min(self, velocity: float) -> None:
        self._initial_velocity_min = velocity
    
    def get_initial_velocity_min(self) -> float:
        return self._initial_velocity_min
    
    def set_initial_velocity_max(self, velocity: float) -> None:
        self._initial_velocity_max = velocity
    
    def get_initial_velocity_max(self) -> float:
        return self._initial_velocity_max
    
    def set_color(self, color: Color) -> None:
        self._color = color
    
    def get_color(self) -> Color:
        return self._color
    
    def restart(self) -> None:
        self._particles.clear()
        self._time = 0.0
    
    def process(self, delta: float) -> None:
        if not self._emitting and not self._particles:
            return
        
        delta *= self._speed_scale
        self._time += delta
        
        # Simple particle processing would go here
        # For now, just placeholder
    
    def __repr__(self) -> str:
        return f"CPUParticles2D('{self.name}', amount={self._amount}, lifetime={self._lifetime}, emitting={self._emitting})"
