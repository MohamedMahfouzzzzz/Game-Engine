# /**************************************************************************/
# /*  input_driver.py                                                       */
# /**************************************************************************/

"""Input driver abstraction.

Simplified Python port of Godot input handling.
Integrates with existing input system.
"""

from typing import Optional, Dict, List, Callable, Tuple
from dataclasses import dataclass
from enum import IntEnum
import threading


class InputDeviceType(IntEnum):
    """Input device types."""
    DEVICE_KEYBOARD = 0
    DEVICE_MOUSE = 1
    DEVICE_TOUCH = 2
    DEVICE_JOYSTICK = 3
    DEVICE_GAMEPAD = 4


@dataclass
class InputEvent:
    """Base input event."""
    device_type: InputDeviceType = InputDeviceType.DEVICE_KEYBOARD
    device_id: int = 0
    timestamp: float = 0.0
    pressed: bool = False


@dataclass
class KeyEvent(InputEvent):
    """Keyboard event."""
    keycode: int = 0
    scancode: int = 0
    unicode: int = 0
    echo: bool = False
    alt: bool = False
    shift: bool = False
    ctrl: bool = False
    meta: bool = False


@dataclass
class MouseEvent(InputEvent):
    """Mouse event."""
    button: int = 0
    x: float = 0.0
    y: float = 0.0
    relative_x: float = 0.0
    relative_y: float = 0.0
    pressure: float = 1.0
    tilt_x: float = 0.0
    tilt_y: float = 0.0


@dataclass
class TouchEvent(InputEvent):
    """Touch event."""
    finger: int = 0
    x: float = 0.0
    y: float = 0.0


@dataclass
class JoystickEvent(InputEvent):
    """Joystick/gamepad event."""
    axis: int = -1
    axis_value: float = 0.0
    button: int = -1


class InputDriver:
    """Abstract input driver."""
    
    def __init__(self, name: str = "InputDriver"):
        self._name = name
        self._initialized: bool = False
        self._event_callbacks: List[Callable[[InputEvent], None]] = []
        self._thread: Optional[threading.Thread] = None
        self._running: bool = False
    
    def get_name(self) -> str:
        return self._name
    
    def initialize(self) -> bool:
        """Initialize input driver."""
        return False
    
    def start(self) -> bool:
        """Start input polling."""
        self._running = True
        return True
    
    def stop(self) -> None:
        """Stop input polling."""
        self._running = False
    
    def poll(self) -> List[InputEvent]:
        """Poll for new input events."""
        return []
    
    def connect_event(self, callback: Callable[[InputEvent], None]) -> None:
        """Connect input event callback."""
        self._event_callbacks.append(callback)
    
    def _emit_event(self, event: InputEvent) -> None:
        """Emit event to all callbacks."""
        for callback in self._event_callbacks:
            callback(event)


class SDL2InputDriver(InputDriver):
    """SDL2-based input driver."""
    
    def __init__(self):
        super().__init__("SDL2")
        self._joysticks: Dict[int, any] = {}
    
    def initialize(self) -> bool:
        try:
            import pygame
            pygame.init()
            pygame.joystick.init()
            self._initialized = True
            return True
        except ImportError:
            return False
    
    def poll(self) -> List[InputEvent]:
        if not self._initialized:
            return []
        
        events = []
        try:
            import pygame
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pass
                elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                    key_event = KeyEvent(
                        device_type=InputDeviceType.DEVICE_KEYBOARD,
                        keycode=event.key,
                        scancode=event.scancode if hasattr(event, 'scancode') else event.key,
                        unicode=event.unicode if hasattr(event, 'unicode') else '',
                        pressed=event.type == pygame.KEYDOWN,
                        alt=bool(event.mod & pygame.KMOD_ALT),
                        shift=bool(event.mod & pygame.KMOD_SHIFT),
                        ctrl=bool(event.mod & pygame.KMOD_CTRL),
                    )
                    events.append(key_event)
                    self._emit_event(key_event)
                    
                elif event.type == pygame.MOUSEMOTION:
                    mouse_event = MouseEvent(
                        device_type=InputDeviceType.DEVICE_MOUSE,
                        x=event.pos[0],
                        y=event.pos[1],
                        relative_x=event.rel[0],
                        relative_y=event.rel[1],
                    )
                    events.append(mouse_event)
                    self._emit_event(mouse_event)
                    
                elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP:
                    mouse_event = MouseEvent(
                        device_type=InputDeviceType.DEVICE_MOUSE,
                        button=event.button,
                        x=event.pos[0],
                        y=event.pos[1],
                        pressed=event.type == pygame.MOUSEBUTTONDOWN,
                    )
                    events.append(mouse_event)
                    self._emit_event(mouse_event)
                    
                elif event.type == pygame.FINGERDOWN or event.type == pygame.FINGERUP:
                    touch_event = TouchEvent(
                        device_type=InputDeviceType.DEVICE_TOUCH,
                        finger=event.finger_id,
                        x=event.x,
                        y=event.y,
                        pressed=event.type == pygame.FINGERDOWN,
                    )
                    events.append(touch_event)
                    self._emit_event(touch_event)
                    
        except:
            pass
        
        return events


class InputManager:
    """Input manager singleton."""
    
    _instance: Optional['InputManager'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._driver: Optional[InputDriver] = None
            cls._instance._accumulated_events: List[InputEvent] = []
        return cls._instance
    
    def initialize(self, driver_name: str = "SDL2") -> bool:
        """Initialize with driver."""
        if driver_name == "SDL2":
            driver = SDL2InputDriver()
            if driver.initialize():
                self._driver = driver
                driver.start()
                return True
        return False
    
    def poll(self) -> List[InputEvent]:
        """Poll for input events."""
        if self._driver:
            return self._driver.poll()
        return []
    
    def get_driver(self) -> Optional[InputDriver]:
        return self._driver
    
    def shutdown(self) -> None:
        if self._driver:
            self._driver.stop()
            self._driver = None
