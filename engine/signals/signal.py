# /**************************************************************************/
# /*  signals/signal.py                                                     */
# /**************************************************************************/

"""Signal class for emitting events to connected slots.

A Signal is an object that can be emitted with arguments,
calling all connected slots. Similar to Godot's Signal or Qt's signals.

Example:
    class Player:
        health_changed = Signal(int, int)  # old_health, new_health
        
        def take_damage(self, amount):
            old = self.health
            self.health -= amount
            self.health_changed.emit(old, self.health)
    
    # Connect from elsewhere
    player.health_changed.connect(on_health_changed)
"""

from typing import Any, Callable, List, Dict, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum, auto
from weakref import ref, ReferenceType
import threading
import inspect


class EmitMode(Enum):
    """Signal emission mode."""
    IMMEDIATE = auto()   # Call slots immediately (synchronous)
    QUEUED = auto()      # Queue for later processing
    DEFERRED = auto()    # Defer to main thread


@dataclass
class SignalEmitOptions:
    """Options for signal emission."""
    mode: EmitMode = EmitMode.IMMEDIATE
    priority: int = 0  # Higher = processed first when queued


class SignalConnection:
    """A connection between a signal and a slot.
    
    Tracks connection state and allows disconnection.
    """
    
    def __init__(self, signal: 'Signal', slot_id: int, 
                 one_shot: bool = False, 
                 priority: int = 0,
                 guard: Optional[ReferenceType] = None):
        self._signal_ref = ref(signal) if signal else None
        self._slot_id = slot_id
        self._one_shot = one_shot
        self._priority = priority
        self._guard = guard  # Weak reference to guard object (disconnect if dead)
        self._active = True
        self._blocked = False
    
    def disconnect(self) -> bool:
        """Disconnect this connection."""
        if not self._active:
            return False
        
        signal = self._signal_ref() if self._signal_ref else None
        if signal:
            signal._disconnect(self._slot_id)
        
        self._active = False
        return True
    
    def block(self) -> None:
        """Block this connection (temporarily disable)."""
        self._blocked = True
    
    def unblock(self) -> None:
        """Unblock this connection."""
        self._blocked = False
    
    @property
    def is_active(self) -> bool:
        """Check if connection is still active."""
        if not self._active:
            return False
        
        # Check guard object
        if self._guard is not None:
            if self._guard() is None:
                self._active = False
                return False
        
        return True
    
    @property
    def is_blocked(self) -> bool:
        """Check if connection is blocked."""
        return self._blocked


class Slot:
    """Base class for slots."""
    
    def __init__(self):
        self._id = id(self)
    
    @property
    def id(self) -> int:
        return self._id
    
    def call(self, *args: Any) -> Any:
        """Call the slot with arguments."""
        raise NotImplementedError
    
    def is_alive(self) -> bool:
        """Check if slot target is still alive."""
        return True


class CallableSlot(Slot):
    """A slot wrapping a callable (function or callable object)."""
    
    def __init__(self, func: Callable, *, weak: bool = False):
        super().__init__()
        self._weak = weak
        
        if weak:
            self._func_ref: Union[ReferenceType, Callable] = ref(func)
        else:
            self._func_ref = func
    
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


class MethodSlot(Slot):
    """A slot wrapping a bound method."""
    
    def __init__(self, method: Callable, *, weak: bool = True):
        super().__init__()
        self._instance_ref: ReferenceType = ref(method.__self__)
        self._func = method.__func__
        self._weak = weak
    
    def call(self, *args: Any) -> Any:
        """Call the bound method."""
        instance = self._instance_ref()
        if instance is None:
            return None
        
        return self._func(instance, *args)
    
    def is_alive(self) -> bool:
        """Check if instance is still alive."""
        return self._instance_ref() is not None


