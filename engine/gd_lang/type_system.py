"""Type validation and checking for GD Language."""

from typing import Any, Dict, Optional, Callable
from .data_types import Type, GDValue, GDArray, GDDictionary


class TypeValidator:
    """Validates and enforces GD Language types."""

    # Type coercion rules
    COERCIBLE = {
        Type.INT: [Type.FLOAT, Type.STRING, Type.BOOL],
        Type.FLOAT: [Type.INT, Type.STRING],
        Type.STRING: [Type.INT, Type.FLOAT, Type.BOOL],
        Type.BOOL: [Type.INT],
    }

    @staticmethod
    def is_type_match(value: Any, expected_type: Type) -> bool:
        """Check if value matches expected type."""
        if expected_type == Type.NIL:
            return value is None

        val = value if isinstance(value, GDValue) else GDValue(value)
        return val.value_type == expected_type

    @staticmethod
    def can_coerce(from_type: Type, to_type: Type) -> bool:
        """Check if type can be coerced to target type."""
        if from_type == to_type:
            return True
        return to_type in TypeValidator.COERCIBLE.get(from_type, [])

    @staticmethod
    def coerce(value: Any, target_type: Type) -> Any:
        """Coerce value to target type."""
        val = value if isinstance(value, GDValue) else GDValue(value)

        if not TypeValidator.can_coerce(val.value_type, target_type):
            raise TypeError(
                f"Cannot coerce {val.value_type.value} to {target_type.value}"
            )

        coerced = val.cast(target_type)
        return coerced.value

    @staticmethod
    def validate_array_type(array: GDArray, element_type: Type) -> bool:
        """Validate all elements in array match type."""
        for item in array.to_list():
            val = item if isinstance(item, GDValue) else GDValue(item)
            if val.value_type != element_type:
                return False
        return True

    @staticmethod
    def validate_dict_values(dictionary: GDDictionary, value_type: Type) -> bool:
        """Validate all values in dictionary match type."""
        for value in dictionary.values():
            val = value if isinstance(value, GDValue) else GDValue(value)
            if val.value_type != value_type:
                return False
        return True


class TypeSignature:
    """Function signature with type information."""

    def __init__(self, params: Dict[str, Type], return_type: Type):
        self.params = params
        self.return_type = return_type

    def validate_call(self, args: Dict[str, Any]) -> bool:
        """Validate function call arguments."""
        for param_name, param_type in self.params.items():
            if param_name not in args:
                return False
            arg_value = args[param_name]
            val = arg_value if isinstance(arg_value, GDValue) else GDValue(arg_value)
            if not TypeValidator.can_coerce(val.value_type, param_type):
                return False
        return True

    def __repr__(self) -> str:
        params_str = ", ".join(f"{k}: {v.value}" for k, v in self.params.items())
        return f"({params_str}) -> {self.return_type.value}"


class TypedFunction:
    """Function with enforced type checking."""

    def __init__(self, func: Callable, signature: TypeSignature):
        self.func = func
        self.signature = signature

    def __call__(self, *args, **kwargs) -> Any:
        """Call function with type validation."""
        # Convert positional args to kwargs
        call_args = dict(kwargs)
        param_names = list(self.signature.params.keys())
        for i, arg in enumerate(args):
            if i < len(param_names):
                call_args[param_names[i]] = arg

        # Validate arguments
        if not self.signature.validate_call(call_args):
            expected = self.signature
            raise TypeError(f"Invalid arguments for function signature {expected}")

        # Call function
        result = self.func(*args, **kwargs)

        # Validate return type
        ret_val = result if isinstance(result, GDValue) else GDValue(result)
        if not TypeValidator.can_coerce(ret_val.value_type, self.signature.return_type):
            raise TypeError(
                f"Return type mismatch: expected {self.signature.return_type.value}, "
                f"got {ret_val.value_type.value}"
            )

        return result
