"""GD Language data types: Arrays, Dictionaries, and Values."""

from typing import Any, Optional, List, Dict, Union, TypeVar, Generic
from enum import Enum
import json


T = TypeVar('T')


class Type(Enum):
    """GD Language type enumeration."""

    NIL = "nil"
    BOOL = "bool"
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    ARRAY = "array"
    DICTIONARY = "dictionary"
    VECTOR2 = "Vector2"
    VECTOR3 = "Vector3"
    COLOR = "Color"
    OBJECT = "Object"


class GDValue:
    """Type-safe value wrapper for GD Language."""

    def __init__(self, value: Any, value_type: Optional[Type] = None):
        self.value = value
        self.value_type = value_type or self._infer_type(value)

    @staticmethod
    def _infer_type(value: Any) -> Type:
        """Infer type from Python value."""
        if value is None:
            return Type.NIL
        if isinstance(value, bool):
            return Type.BOOL
        if isinstance(value, int):
            return Type.INT
        if isinstance(value, float):
            return Type.FLOAT
        if isinstance(value, str):
            return Type.STRING
        if isinstance(value, (GDArray, list)):
            return Type.ARRAY
        if isinstance(value, (GDDictionary, dict)):
            return Type.DICTIONARY
        return Type.OBJECT

    def cast(self, target_type: Type) -> 'GDValue':
        """Cast value to target type."""
        if target_type == self.value_type:
            return GDValue(self.value, target_type)

        if target_type == Type.STRING:
            return GDValue(str(self.value), Type.STRING)
        if target_type == Type.INT:
            return GDValue(int(float(str(self.value))), Type.INT)
        if target_type == Type.FLOAT:
            return GDValue(float(self.value), Type.FLOAT)
        if target_type == Type.BOOL:
            return GDValue(bool(self.value), Type.BOOL)

        raise TypeError(f"Cannot cast {self.value_type} to {target_type}")

    def __repr__(self) -> str:
        return f"GDValue({self.value}, {self.value_type.value})"


class GDArray(Generic[T]):
    """Type-safe dynamic array for GD Language."""

    def __init__(self, items: Optional[List[T]] = None, element_type: Optional[Type] = None):
        self._items: List[T] = items or []
        self.element_type = element_type
        self._validate_items()

    def _validate_items(self) -> None:
        """Validate all items match declared type."""
        if self.element_type is None:
            return

        for item in self._items:
            if isinstance(item, GDValue):
                if item.value_type != self.element_type:
                    raise TypeError(
                        f"Array element type mismatch: expected {self.element_type.value}, "
                        f"got {item.value_type.value}"
                    )
            else:
                inferred = GDValue._infer_type(item)
                if inferred != self.element_type:
                    raise TypeError(
                        f"Array element type mismatch: expected {self.element_type.value}, "
                        f"got {inferred.value}"
                    )

    def append(self, item: T) -> None:
        """Add item to end of array."""
        if self.element_type is not None:
            value = item if isinstance(item, GDValue) else GDValue(item)
            if value.value_type != self.element_type:
                raise TypeError(
                    f"Cannot append {value.value_type.value} to "
                    f"array of {self.element_type.value}"
                )
        self._items.append(item)

    def insert(self, index: int, item: T) -> None:
        """Insert item at index."""
        if self.element_type is not None:
            value = item if isinstance(item, GDValue) else GDValue(item)
            if value.value_type != self.element_type:
                raise TypeError(f"Type mismatch for insert")
        self._items.insert(index, item)

    def erase(self, index: int) -> None:
        """Remove item at index."""
        if 0 <= index < len(self._items):
            del self._items[index]

    def remove(self, item: T) -> None:
        """Remove first occurrence of item."""
        if item in self._items:
            self._items.remove(item)

    def pop_back(self) -> Optional[T]:
        """Remove and return last item."""
        if self._items:
            return self._items.pop()
        return None

    def pop_front(self) -> Optional[T]:
        """Remove and return first item."""
        if self._items:
            return self._items.pop(0)
        return None

    def clear(self) -> None:
        """Remove all items."""
        self._items.clear()

    def size(self) -> int:
        """Get array size."""
        return len(self._items)

    def is_empty(self) -> bool:
        """Check if array is empty."""
        return len(self._items) == 0

    def get(self, index: int) -> Optional[T]:
        """Get item at index."""
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def find(self, item: T) -> int:
        """Find index of item, or -1 if not found."""
        try:
            return self._items.index(item)
        except ValueError:
            return -1

    def has(self, item: T) -> bool:
        """Check if array contains item."""
        return item in self._items

    def reverse(self) -> None:
        """Reverse array in place."""
        self._items.reverse()

    def sort(self) -> None:
        """Sort array in place."""
        self._items.sort()

    def to_list(self) -> List[T]:
        """Convert to Python list."""
        return self._items.copy()

    def to_json(self) -> str:
        """Serialize to JSON string."""
        data = []
        for item in self._items:
            if isinstance(item, (GDArray, GDDictionary)):
                data.append(json.loads(item.to_json()))
            elif isinstance(item, GDValue):
                data.append(item.value)
            else:
                data.append(item)
        return json.dumps(data)

    def __len__(self) -> int:
        return len(self._items)

    def __getitem__(self, index: int) -> T:
        return self._items[index]

    def __setitem__(self, index: int, value: T) -> None:
        if self.element_type is not None:
            val = value if isinstance(value, GDValue) else GDValue(value)
            if val.value_type != self.element_type:
                raise TypeError(f"Type mismatch on assignment")
        self._items[index] = value

    def __repr__(self) -> str:
        return f"GDArray({self._items})"


