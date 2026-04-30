# /**************************************************************************/
# /*  pressure_curve.py                                                     */
# /**************************************************************************/

"""Pressure curve for graphics tablet support.

Maps raw pressure values (0.0-1.0) to brush properties
using customizable curves.
"""

from typing import Callable, List, Tuple
from enum import Enum, auto
import math


class CurveType(Enum):
    """Pressure curve types."""
    LINEAR = auto()      # 1:1 mapping
    QUADRATIC = auto()   # Exponential
    INVERSE_QUAD = auto()  # Inverse exponential
    S_CURVE = auto()     # S-shaped curve
    HARD = auto()        # Threshold-based
    CUSTOM = auto()      # User-defined points


class PressureCurve:
    """Pressure response curve for brush dynamics.
    
    Maps tablet pressure (0.0-1.0) to brush properties:
    - Size
    - Opacity
    - Color intensity
    
    Common curve types:
    - Linear: Direct 1:1 mapping
    - Quadratic: Soft start, quick ramp
    - S-Curve: Soft start and end
    - Hard: Threshold-based (on/off)
    """
    
    def __init__(self, curve_type: CurveType = CurveType.LINEAR):
        self.curve_type = curve_type
        self._custom_points: List[Tuple[float, float]] = []
        self._min_input = 0.0
        self._max_input = 1.0
        self._min_output = 0.0
        self._max_output = 1.0
    
    def set_range(self, min_in: float, max_in: float, 
                  min_out: float, max_out: float) -> None:
        """Set input/output value ranges."""
        self._min_input = min_in
        self._max_input = max_in
        self._min_output = min_out
        self._max_output = max_out
    
    def set_custom_points(self, points: List[Tuple[float, float]]) -> None:
        """Set custom curve control points.
        
        Points should be [(input, output), ...] sorted by input.
        """
        self._custom_points = sorted(points, key=lambda p: p[0])
        self.curve_type = CurveType.CUSTOM
    
    def map(self, pressure: float) -> float:
        """Map input pressure to output value."""
        # Clamp input
        pressure = max(0.0, min(1.0, pressure))
        
        # Apply curve function
        if self.curve_type == CurveType.LINEAR:
            result = pressure
        elif self.curve_type == CurveType.QUADRATIC:
            result = pressure * pressure
        elif self.curve_type == CurveType.INVERSE_QUAD:
            result = 1.0 - (1.0 - pressure) * (1.0 - pressure)
        elif self.curve_type == CurveType.S_CURVE:
            # Sigmoid-like curve
            result = self._s_curve(pressure)
        elif self.curve_type == CurveType.HARD:
            # Threshold at 0.5
            result = 0.0 if pressure < 0.5 else 1.0
        elif self.curve_type == CurveType.CUSTOM:
            result = self._interpolate_custom(pressure)
        else:
            result = pressure
        
        # Scale to output range
        return self._min_output + result * (self._max_output - self._min_output)
    
    def _s_curve(self, x: float) -> float:
        """Calculate S-curve value."""
        # Smooth step function: 3x^2 - 2x^3
        return x * x * (3.0 - 2.0 * x)
    
    def _interpolate_custom(self, x: float) -> float:
        """Interpolate using custom control points."""
        if not self._custom_points:
            return x
        
        # Find surrounding points
        points = self._custom_points
        
        # Before first point
        if x <= points[0][0]:
            return points[0][1]
        
        # After last point
        if x >= points[-1][0]:
            return points[-1][1]
        
        # Find segment and interpolate
        for i in range(len(points) - 1):
            x0, y0 = points[i]
            x1, y1 = points[i + 1]
            
            if x0 <= x <= x1:
                # Linear interpolation
                if x1 == x0:
                    return y0
                t = (x - x0) / (x1 - x0)
                return y0 + t * (y1 - y0)
        
        return x
    
    def map_size(self, pressure: float, min_size: float, max_size: float) -> float:
        """Map pressure to brush size."""
        t = self.map(pressure)
        return min_size + t * (max_size - min_size)
    
    def map_opacity(self, pressure: float, min_opacity: float, max_opacity: float) -> float:
        """Map pressure to brush opacity."""
        t = self.map(pressure)
        return min_opacity + t * (max_opacity - min_opacity)
    
    @classmethod
    def linear(cls) -> 'PressureCurve':
        """Create linear curve."""
        return cls(CurveType.LINEAR)
    
    @classmethod
    def quadratic(cls) -> 'PressureCurve':
        """Create quadratic curve (soft start)."""
        return cls(CurveType.QUADRATIC)
    
    @classmethod
    def s_curve(cls) -> 'PressureCurve':
        """Create S-curve (soft start and end)."""
        return cls(CurveType.S_CURVE)
    
    @classmethod
    def hard(cls, threshold: float = 0.1) -> 'PressureCurve':
        """Create hard/threshold curve."""
        curve = cls(CurveType.HARD)
        curve._min_input = threshold
        return curve


class BrushDynamics:
    """Brush dynamics combining multiple pressure curves."""
    
    def __init__(self):
        self.size_curve = PressureCurve.linear()
        self.opacity_curve = PressureCurve.linear()
        self.color_curve = PressureCurve.linear()
        
        # Enable flags
        self.size_enabled = True
        self.opacity_enabled = False
        self.color_enabled = False
        
        # Value ranges
        self.min_size = 1.0
        self.max_size = 10.0
        self.min_opacity = 0.1
        self.max_opacity = 1.0
    
    def apply(self, brush, pressure: float) -> None:
        """Apply pressure to brush.
        
        Modifies brush properties based on pressure.
        """
        if self.size_enabled:
            new_size = self.size_curve.map_size(
                pressure, self.min_size, self.max_size
            )
            brush.size = int(round(new_size))
        
        if self.opacity_enabled:
            brush.opacity = self.opacity_curve.map_opacity(
                pressure, self.min_opacity, self.max_opacity
            )
    
    def reset(self, brush) -> None:
        """Reset brush to default state."""
        brush.size = int(self.max_size)
        brush.opacity = 1.0
