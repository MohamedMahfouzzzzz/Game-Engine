# /**************************************************************************/
# /*  input_events.py                                                       */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Godot Engine Input Events - Python Port

All input event classes from Godot Engine, ported to Python.
"""

from typing import Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import auto
import time

from engine.input.input_enums import (
    Key, MouseButton, JoyButton, JoyAxis, 
    InputEventType, MouseButtonMask, InputConstants
)


# =============================================================================
# Base Input Event
# =============================================================================

@dataclass
class InputEvent:
    """Base class for all input events."""
    
    device: int = 0
    timestamp: float = field(default_factory=time.time)
    _instance_id: int = field(default=0)
    
    def __post_init__(self):
        if self._instance_id == 0:
            self._instance_id = id(self)
    
    def get_instance_id(self) -> int:
        """Get unique instance identifier."""
        return self._instance_id
    
    def get_type(self) -> InputEventType:
        """Get event type."""
        return InputEventType.NONE
    
    def is_pressed(self) -> bool:
        """Check if event represents a pressed state."""
        return False
    
    def is_released(self) -> bool:
        """Check if event represents a released state."""
        return not self.is_pressed()
    
    def is_echo(self) -> bool:
        """Check if this is an echo event (key repeat)."""
        return False
    
    def is_action(self, action: str) -> bool:
        """Check if this event matches an action."""
        # Will be implemented with InputMap integration
        return False
    
    def is_action_pressed(self, action: str, exact_match: bool = False) -> bool:
        """Check if this event represents pressing an action."""
        return self.is_action(action) and self.is_pressed()
    
    def is_action_released(self, action: str, exact_match: bool = False) -> bool:
        """Check if this event represents releasing an action."""
        return self.is_action(action) and self.is_released()
    
    def get_action_strength(self, action: str) -> float:
        """Get the strength of the action (0.0-1.0)."""
        return 1.0 if self.is_action(action) and self.is_pressed() else 0.0
    
    def get_action_raw_strength(self, action: str) -> float:
        """Get the raw strength without deadzone applied."""
        return self.get_action_strength(action)
    
    def accumulate(self, other: 'InputEvent') -> bool:
        """Try to accumulate this event with another. Returns True if successful."""
        return False
    
    def duplicate(self) -> 'InputEvent':
        """Create a copy of this event."""
        raise NotImplementedError("Subclasses must implement duplicate()")


# =============================================================================
# Keyboard Event
# =============================================================================

@dataclass
class InputEventKey(InputEvent):
    """Keyboard key event."""
    
    keycode: Key = Key.NONE
    physical_keycode: Key = Key.NONE
    key_label: Key = Key.NONE
    pressed: bool = False
    echo: bool = False
    ctrl_pressed: bool = False
    shift_pressed: bool = False
    alt_pressed: bool = False
    meta_pressed: bool = False
    window_id: int = 0
    unicode: int = 0
    location: int = 0
    
    def get_type(self) -> InputEventType:
        return InputEventType.KEY
    
    def is_pressed(self) -> bool:
        return self.pressed
    
    def is_echo(self) -> bool:
        return self.echo
    
    def get_keycode(self) -> Key:
        return self.keycode
    
    def get_physical_keycode(self) -> Key:
        return self.physical_keycode
    
    def get_key_label(self) -> Key:
        return self.key_label
    
    def duplicate(self) -> 'InputEventKey':
        return InputEventKey(
            device=self.device,
            keycode=self.keycode,
            physical_keycode=self.physical_keycode,
            key_label=self.key_label,
            pressed=self.pressed,
            echo=self.echo,
            ctrl_pressed=self.ctrl_pressed,
            shift_pressed=self.shift_pressed,
            alt_pressed=self.alt_pressed,
            meta_pressed=self.meta_pressed,
            window_id=self.window_id,
            unicode=self.unicode,
            location=self.location
        )


# =============================================================================
# Mouse Button Event
# =============================================================================

@dataclass
class InputEventMouseButton(InputEvent):
    """Mouse button click event."""
    
    button_index: MouseButton = MouseButton.LEFT
    pressed: bool = False
    canceled: bool = False
    double_click: bool = False
    position: Tuple[float, float] = (0.0, 0.0)
    global_position: Tuple[float, float] = (0.0, 0.0)
    button_mask: int = 0  # BitField<MouseButtonMask>
    window_id: int = 0
    
    def get_type(self) -> InputEventType:
        return InputEventType.MOUSE_BUTTON
    
    def is_pressed(self) -> bool:
        return self.pressed
    
    def is_canceled(self) -> bool:
        return self.canceled
    
    def is_double_click(self) -> bool:
        return self.double_click
    
    def get_button_index(self) -> MouseButton:
        return self.button_index
    
    def get_position(self) -> Tuple[float, float]:
        return self.position
    
    def get_global_position(self) -> Tuple[float, float]:
        return self.global_position
    
    def get_button_mask(self) -> int:
        return self.button_mask
    
    def duplicate(self) -> 'InputEventMouseButton':
        return InputEventMouseButton(
            device=self.device,
            button_index=self.button_index,
            pressed=self.pressed,
            canceled=self.canceled,
            double_click=self.double_click,
            position=self.position,
            global_position=self.global_position,
            button_mask=self.button_mask,
            window_id=self.window_id
        )


# =============================================================================
# Mouse Motion Event
# =============================================================================

@dataclass
class InputEventMouseMotion(InputEvent):
    """Mouse movement event."""
    
    position: Tuple[float, float] = (0.0, 0.0)
    global_position: Tuple[float, float] = (0.0, 0.0)
    relative: Tuple[float, float] = (0.0, 0.0)
    relative_screen_position: Tuple[float, float] = (0.0, 0.0)
    velocity: Tuple[float, float] = (0.0, 0.0)
    screen_velocity: Tuple[float, float] = (0.0, 0.0)
    button_mask: int = 0  # BitField<MouseButtonMask>
    pressure: float = 0.0
    tilt: Tuple[float, float] = (0.0, 0.0)
    pen_inverted: bool = False
    window_id: int = 0
    
    def get_type(self) -> InputEventType:
        return InputEventType.MOUSE_MOTION
    
    def get_position(self) -> Tuple[float, float]:
        return self.position
    
    def get_global_position(self) -> Tuple[float, float]:
        return self.global_position
    
    def get_relative(self) -> Tuple[float, float]:
        return self.relative
    
    def get_relative_screen_position(self) -> Tuple[float, float]:
        return self.relative_screen_position
    
    def get_velocity(self) -> Tuple[float, float]:
        return self.velocity
    
    def get_screen_velocity(self) -> Tuple[float, float]:
        return self.screen_velocity
    
    def get_button_mask(self) -> int:
        return self.button_mask
    
    def get_pressure(self) -> float:
        return self.pressure
    
    def get_tilt(self) -> Tuple[float, float]:
        return self.tilt
    
    def get_pen_inverted(self) -> bool:
        return self.pen_inverted
    
    def accumulate(self, other: 'InputEvent') -> bool:
        """Accumulate mouse motion events."""
        if not isinstance(other, InputEventMouseMotion):
            return False
        if other.device != self.device or other.window_id != self.window_id:
            return False
        if other.button_mask != self.button_mask:
            return False
        
        # Accumulate relative movement
        self.relative = (
            self.relative[0] + other.relative[0],
            self.relative[1] + other.relative[1]
        )
        self.relative_screen_position = (
            self.relative_screen_position[0] + other.relative_screen_position[0],
            self.relative_screen_position[1] + other.relative_screen_position[1]
        )
        
        # Update to latest position
        self.position = other.position
        self.global_position = other.global_position
        self.velocity = other.velocity
        self.screen_velocity = other.screen_velocity
        self.pressure = other.pressure
        self.tilt = other.tilt
        self.pen_inverted = other.pen_inverted
        
        return True
    
    def duplicate(self) -> 'InputEventMouseMotion':
        return InputEventMouseMotion(
            device=self.device,
            position=self.position,
            global_position=self.global_position,
            relative=self.relative,
            relative_screen_position=self.relative_screen_position,
            velocity=self.velocity,
            screen_velocity=self.screen_velocity,
            button_mask=self.button_mask,
            pressure=self.pressure,
            tilt=self.tilt,
            pen_inverted=self.pen_inverted,
            window_id=self.window_id
        )


# =============================================================================
# Touch Screen Event
# =============================================================================

@dataclass
class InputEventScreenTouch(InputEvent):
    """Touch screen tap event."""
    
    index: int = 0  # Finger index
    pressed: bool = False
    canceled: bool = False
    double_tap: bool = False
    position: Tuple[float, float] = (0.0, 0.0)
    window_id: int = 0
    
    def get_type(self) -> InputEventType:
        return InputEventType.SCREEN_TOUCH
    
    def is_pressed(self) -> bool:
        return self.pressed
    
    def is_canceled(self) -> bool:
        return self.canceled
    
    def is_double_tap(self) -> bool:
        return self.double_tap
    
    def get_index(self) -> int:
        return self.index
    
    def get_position(self) -> Tuple[float, float]:
        return self.position
    
    def duplicate(self) -> 'InputEventScreenTouch':
        return InputEventScreenTouch(
            device=self.device,
            index=self.index,
            pressed=self.pressed,
            canceled=self.canceled,
            double_tap=self.double_tap,
            position=self.position,
            window_id=self.window_id
        )


# =============================================================================
# Screen Drag Event
# =============================================================================

@dataclass
class InputEventScreenDrag(InputEvent):
    """Touch screen drag event."""
    
    index: int = 0  # Finger index
    position: Tuple[float, float] = (0.0, 0.0)
    relative: Tuple[float, float] = (0.0, 0.0)
    relative_screen_position: Tuple[float, float] = (0.0, 0.0)
    velocity: Tuple[float, float] = (0.0, 0.0)
    screen_velocity: Tuple[float, float] = (0.0, 0.0)
    pressure: float = 0.0
    tilt: Tuple[float, float] = (0.0, 0.0)
    pen_inverted: bool = False
    window_id: int = 0
    
    def get_type(self) -> InputEventType:
        return InputEventType.SCREEN_DRAG
    
    def get_index(self) -> int:
        return self.index
    
    def get_position(self) -> Tuple[float, float]:
        return self.position
    
    def get_relative(self) -> Tuple[float, float]:
        return self.relative
    
    def get_relative_screen_position(self) -> Tuple[float, float]:
        return self.relative_screen_position
    
    def get_velocity(self) -> Tuple[float, float]:
        return self.velocity
    
    def get_screen_velocity(self) -> Tuple[float, float]:
        return self.screen_velocity
    
    def get_pressure(self) -> float:
        return self.pressure
    
    def get_tilt(self) -> Tuple[float, float]:
        return self.tilt
    
    def get_pen_inverted(self) -> bool:
        return self.pen_inverted
    
    def set_velocity(self, velocity: Tuple[float, float]) -> None:
        self.velocity = velocity
    
    def set_screen_velocity(self, velocity: Tuple[float, float]) -> None:
        self.screen_velocity = velocity
    
    def accumulate(self, other: 'InputEvent') -> bool:
        """Accumulate drag events for the same finger."""
        if not isinstance(other, InputEventScreenDrag):
            return False
        if other.device != self.device or other.window_id != self.window_id:
            return False
        if other.index != self.index:
            return False
        
        # Accumulate relative movement
        self.relative = (
            self.relative[0] + other.relative[0],
            self.relative[1] + other.relative[1]
        )
        self.relative_screen_position = (
            self.relative_screen_position[0] + other.relative_screen_position[0],
            self.relative_screen_position[1] + other.relative_screen_position[1]
        )
        
        # Update to latest position
        self.position = other.position
        self.velocity = other.velocity
        self.screen_velocity = other.screen_velocity
        self.pressure = other.pressure
        self.tilt = other.tilt
        self.pen_inverted = other.pen_inverted
        
        return True
    
    def duplicate(self) -> 'InputEventScreenDrag':
        return InputEventScreenDrag(
            device=self.device,
            index=self.index,
            position=self.position,
            relative=self.relative,
            relative_screen_position=self.relative_screen_position,
            velocity=self.velocity,
            screen_velocity=self.screen_velocity,
            pressure=self.pressure,
            tilt=self.tilt,
            pen_inverted=self.pen_inverted,
            window_id=self.window_id
        )


# =============================================================================
# Joypad Button Event
# =============================================================================

@dataclass
class InputEventJoypadButton(InputEvent):
    """Gamepad button event."""
    
    button_index: JoyButton = JoyButton.INVALID
    pressed: bool = False
    pressure: float = 0.0
    window_id: int = 0
    
    def get_type(self) -> InputEventType:
        return InputEventType.JOY_BUTTON
    
    def is_pressed(self) -> bool:
        return self.pressed
    
    def get_button_index(self) -> JoyButton:
        return self.button_index
    
    def get_pressure(self) -> float:
        return self.pressure
    
    def duplicate(self) -> 'InputEventJoypadButton':
        return InputEventJoypadButton(
            device=self.device,
            button_index=self.button_index,
            pressed=self.pressed,
            pressure=self.pressure,
            window_id=self.window_id
        )


# =============================================================================
# Joypad Motion Event
# =============================================================================

@dataclass
class InputEventJoypadMotion(InputEvent):
    """Gamepad axis/analog stick event."""
    
    axis: JoyAxis = JoyAxis.INVALID
    axis_value: float = 0.0  # Range: -1.0 to 1.0
    window_id: int = 0
    
    def get_type(self) -> InputEventType:
        return InputEventType.JOY_MOTION
    
    def get_axis(self) -> JoyAxis:
        return self.axis
    
    def get_axis_value(self) -> float:
        return self.axis_value
    
    def duplicate(self) -> 'InputEventJoypadMotion':
        return InputEventJoypadMotion(
            device=self.device,
            axis=self.axis,
            axis_value=self.axis_value,
            window_id=self.window_id
        )


# =============================================================================
# Gesture Event
# =============================================================================

@dataclass
class InputEventGesture(InputEvent):
    """Gesture event (pinch, zoom, etc.)."""
    
    gesture_type: str = ""  # "pinch", "zoom", "rotate", etc.
    scale: float = 1.0
    rotation: float = 0.0
    position: Tuple[float, float] = (0.0, 0.0)
    window_id: int = 0
    
    def get_type(self) -> InputEventType:
        return InputEventType.GESTURE
    
    def get_gesture_type(self) -> str:
        return self.gesture_type
    
    def get_scale(self) -> float:
        return self.scale
    
    def get_rotation(self) -> float:
        return self.rotation
    
    def get_position(self) -> Tuple[float, float]:
        return self.position
    
    def duplicate(self) -> 'InputEventGesture':
        return InputEventGesture(
            device=self.device,
            gesture_type=self.gesture_type,
            scale=self.scale,
            rotation=self.rotation,
            position=self.position,
            window_id=self.window_id
        )


# =============================================================================
# Action Event
# =============================================================================

@dataclass
class InputEventAction(InputEvent):
    """Virtual action event (programmatically generated)."""
    
    action: str = ""
    pressed: bool = False
    strength: float = 1.0
    
    def get_type(self) -> InputEventType:
        return InputEventType.ACTION
    
    def is_pressed(self) -> bool:
        return self.pressed
    
    def get_action(self) -> str:
        return self.action
    
    def get_strength(self) -> float:
        return self.strength
    
    def duplicate(self) -> 'InputEventAction':
        return InputEventAction(
            device=self.device,
            action=self.action,
            pressed=self.pressed,
            strength=self.strength
        )


# =============================================================================
# Helper Functions
# =============================================================================

def mouse_button_to_mask(button: MouseButton) -> int:
    """Convert MouseButton to MouseButtonMask bit."""
    if button == MouseButton.LEFT:
        return MouseButtonMask.LEFT
    elif button == MouseButton.RIGHT:
        return MouseButtonMask.RIGHT
    elif button == MouseButton.MIDDLE:
        return MouseButtonMask.MIDDLE
    elif button == MouseButton.WHEEL_UP:
        return MouseButtonMask.WHEEL_UP
    elif button == MouseButton.WHEEL_DOWN:
        return MouseButtonMask.WHEEL_DOWN
    elif button == MouseButton.WHEEL_LEFT:
        return MouseButtonMask.WHEEL_LEFT
    elif button == MouseButton.WHEEL_RIGHT:
        return MouseButtonMask.WHEEL_RIGHT
    elif button == MouseButton.XBUTTON1:
        return MouseButtonMask.XBUTTON1
    elif button == MouseButton.XBUTTON2:
        return MouseButtonMask.XBUTTON2
    return 0
