"""Built-in functions for GD Language."""

import math
from typing import Any, Dict, List
from .data_types import GDArray, GDDictionary, GDValue, Type


class GDBuiltins:
    """Built-in GD Language functions."""

    @staticmethod
    def print(*args) -> None:
        """Print values to console."""
        output = " ".join(str(arg) for arg in args)
        print(output)

    @staticmethod
    def debug(*args) -> None:
        """Print debug information."""
        output = " ".join(str(arg) for arg in args)
        print(f"[DEBUG] {output}")

    @staticmethod
    def assert_true(condition: bool, message: str = "") -> None:
        """Assert that condition is true."""
        if not condition:
            raise AssertionError(message or "Assertion failed")

    @staticmethod
    def typeof(value: Any) -> str:
        """Get type of value as string."""
        val = value if isinstance(value, GDValue) else GDValue(value)
        return val.value_type.value

    @staticmethod
    def int(value: Any) -> int:
        """Convert to integer."""
        if isinstance(value, GDValue):
            return int(value.cast(Type.INT).value)
        return int(value)

    @staticmethod
    def float_val(value: Any) -> float:
        """Convert to float."""
        if isinstance(value, GDValue):
            return float(value.cast(Type.FLOAT).value)
        return float(value)

    @staticmethod
    def str_val(value: Any) -> str:
        """Convert to string."""
        if isinstance(value, GDValue):
            return str(value.cast(Type.STRING).value)
        return str(value)

    @staticmethod
    def bool_val(value: Any) -> bool:
        """Convert to boolean."""
        if isinstance(value, GDValue):
            return bool(value.cast(Type.BOOL).value)
        return bool(value)

    @staticmethod
    def is_zero(value: Any) -> bool:
        """Check if value is zero."""
        return value == 0 or value == 0.0

    @staticmethod
    def is_equal_approx(a: float, b: float, epsilon: float = 0.00001) -> bool:
        """Check if floats are approximately equal."""
        return abs(a - b) < epsilon

    @staticmethod
    def abs_val(value: Any) -> Any:
        """Get absolute value."""
        return abs(value)

    @staticmethod
    def sign(value: Any) -> int:
        """Get sign of value (-1, 0, or 1)."""
        if value > 0:
            return 1
        if value < 0:
            return -1
        return 0

    @staticmethod
    def round_val(value: float) -> int:
        """Round to nearest integer."""
        return round(value)

    @staticmethod
    def floor_val(value: float) -> int:
        """Floor function."""
        return math.floor(value)

    @staticmethod
    def ceil_val(value: float) -> int:
        """Ceiling function."""
        return math.ceil(value)

    @staticmethod
    def sqrt(value: float) -> float:
        """Square root."""
        return math.sqrt(value)

    @staticmethod
    def pow_val(base: float, exponent: float) -> float:
        """Power function."""
        return math.pow(base, exponent)

    @staticmethod
    def sin(value: float) -> float:
        """Sine function (radians)."""
        return math.sin(value)

    @staticmethod
    def cos(value: float) -> float:
        """Cosine function (radians)."""
        return math.cos(value)

    @staticmethod
    def tan(value: float) -> float:
        """Tangent function (radians)."""
        return math.tan(value)

    @staticmethod
    def asin(value: float) -> float:
        """Arc sine function."""
        return math.asin(value)

    @staticmethod
    def acos(value: float) -> float:
        """Arc cosine function."""
        return math.acos(value)

    @staticmethod
    def atan(value: float) -> float:
        """Arc tangent function."""
        return math.atan(value)

    @staticmethod
    def atan2(y: float, x: float) -> float:
        """Arc tangent of y/x."""
        return math.atan2(y, x)

    @staticmethod
    def rad_to_deg(radians: float) -> float:
        """Convert radians to degrees."""
        return math.degrees(radians)

    @staticmethod
    def deg_to_rad(degrees: float) -> float:
        """Convert degrees to radians."""
        return math.radians(degrees)

    @staticmethod
    def min_val(*args) -> Any:
        """Get minimum value."""
        return min(args)

    @staticmethod
    def max_val(*args) -> Any:
        """Get maximum value."""
        return max(args)

    @staticmethod
    def clamp(value: float, min_val: float, max_val: float) -> float:
        """Clamp value between min and max."""
        return max(min_val, min(max_val, value))

    @staticmethod
    def lerp(from_val: float, to_val: float, weight: float) -> float:
        """Linear interpolation."""
        return from_val + (to_val - from_val) * weight

    @staticmethod
    def range_fn(start: int, end: int, step: int = 1) -> GDArray:
        """Create array with range of values."""
        items = list(range(start, end, step))
        return GDArray(items, Type.INT)

    @staticmethod
    def len_val(value: Any) -> int:
        """Get length of array/dictionary/string."""
        if isinstance(value, (GDArray, GDDictionary)):
            return value.size()
        return len(value)

    @staticmethod
    def preload(path: str) -> Any:
        """Placeholder for resource preloading."""
        # In a real implementation, this would load resources
        return None

    @staticmethod
    def yield_fn(object_val: Any, signal: str) -> Any:
        """Placeholder for signal yielding."""
        # In a real implementation, this would wait for signals
        return None


def setup_builtins(globals_dict: Dict[str, Any]) -> None:
    """Set up GD Language built-ins in a globals dictionary."""
    builtins = {
        'print': GDBuiltins.print,
        'debug': GDBuiltins.debug,
        'assert': GDBuiltins.assert_true,
        'typeof': GDBuiltins.typeof,
        'int': GDBuiltins.int,
        'float': GDBuiltins.float_val,
        'str': GDBuiltins.str_val,
        'bool': GDBuiltins.bool_val,
        'is_zero': GDBuiltins.is_zero,
        'is_equal_approx': GDBuiltins.is_equal_approx,
        'abs': GDBuiltins.abs_val,
        'sign': GDBuiltins.sign,
        'round': GDBuiltins.round_val,
        'floor': GDBuiltins.floor_val,
        'ceil': GDBuiltins.ceil_val,
        'sqrt': GDBuiltins.sqrt,
        'pow': GDBuiltins.pow_val,
        'sin': GDBuiltins.sin,
        'cos': GDBuiltins.cos,
        'tan': GDBuiltins.tan,
        'asin': GDBuiltins.asin,
        'acos': GDBuiltins.acos,
        'atan': GDBuiltins.atan,
        'atan2': GDBuiltins.atan2,
        'rad_to_deg': GDBuiltins.rad_to_deg,
        'deg_to_rad': GDBuiltins.deg_to_rad,
        'min': GDBuiltins.min_val,
        'max': GDBuiltins.max_val,
        'clamp': GDBuiltins.clamp,
        'lerp': GDBuiltins.lerp,
        'range': GDBuiltins.range_fn,
        'len': GDBuiltins.len_val,
        'Array': GDArray,
        'Dictionary': GDDictionary,
        'preload': GDBuiltins.preload,
        'yield': GDBuiltins.yield_fn,
    }

    globals_dict.update(builtins)