class GDDictionary:
    """Type-safe key-value dictionary for GD Language."""

    def __init__(self, items: Optional[Dict[str, Any]] = None,
                 key_type: Optional[Type] = None,
                 value_type: Optional[Type] = None):
        self._items: Dict[str, Any] = items or {}
        self.key_type = key_type or Type.STRING
        self.value_type = value_type
        self._validate_items()

    def _validate_items(self) -> None:
        """Validate all items match declared types."""
        for key, value in self._items.items():
            if self.key_type and not isinstance(key, str):
                raise TypeError(f"Dictionary key must be string")

            if self.value_type is not None:
                val = value if isinstance(value, GDValue) else GDValue(value)
                if val.value_type != self.value_type:
                    raise TypeError(
                        f"Dictionary value type mismatch: expected "
                        f"{self.value_type.value}, got {val.value_type.value}"
                    )

    def set(self, key: str, value: Any) -> None:
        """Set key-value pair."""
        if self.value_type is not None:
            val = value if isinstance(value, GDValue) else GDValue(value)
            if val.value_type != self.value_type:
                raise TypeError(f"Value type mismatch")
        self._items[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get value by key."""
        return self._items.get(key, default)

    def has(self, key: str) -> bool:
        """Check if key exists."""
        return key in self._items

    def erase(self, key: str) -> None:
        """Remove key-value pair."""
        if key in self._items:
            del self._items[key]

    def clear(self) -> None:
        """Remove all items."""
        self._items.clear()

    def size(self) -> int:
        """Get dictionary size."""
        return len(self._items)

    def is_empty(self) -> bool:
        """Check if dictionary is empty."""
        return len(self._items) == 0

    def keys(self) -> List[str]:
        """Get all keys."""
        return list(self._items.keys())

    def values(self) -> List[Any]:
        """Get all values."""
        return list(self._items.values())

    def items(self) -> List[tuple]:
        """Get all key-value pairs."""
        return list(self._items.items())

    def merge(self, other: 'GDDictionary') -> None:
        """Merge another dictionary into this one."""
        self._items.update(other._items)

    def duplicate(self) -> 'GDDictionary':
        """Create a copy of this dictionary."""
        return GDDictionary(
            self._items.copy(),
            self.key_type,
            self.value_type
        )

    def to_json(self) -> str:
        """Serialize to JSON string."""
        data = {}
        for key, value in self._items.items():
            if isinstance(value, (GDArray, GDDictionary)):
                data[key] = json.loads(value.to_json())
            elif isinstance(value, GDValue):
                data[key] = value.value
            else:
                data[key] = value
        return json.dumps(data)

    def __len__(self) -> int:
        return len(self._items)

    def __getitem__(self, key: str) -> Any:
        return self._items[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.set(key, value)

    def __contains__(self, key: str) -> bool:
        return key in self._items

    def __repr__(self) -> str:
        return f"GDDictionary({self._items})"
