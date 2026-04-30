# /**************************************************************************/
# /*  signals/signal_manager.py                                             */
# /**************************************************************************/

"""Signal manager for global and named signal management.

Provides a centralized registry for signals and signal groups.
Useful for global events and cross-component communication.
"""

from typing import Dict, Optional, List, Any, Callable
from .signal import Signal, SignalConnection


class SignalGroup:
    """A group of related signals.
    
    Useful for organizing signals by component or feature.
    """
    
    def __init__(self, name: str):
        self._name = name
        self._signals: Dict[str, Signal] = {}
    
    def add_signal(self, name: str, signal: Signal) -> Signal:
        """Add a signal to this group."""
        self._signals[name] = signal
        return signal
    
    def get_signal(self, name: str) -> Optional[Signal]:
        """Get a signal by name."""
        return self._signals.get(name)
    
    def connect(self, signal_name: str, callback: Callable, **kwargs) -> Optional[SignalConnection]:
        """Connect to a signal in this group."""
        signal = self._signals.get(signal_name)
        if signal:
            return signal.connect(callback, **kwargs)
        return None
    
    def emit(self, signal_name: str, *args: Any) -> List[Any]:
        """Emit a signal in this group."""
        signal = self._signals.get(signal_name)
        if signal:
            return signal.emit(*args)
        return []
    
    def disconnect_all(self) -> int:
        """Disconnect all signals in this group."""
        total = 0
        for signal in self._signals.values():
            total += signal.disconnect()
        return total
    
    def get_signal_names(self) -> List[str]:
        """Get list of signal names in this group."""
        return list(self._signals.keys())
    
    def __repr__(self) -> str:
        return f"SignalGroup({self._name}, {len(self._signals)} signals)"


class SignalManager:
    """Global signal manager.
    
    Provides centralized signal registry and management.
    Supports named signal groups for organization.
    
    Example:
        manager = SignalManager()
        
        # Create a global signal
        manager.add_signal("game_started", Signal())
        
        # Create a group for player events
        player_group = manager.create_group("player")
        player_group.add_signal("health_changed", Signal(int, int))
        
        # Connect and emit
        manager.connect("player.health_changed", on_health_change)
        manager.emit("player.health_changed", 100, 80)
    """
    
    _instance: Optional['SignalManager'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._signals: Dict[str, Signal] = {}
        self._groups: Dict[str, SignalGroup] = {}
        self._initialized = True
    
    @classmethod
    def get_instance(cls) -> 'SignalManager':
        """Get the singleton instance."""
        return cls()
    
    def add_signal(self, name: str, signal: Signal) -> Signal:
        """Add a global signal.
        
        Args:
            name: Unique signal name
            signal: The signal to add
        
        Returns:
            The added signal
        """
        self._signals[name] = signal
        return signal
    
    def get_signal(self, name: str) -> Optional[Signal]:
        """Get a signal by name (supports group.name syntax).
        
        Args:
            name: Signal name, optionally with group prefix (e.g., "player.health_changed")
        
        Returns:
            The signal if found, None otherwise
        """
        # Check for group syntax
        if "." in name:
            group_name, signal_name = name.split(".", 1)
            group = self._groups.get(group_name)
            if group:
                return group.get_signal(signal_name)
            return None
        
        return self._signals.get(name)
    
    def create_group(self, name: str) -> SignalGroup:
        """Create a new signal group.
        
        Args:
            name: Group name
        
        Returns:
            The created SignalGroup
        """
        group = SignalGroup(name)
        self._groups[name] = group
        return group
    
    def get_group(self, name: str) -> Optional[SignalGroup]:
        """Get a signal group by name."""
        return self._groups.get(name)
    
    def connect(self, signal_name: str, callback: Callable, **kwargs) -> Optional[SignalConnection]:
        """Connect to a signal by name.
        
        Args:
            signal_name: Name of the signal (supports group.name syntax)
            callback: Callable to connect
            **kwargs: Additional connection options
        
        Returns:
            SignalConnection if successful, None otherwise
        """
        signal = self.get_signal(signal_name)
        if signal is None and "." not in signal_name:
            signal = self.add_signal(signal_name, Signal())
        if signal:
            return signal.connect(callback, **kwargs)
        return None
    
    def emit(self, signal_name: str, *args: Any) -> List[Any]:
        """Emit a signal by name.
        
        Args:
            signal_name: Name of the signal to emit
            *args: Arguments to pass to connected slots
        
        Returns:
            List of return values from slots
        """
        signal = self.get_signal(signal_name)
        if signal:
            return signal.emit(*args)
        return []
    
    def disconnect(self, signal_name: str, callback: Optional[Callable] = None) -> int:
        """Disconnect from a signal.
        
        Args:
            signal_name: Name of the signal
            callback: Specific callback to disconnect, or None for all
        
        Returns:
            Number of connections removed
        """
        signal = self.get_signal(signal_name)
        if signal:
            return signal.disconnect(callback)
        return 0
    
    def disconnect_all(self) -> int:
        """Disconnect all signals globally."""
        total = 0
        
        for signal in self._signals.values():
            total += signal.disconnect()
        
        for group in self._groups.values():
            total += group.disconnect_all()
        
        return total

    def prune_dead(self) -> int:
        """Prune dead weak-reference connections from all managed signals."""
        total = 0
        for signal in self._signals.values():
            total += signal.prune_dead()
        for group in self._groups.values():
            for signal_name in group.get_signal_names():
                signal = group.get_signal(signal_name)
                if signal:
                    total += signal.prune_dead()
        return total

    def connection_count(self, signal_name: str) -> int:
        """Return live connection count for a managed signal."""
        signal = self.get_signal(signal_name)
        return signal.connection_count if signal else 0
    
    def get_signal_names(self) -> List[str]:
        """Get all global signal names."""
        return list(self._signals.keys())
    
    def get_group_names(self) -> List[str]:
        """Get all group names."""
        return list(self._groups.keys())
    
    def __repr__(self) -> str:
        return f"SignalManager({len(self._signals)} signals, {len(self._groups)} groups)"


# Global convenience functions
def get_signal_manager() -> SignalManager:
    """Get the global signal manager instance."""
    return SignalManager.get_instance()
