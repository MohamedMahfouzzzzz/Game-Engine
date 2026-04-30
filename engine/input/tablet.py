# /**************************************************************************/
# /*  tablet.py                                                             */
# /**************************************************************************/

"""Graphics tablet input support (Wacom, Huion, XP-Pen, etc.).

Provides pressure sensitivity, tilt, and stylus button support
for professional digital art workflows.

Features:
- Pen pressure (0.0 - 1.0)
- Tilt X/Y angles
- Stylus buttons (eraser, barrel buttons)
- Proximity detection
- Device identification
"""

from typing import Optional, Callable, List, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum, auto
import time


class TabletDeviceType(Enum):
    """Type of tablet device."""
    STYLUS = auto()        # Regular pen/stylus
    ERASER = auto()        # Eraser end of stylus
    AIRBRUSH = auto()      # Airbrush tool
    MOUSE = auto()         # Tablet mouse (puck)
    TOUCH = auto()         # Finger touch
    PAD = auto()           # Tablet pad/express keys


@dataclass
class TabletEvent:
    """A tablet/stylus input event.
    
    Contains all data from a tablet input event including
    position, pressure, tilt, and button states.
    """
    # Event type
    device_type: TabletDeviceType
    device_id: int
    
    # Position (in tablet coordinates, typically 0-1 or raw tablet units)
    x: float
    y: float
    
    # Pressure (0.0 = no pressure, 1.0 = max pressure)
    pressure: float = 0.0
    
    # Tilt angles in degrees (-90 to +90)
    tilt_x: float = 0.0  # Left/right tilt
    tilt_y: float = 0.0  # Forward/back tilt
    
    # Rotation (for supported styluses, in degrees)
    rotation: float = 0.0
    
    # Button states
    buttons: int = 0  # Bitmask of pressed buttons
    
    # Proximity (is pen near tablet)
    in_proximity: bool = True
    
    # Timestamp
    timestamp: float = 0.0
    
    # Tablet-specific raw data
    raw_data: Optional[Dict[str, Any]] = None


class TabletDevice:
    """Represents a connected graphics tablet or stylus.
    
    Tracks device capabilities and current state.
    """
    
    def __init__(self, device_id: int, name: str, 
                 device_type: TabletDeviceType = TabletDeviceType.STYLUS):
        self.device_id = device_id
        self.name = name
        self.device_type = device_type
        
        # Capabilities
        self.supports_pressure = True
        self.supports_tilt = False
        self.supports_rotation = False
        self.supports_buttons = True
        
        # Physical characteristics
        self.max_pressure = 1.0
        self.pressure_levels = 1024  # e.g., 1024 levels of pressure
        
        # Work area in tablet units
        self.work_area: Tuple[float, float, float, float] = (0, 0, 1, 1)
        
        # Current state
        self._last_event: Optional[TabletEvent] = None
        self._connected = True
    
    @property
    def is_connected(self) -> bool:
        """Check if device is connected."""
        return self._connected
    
    @property
    def last_event(self) -> Optional[TabletEvent]:
        """Get the last event from this device."""
        return self._last_event
    
    def update(self, event: TabletEvent) -> None:
        """Update device state with new event."""
        self._last_event = event
        self._connected = True
    
    def disconnect(self) -> None:
        """Mark device as disconnected."""
        self._connected = False
    
    def __repr__(self) -> str:
        return f"TabletDevice({self.name}, id={self.device_id}, {self.device_type.name})"


class TabletHandler:
    """Handler for tablet input events.
    
    Receives tablet events and processes them.
    """
    
    def handle_event(self, event: TabletEvent) -> None:
        """Process a tablet event.
        
        Override this method to handle tablet input.
        """
        pass