class Signal:
    """A typed signal that can be connected to slots and emitted.
    
    Similar to Godot's signal system. Supports:
    - Multiple connections
    - One-shot connections
    - Priority ordering
    - Weak references (auto-disconnect when target dies)
    - Connection blocking
    - Queued emission
    
    Example:
        class Button:
            clicked = Signal()  # No args
            
        class Slider:
            value_changed = Signal(float)  # One arg
            
        # Connect and emit
        button.clicked.connect(on_click)
        button.clicked.emit()  # Calls on_click()
    """
    
    _id_counter = 0
    _lock = threading.Lock()
    
    def __init__(self, *arg_types: type, name: str = ""):
        """Create a signal with optional argument type hints.
        
        Args:
            *arg_types: Expected argument types (for documentation/validation)
            name: Signal name (for debugging)
        """
        Signal._id_counter += 1
        self._id = Signal._id_counter
        self._name = name or f"Signal_{self._id}"
        self._arg_types = arg_types
        
        # Slot storage: slot_id -> Slot
        self._slots: Dict[int, Slot] = {}
        
        # Connection storage: slot_id -> SignalConnection
        self._connections: Dict[int, SignalConnection] = {}
        
        # Lock for thread safety
        self._lock = threading.RLock()
        
        # Emission queue (for QUEUED mode)
        self._emit_queue: List[Tuple[Tuple[Any, ...], SignalEmitOptions]] = []
    
    def connect(self, callback: Callable, *,
                one_shot: bool = False,
                priority: int = 0,
                weak: bool = True,
                guard: Optional[Any] = None) -> SignalConnection:
        """Connect a callable to this signal.
        
        Args:
            callback: Function or method to call when signal is emitted
            one_shot: If True, auto-disconnect after first emission
            priority: Higher priority = called first (default 0)
            weak: Use weak references (methods default to weak)
            guard: Optional object that keeps connection alive while it exists
        
        Returns:
            SignalConnection object for managing the connection
        """
        with self._lock:
            # Create appropriate slot type
            if inspect.ismethod(callback):
                slot = MethodSlot(callback, weak=weak)
            else:
                slot = CallableSlot(callback, weak=weak)
            
            slot_id = slot.id
            self._slots[slot_id] = slot
            
            # Create connection
            guard_ref = ref(guard) if guard is not None else None
            connection = SignalConnection(
                self, slot_id, one_shot, priority, guard_ref
            )
            
            # Insert maintaining priority order (higher priority first)
            # Convert to list, insert sorted, convert back to dict
            items = list(self._connections.items())
            items.append((slot_id, connection))
            items.sort(key=lambda x: x[1]._priority, reverse=True)
            self._connections = dict(items)
            
            return connection
    
    def disconnect(self, callback: Optional[Callable] = None) -> int:
        """Disconnect one or all callbacks.
        
        Args:
            callback: Specific callback to disconnect, or None for all
        
        Returns:
            Number of connections removed
        """
        with self._lock:
            if callback is None:
                # Disconnect all
                count = len(self._connections)
                self._slots.clear()
                self._connections.clear()
                return count
            
            # Find and disconnect specific callback
            removed = 0
            callback_id = id(callback)
            
            for slot_id, slot in list(self._slots.items()):
                # Check if this slot matches the callback
                if isinstance(slot, CallableSlot) and not slot._weak:
                    if slot._func_ref is callback:
                        self._disconnect(slot_id)
                        removed += 1
            
            return removed
    
    def _disconnect(self, slot_id: int) -> bool:
        """Internal disconnect by slot ID."""
        with self._lock:
            if slot_id in self._slots:
                del self._slots[slot_id]
                if slot_id in self._connections:
                    del self._connections[slot_id]
                return True
            return False
    
    def emit(self, *args: Any, options: Optional[SignalEmitOptions] = None) -> List[Any]:
        """Emit the signal with arguments.
        
        Args:
            *args: Arguments to pass to connected slots
            options: Optional emission options
        
        Returns:
            List of return values from slots
        """
        opts = options or SignalEmitOptions()
        
        if opts.mode == EmitMode.QUEUED:
            # Queue for later
            with self._lock:
                self._emit_queue.append((args, opts))
            return []
        
        # Immediate emission
        return self._emit_immediate(*args)
    
    def _emit_immediate(self, *args: Any) -> List[Any]:
        """Emit signal immediately (synchronous)."""
        results = []
        to_remove = []
        
        # Fast path: no connections
        if not self._connections:
            return results
        
        with self._lock:
            # Connections are maintained in priority order
            items = list(self._connections.items())
            
            for slot_id, connection in items:
                # Check if connection is valid
                if not connection.is_active:
                    to_remove.append(slot_id)
                    continue
                
                if connection.is_blocked:
                    continue
                
                # Get slot
                slot = self._slots.get(slot_id)
                if slot is None or not slot.is_alive():
                    to_remove.append(slot_id)
                    continue
                
                # Call slot
                try:
                    result = slot.call(*args)
                    results.append(result)
                except Exception as e:
                    # Log but don't stop other slots
                    print(f"Error in signal slot: {e}")
                
                # Handle one-shot
                if connection._one_shot:
                    to_remove.append(slot_id)
        
        # Clean up dead/one-shot connections
        for slot_id in to_remove:
            self._disconnect(slot_id)
        
        return results
    
    def process_queue(self) -> List[List[Any]]:
        """Process all queued emissions.
        
        Returns:
            List of results from each queued emission
        """
        with self._lock:
            queue = self._emit_queue
            self._emit_queue = []
        
        all_results = []
        for args, opts in sorted(queue, key=lambda x: x[1].priority, reverse=True):
            results = self._emit_immediate(*args)
            all_results.append(results)
        
        return all_results
    
    def block(self) -> None:
        """Block all connections (temporarily disable emission)."""
        with self._lock:
            for conn in self._connections.values():
                conn.block()
    
    def unblock(self) -> None:
        """Unblock all connections."""
        with self._lock:
            for conn in self._connections.values():
                conn.unblock()
    
    @property
    def connection_count(self) -> int:
        """Number of active connections."""
        with self._lock:
            self.prune_dead()
            return len(self._connections)

    def prune_dead(self) -> int:
        """Remove dead weak slots and inactive connections."""
        removed = 0
        for slot_id, slot in list(self._slots.items()):
            conn = self._connections.get(slot_id)
            if conn is None or not conn.is_active or not slot.is_alive():
                self._slots.pop(slot_id, None)
                self._connections.pop(slot_id, None)
                removed += 1
        return removed
    
    def __repr__(self) -> str:
        return f"Signal({self._name}, {self.connection_count} connections)"


# Decorator for class-level signals
def signal(*arg_types: type) -> Signal:
    """Decorator to create a signal attribute.
    
    Example:
        class MyClass:
            value_changed = signal(int)
    """
    return Signal(*arg_types)
