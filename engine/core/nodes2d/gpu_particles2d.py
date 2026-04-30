# /**************************************************************************/
# /*  gpu_particles2d.py                                                    */
# /**************************************************************************/

"""GPUParticles2D - GPU-based 2D particle system."""

from __future__ import annotations
from typing import Optional, Any
from enum import IntEnum
from .node2d import Node2D
from .types import Vector2, Texture2D
from engine.core.types import NodeType

class Rect2:
    """2D rectangle."""
    def __init__(self, x: float = 0, y: float = 0, w: float = 0, h: float = 0):
        self.x = x
        self.y = y
        self.width = w
        self.height = h


class Material:
    """Material resource."""
    pass


class GPUParticles2D(Node2D):
    """GPU-based particle system.
    
    Properties:
        emitting: bool - Currently emitting
        amount: int - Particle count
        process_material: Material - Particle shader
        texture: Texture2D - Particle texture
        lifetime: float - Particle lifetime
        one_shot: bool - Emit once
        preprocess: float - Preprocess time
        speed_scale: float - Simulation speed
        explosiveness: float - 0-1 emission spread
        randomness: float - 0-1 random offset
        fixed_fps: int - Update rate (0 = variable)
        interpolate: bool - Interpolate frames
        fract_delta: bool - Fractional delta
        visibility_rect: Rect2 - Visibility bounds
        local_coords: bool - Local vs global coords
        draw_order: int - 0=INDEX, 1=LIFETIME, 2=REVERSE_LIFETIME, 3=VIEW_DEPTH
    
    Signals:
        finished - Emission complete (one_shot)
    """
    
    class DrawOrder(IntEnum):
        INDEX = 0
        LIFETIME = 1
        REVERSE_LIFETIME = 2
        VIEW_DEPTH = 3
    
    __slots__ = [
        "emitting",
        "amount",
        "process_material",
        "texture",
        "lifetime",
        "one_shot",
        "preprocess",
        "speed_scale",
        "explosiveness",
        "randomness",
        "fixed_fps",
        "interpolate",
        "fract_delta",
        "visibility_rect",
        "local_coords",
        "draw_order"
    ]
    
    _SIGNALS = ["finished"]
    
    def __init__(self, name: str = "GPUParticles2D"):
        super().__init__(name)
        self.node_type = NodeType.GPU_PARTICLES2D
        
        self.emitting: bool = True
        self.amount: int = 100
        self.process_material: Optional[Material] = None
        self.texture: Optional[Texture2D] = None
        self.lifetime: float = 1.0
        self.one_shot: bool = False
        self.preprocess: float = 0.0
        self.speed_scale: float = 1.0
        self.explosiveness: float = 0.0
        self.randomness: float = 0.0
        self.fixed_fps: int = 0
        self.interpolate: bool = True
        self.fract_delta: bool = True
        self.visibility_rect: Rect2 = Rect2(-100, -100, 200, 200)
        self.local_coords: bool = True
        self.draw_order: int = self.DrawOrder.INDEX
    
    def restart(self) -> None:
        """Restart emission."""
        pass
    
    def set_emitting(self, emitting: bool) -> None:
        """Set emitting state."""
        self.emitting = emitting
        if not emitting and self.one_shot:
            self.signals.emit("finished")


__all__ = ["GPUParticles2D", "Rect2"]