class TabletInputManager:
    """Manages graphics tablet input devices.
    
    Provides access to tablet devices and routes events to handlers.
    Similar to how InputManager works for keyboard/mouse.
    """
    
    _instance: Optional['TabletInputManager'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._devices: Dict[int, TabletDevice] = {}
        self._handlers: List[TabletHandler] = []
        self._event_callbacks: List[Callable[[TabletEvent], None]] = []
        
        # Event filtering
        self._pressure_threshold = 0.0  # Ignore events below this pressure
        self._smoothing_enabled = True
        self._smoothing_factor = 0.3
        
        # Last positions for smoothing
        self._last_positions: Dict[int, Tuple[float, float]] = {}
        
        self._initialized = True
    
    @classmethod
    def get_instance(cls) -> 'TabletInputManager':
        """Get the singleton instance."""
        return cls()
    
    def register_device(self, device: TabletDevice) -> None:
        """Register a tablet device."""
        self._devices[device.device_id] = device
    
    def unregister_device(self, device_id: int) -> None:
        """Unregister a tablet device."""
        if device_id in self._devices:
            self._devices[device_id].disconnect()
            del self._devices[device_id]
    
    def get_device(self, device_id: int) -> Optional[TabletDevice]:
        """Get a device by ID."""
        return self._devices.get(device_id)
    
    def get_devices(self, device_type: Optional[TabletDeviceType] = None) -> List[TabletDevice]:
        """Get all devices, optionally filtered by type."""
        devices = list(self._devices.values())
        if device_type:
            devices = [d for d in devices if d.device_type == device_type]
        return devices
    
    def add_handler(self, handler: TabletHandler) -> None:
        """Add a tablet event handler."""
        self._handlers.append(handler)
    
    def remove_handler(self, handler: TabletHandler) -> bool:
        """Remove a tablet event handler."""
        if handler in self._handlers:
            self._handlers.remove(handler)
            return True
        return False
    
    def on_event(self, callback: Callable[[TabletEvent], None]) -> None:
        """Register a callback for all tablet events."""
        self._event_callbacks.append(callback)
    
    def process_event(self, event: TabletEvent) -> None:
        """Process a tablet event from the OS/driver.
        
        This is called by the platform-specific tablet input code.
        """
        # Update device
        device = self._devices.get(event.device_id)
        if device:
            device.update(event)
        
        # Apply smoothing if enabled
        if self._smoothing_enabled and event.device_id in self._last_positions:
            last_x, last_y = self._last_positions[event.device_id]
            factor = self._smoothing_factor
            event.x = last_x * (1 - factor) + event.x * factor
            event.y = last_y * (1 - factor) + event.y * factor
        
        self._last_positions[event.device_id] = (event.x, event.y)
        
        # Filter low-pressure events
        if event.pressure < self._pressure_threshold:
            return
        
        # Notify handlers
        for handler in self._handlers:
            try:
                handler.handle_event(event)
            except Exception as e:
                print(f"Error in tablet handler: {e}")
        
        # Notify callbacks
        for callback in self._event_callbacks:
            try:
                callback(event)
            except Exception as e:
                print(f"Error in tablet callback: {e}")
    
    def set_pressure_threshold(self, threshold: float) -> None:
        """Set minimum pressure to register events (0.0-1.0)."""
        self._pressure_threshold = max(0.0, min(1.0, threshold))
    
    def set_smoothing(self, enabled: bool, factor: float = 0.3) -> None:
        """Enable/disable position smoothing.
        
        Args:
            enabled: Whether to enable smoothing
            factor: Smoothing factor (0.0 = no smoothing, 1.0 = max smoothing)
        """
        self._smoothing_enabled = enabled
        self._smoothing_factor = max(0.0, min(1.0, factor))
    
    @property
    def device_count(self) -> int:
        """Number of registered devices."""
        return len(self._devices)
    
    def has_tablet(self) -> bool:
        """Check if any tablet device is connected."""
        return any(d.is_connected for d in self._devices.values())
    
    def __repr__(self) -> str:
        connected = sum(1 for d in self._devices.values() if d.is_connected)
        return f"TabletInputManager({connected}/{len(self._devices)} devices active)"


def get_tablet_manager() -> TabletInputManager:
    """Get the global tablet input manager."""
    return TabletInputManager.get_instance()
