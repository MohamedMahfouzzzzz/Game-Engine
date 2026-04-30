# /**************************************************************************/
# /*  transform.py                                                          */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

from dataclasses import dataclass
import math
from typing import List, Tuple

import logging


logger = logging.getLogger(__name__)



@dataclass
class Transform2D:
    """2D affine transformation matrix.
    
    Stores position, rotation, and scale for efficient 2D transforms.
    """
    
    position: Tuple[float, float] = (0.0, 0.0)
    rotation: float = 0.0
    scale: Tuple[float, float] = (1.0, 1.0)
    
    @classmethod
    def from_components(
        cls,
        translation: Tuple[float, float] = (0, 0),
        rotation: float = 0.0,
        scale: Tuple[float, float] = (1, 1)
    ) -> 'Transform2D':
        """Create transform from components."""
        return cls(
            position=translation,
            rotation=rotation,
            scale=scale
        )
    
    @classmethod
    def identity(cls) -> 'Transform2D':
        """Create identity transform."""
        return cls()
    
    @property
    def origin(self) -> Tuple[float, float]:
        """Get origin position."""
        return self.position
    
    def get_matrix(self) -> List[List[float]]:
        """Return a 3x3 transform matrix."""
        cos_r = math.cos(self.rotation)
        sin_r = math.sin(self.rotation)
        sx, sy = self.scale
        px, py = self.position
        return [
            [cos_r * sx, -sin_r * sy, px],
            [sin_r * sx, cos_r * sy, py],
            [0.0, 0.0, 1.0],
        ]
    
    def __mul__(self, other) -> 'Transform2D':
        """Combine two transforms: self × other."""
        if isinstance(other, Transform2D):
            # Combine transforms: T1 * T2 means apply T2 then T1
            # For position: T1.position + rotate_scale(T2.position)
            cos_r = math.cos(self.rotation)
            sin_r = math.sin(self.rotation)
            
            # Apply T1's rotation and scale to T2's position
            x2, y2 = other.position
            new_x = self.position[0] + (cos_r * self.scale[0] * x2 - sin_r * self.scale[1] * y2)
            new_y = self.position[1] + (sin_r * self.scale[0] * x2 + cos_r * self.scale[1] * y2)
            
            # Combine rotations
            new_rotation = self.rotation + other.rotation
            
            # Combine scales
            new_scale = (self.scale[0] * other.scale[0], self.scale[1] * other.scale[1])
            
            return cls(
                position=(new_x, new_y),
                rotation=new_rotation,
                scale=new_scale
            )
        elif isinstance(other, tuple) and len(other) == 2:
            # Transform a point
            x, y = other
            cos_r = math.cos(self.rotation)
            sin_r = math.sin(self.rotation)
            
            new_x = self.position[0] + (cos_r * self.scale[0] * x - sin_r * self.scale[1] * y)
            new_y = self.position[1] + (sin_r * self.scale[0] * x + cos_r * self.scale[1] * y)
            
            return (new_x, new_y)
        
        return NotImplemented
    
    def affine_inverse(self) -> 'Transform2D':
        """Calculate inverse transform (world to local)."""
        # For scale, we use reciprocal
        inv_scale = (
            1.0 / self.scale[0] if self.scale[0] != 0 else 0,
            1.0 / self.scale[1] if self.scale[1] != 0 else 0
        )
        
        # For rotation, negate (and reverse order for application)
        inv_rotation = -self.rotation
        
        # For position: rotate and scale the negative position
        cos_r = math.cos(inv_rotation)
        sin_r = math.sin(inv_rotation)
        
        px, py = self.position
        
        # (-position) transformed by inverse scale and rotation
        inv_x = inv_scale[0] * (cos_r * (-px) - sin_r * (-py))
        inv_y = inv_scale[1] * (sin_r * (-px) + cos_r * (-py))
        
        return Transform2D(
            position=(inv_x, inv_y),
            rotation=inv_rotation,
            scale=inv_scale
        )
