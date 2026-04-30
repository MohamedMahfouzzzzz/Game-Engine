# /**************************************************************************/
# /*  signals/slot.py                                                       */
# /**************************************************************************/

"""Slot implementations for signal connections.

Slots are callable targets that receive signal emissions.
"""

from typing import Any, Callable, Optional
from abc import ABC, abstractmethod
from weakref import ref, ReferenceType
import inspect


class Slot(ABC):
    """Abstract base class for slots.
    
    A slot is a callable target that receives signal emissions.
    """
    
    def __init__(self):
        self._id = id(self)
    
    @property
    def id(self) -> int:
        """Unique slot identifier."""
        return self._id
    
    @abstractmethod
    def call(self, *args: Any) -> Any:
        """Call the slot with arguments."""
        pass
    
    @abstractmethod
    def is_alive(self) -> bool:
        """Check if slot target is still alive."""
        pass
    
    @abstractmethod
    def get_target(self) -> Optional[Any]:
        """Get the target object (if applicable)."""
        pass


class CallableSlot(Slot):
    """A slot wrapping any callable (function, lambda, etc.).
    
    Supports both strong and weak references.
    """
    
    def __init__(self, func: Callable, *, weak: bool = False):
        """Create a callable slot.
        
        Args:
            func: The callable to wrap
            weak: If True, use weak reference (allows garbage collection)
        """
        super().__init__()
        self._weak = weak
        
        if weak:
            self._func_ref: ReferenceType = ref(func)
        else:
            self._func_ref = func
        
        self._func_name = getattr(func, '__name__', repr(func))
    
    def call(self, *args: Any) -> Any:
        """Call the wrapped function."""
        func = self._func_ref
        
        if isinstance(func, ReferenceType):
            func = func()
            if func is None:
                return None
        
        return func(*args)
    
    def is_alive(self) -> bool:
        """Check if function reference is still valid."""
        if isinstance(self._func_ref, ReferenceType):
            return self._func_ref() is not None
        return True
    
    def get_target(self) -> Optional[Any]:
        """Get the target function."""
        if isinstance(self._func_ref, ReferenceType):
            return self._func_ref()
        return self._func_ref
    
    def __repr__(self) -> str:
        return f"CallableSlot({self._func_name}, weak={self._weak})"


class MethodSlot(Slot):
    """A slot wrapping a bound method.
    
    Automatically uses weak references to the instance to avoid
    keeping objects alive just for signal connections.
    """
    
    def __init__(self, method: Callable, *, weak: bool = True):
        """Create a method slot.
        
        Args:
            method: The bound method to wrap
            weak: If True, use weak reference to instance
        """
        super().__init__()
        
        # Get method components
        self._instance = method.__self__
        self._func = method.__func__
        self._method_name = method.__func__.__name__
        self._weak = weak
        
        if weak:
            self._instance_ref: ReferenceType = ref(self._instance)
        else:
            self._instance_ref = self._instance
    
    def call(self, *args: Any) -> Any:
        """Call the bound method."""
        instance = self._instance_ref
        
        if isinstance(instance, ReferenceType):
            instance = instance()
            if instance is None:
                return None
        
        return self._func(instance, *args)
    
    def is_alive(self) -> bool:
        """Check if instance is still alive."""
        if isinstance(self._instance_ref, ReferenceType):
            return self._instance_ref() is not None
        return True
    
    def get_target(self) -> Optional[Any]:
        """Get the bound method."""
        instance = self._instance_ref
        
        if isinstance(instance, ReferenceType):
            instance = instance()
            if instance is None:
                return None
        
        return self._func.__get__(instance, type(instance))
    
    def __repr__(self) -> str:
        instance_str = "weak" if isinstance(self._instance_ref, ReferenceType) else "strong"
        return f"MethodSlot({self._method_name}, {instance_str})"


class PropertySlot(Slot):
    """A slot that sets a property/attribute on an object."""
    
    def __init__(self, obj: Any, property_name: str, *, weak: bool = True):
        """Create a property slot.
        
        Args:
            obj: The object with the property
            property_name: Name of the property to set
            weak: If True, use weak reference to object
        """
        super().__init__()
        
        self._property_name = property_name
        self._weak = weak
        
        if weak:
            self._obj_ref: ReferenceType = ref(obj)
        else:
            self._obj_ref = obj
    
    def call(self, *args: Any) -> Any:
        """Set the property to the first argument."""
        obj = self._obj_ref
        
        if isinstance(obj, ReferenceType):
            obj = obj()
            if obj is None:
                return None
        
        if args:
            setattr(obj, self._property_name, args[0])
        
        return None
    
    def is_alive(self) -> bool:
        """Check if object is still alive."""
        if isinstance(self._obj_ref, ReferenceType):
            return self._obj_ref() is not None
        return True
    
    def get_target(self) -> Optional[Any]:
        """Get the target object."""
        if isinstance(self._obj_ref, ReferenceType):
            return self._obj_ref()
        return self._obj_ref
    
    def __repr__(self) -> str:
        return f"PropertySlot({self._property_name})"


def create_slot(callback: Callable, *, weak: Optional[bool] = None) -> Slot:
    """Factory function to create appropriate slot type.
    
    Automatically detects bound methods vs other callables.
    
    Args:
        callback: The callable to wrap
        weak: Force weak/strong reference, or None for auto
    
    Returns:
        Appropriate Slot subclass instance
    """
    is_method = inspect.ismethod(callback)
    
    if weak is None:
        # Auto: methods default to weak, others to strong
        weak = is_method
    
    if is_method:
        return MethodSlot(callback, weak=weak)
    else:
        return CallableSlot(callback, weak=weak)
