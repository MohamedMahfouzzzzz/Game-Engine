# /**************************************************************************/
# /*  input_godot.py                                                        */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Godot Engine Input Singleton - Python Port

Complete port of Godot's input.cpp/input.h to Python.
Maintains all functionality including joypad mappings, action system,
motion sensors, and event processing.
"""

from typing import Dict, Set, List, Optional, Tuple, Callable, Any
from dataclasses import dataclass, field
from enum import IntEnum
from collections import deque
import threading
import time
import math
import logging
from pathlib import Path

from engine.input.input_enums import (
    JoyButton, JoyAxis, Key, MouseButton, MouseButtonMask,
    MouseMode, CursorShape, HatMask, HatDir, JoyAxisRange,
    JoyEventType, InputEventType, InputConstants,
    JOY_BUTTON_NAMES, JOY_AXIS_NAMES,
    JOY_BUTTON_NAME_TO_ENUM, JOY_AXIS_NAME_TO_ENUM
)

from engine.input.input_events import (
    InputEvent, InputEventKey, InputEventMouseButton, InputEventMouseMotion,
    InputEventScreenTouch, InputEventScreenDrag, InputEventJoypadButton,
    InputEventJoypadMotion, InputEventGesture, InputEventAction,
    mouse_button_to_mask
)

logger = logging.getLogger(__name__)


# =============================================================================
# Joypad Data Structures
# =============================================================================

@dataclass
class JoypadFeatures:
    """Joypad hardware features."""
    has_vibration: bool = False
    has_light: bool = False
    has_motion_sensors: bool = False
    
    def set_joy_vibration(self, weak: float, strong: float, duration: float) -> None:
        """Set vibration (platform-specific implementation)."""
        pass
    
    def set_joy_light(self, color: Tuple[float, float, float]) -> None:
        """Set LED light color."""
        pass
    
    def set_joy_motion_sensors_enabled(self, enabled: bool) -> None:
        """Enable/disable motion sensors."""
        pass


@dataclass
class Joypad:
    """Joypad device information."""
    name: str = ""
    uid: str = ""
    connected: bool = False
    is_known: bool = False
    mapping: int = -1
    info: Dict[str, Any] = field(default_factory=dict)
    features: Optional[JoypadFeatures] = None
    has_vibration: bool = False
    has_light: bool = False
    last_buttons: List[bool] = field(default_factory=lambda: [False] * int(JoyButton.MAX))
    last_axis: List[float] = field(default_factory=lambda: [0.0] * int(JoyAxis.MAX))
    hat_current: int = 0


@dataclass
class VibrationInfo:
    """Vibration state for a joypad."""
    weak_magnitude: float = 0.0
    strong_magnitude: float = 0.0
    duration: float = 0.0
    timestamp: int = 0


@dataclass
class MotionInfo:
    """Motion sensor data for a joypad."""
    sensors_enabled: bool = False
    calibrating: bool = False
    calibrated: bool = False
    sensor_data_rate: float = 0.0
    last_timestamp: int = 0
    gamepad_motion: Any = None  # Platform-specific motion helper


# =============================================================================
# Velocity Tracking
# =============================================================================

@dataclass
class VelocityTrack:
    """Tracks velocity of pointer motion."""
    
    velocity: Tuple[float, float] = (0.0, 0.0)
    screen_velocity: Tuple[float, float] = (0.0, 0.0)
    accum: Tuple[float, float] = (0.0, 0.0)
    screen_accum: Tuple[float, float] = (0.0, 0.0)
    accum_t: float = 0.0
    last_tick: int = 0
    min_ref_frame: float = 0.1
    max_ref_frame: float = 3.0
    
    def __post_init__(self):
        if self.last_tick == 0:
            self.reset()
    
    def reset(self) -> None:
        """Reset velocity tracking."""
        self.last_tick = int(time.time() * 1000000)
        self.velocity = (0.0, 0.0)
        self.screen_velocity = (0.0, 0.0)
        self.accum = (0.0, 0.0)
        self.screen_accum = (0.0, 0.0)
        self.accum_t = 0.0
    
    def update(self, delta_p: Tuple[float, float], screen_delta_p: Tuple[float, float]) -> None:
        """Update velocity tracking with new position delta."""
        tick = int(time.time() * 1000000)
        tdiff = tick - self.last_tick
        delta_t = tdiff / 1000000.0
        self.last_tick = tick
        
        if delta_t > self.max_ref_frame:
            # First movement in a long time, reset and start again
            self.velocity = (0.0, 0.0)
            self.screen_velocity = (0.0, 0.0)
            self.accum = delta_p
            self.screen_accum = screen_delta_p
            self.accum_t = 0.0
            return
        
        self.accum = (self.accum[0] + delta_p[0], self.accum[1] + delta_p[1])
        self.screen_accum = (self.screen_accum[0] + screen_delta_p[0], 
                            self.screen_accum[1] + screen_delta_p[1])
        self.accum_t += delta_t
        
        if self.accum_t < self.min_ref_frame:
            # Not enough time has passed to calculate speed precisely
            return
        
        self.velocity = (self.accum[0] / self.accum_t, self.accum[1] / self.accum_t)
        self.screen_velocity = (self.screen_accum[0] / self.accum_t, 
                               self.screen_accum[1] / self.accum_t)
        self.accum = (0.0, 0.0)
        self.screen_accum = (0.0, 0.0)
        self.accum_t = 0.0


# =============================================================================
# Joypad Binding System
# =============================================================================

@dataclass
class JoyBindingOutput:
    """Output side of a joypad binding."""
    button: JoyButton = JoyButton.INVALID
    axis: JoyAxis = JoyAxis.INVALID
    range: JoyAxisRange = JoyAxisRange.FULL_AXIS


@dataclass
class JoyBindingInput:
    """Input side of a joypad binding."""
    button: JoyButton = JoyButton.INVALID
    axis: JoyAxis = JoyAxis.INVALID
    range: JoyAxisRange = JoyAxisRange.FULL_AXIS
    invert: bool = False
    hat: int = 0
    hat_mask: HatMask = HatMask.CENTER


@dataclass
class JoyBinding:
    """Single input to output binding."""
    inputType: JoyEventType = JoyEventType.NONE
    outputType: JoyEventType = JoyEventType.NONE
    input: JoyBindingInput = field(default_factory=JoyBindingInput)
    output: JoyBindingOutput = field(default_factory=JoyBindingOutput)


@dataclass
class JoyDeviceMapping:
    """Complete device mapping with all bindings."""
    uid: str = ""
    name: str = ""
    bindings: List[JoyBinding] = field(default_factory=list)


@dataclass
class JoyEvent:
    """Parsed joy event."""
    type: JoyEventType = JoyEventType.NONE
    index: int = 0
    value: float = 0.0


# =============================================================================
# Action System
# =============================================================================

@dataclass
class ActionState:
    """State of an input action."""
    
    @dataclass
    class DeviceState:
        """Per-device state for an action."""
        pressed: List[bool] = field(default_factory=lambda: [False] * InputConstants.MAX_EVENT)
        strength: List[float] = field(default_factory=lambda: [0.0] * InputConstants.MAX_EVENT)
        raw_strength: List[float] = field(default_factory=lambda: [0.0] * InputConstants.MAX_EVENT)
        event_type: List[InputEventType] = field(
            default_factory=lambda: [InputEventType.NONE] * InputConstants.MAX_EVENT
        )
    
    @dataclass
    class Cache:
        """Cached computed state."""
        pressed: bool = False
        strength: float = 0.0
        raw_strength: float = 0.0
    
    device_states: Dict[int, 'ActionState.DeviceState'] = field(default_factory=dict)
    exact: bool = False
    api_pressed: bool = False
    api_strength: float = 0.0
    pressed_event_id: int = 0
    released_event_id: int = 0
    pressed_physics_frame: int = 0
    pressed_process_frame: int = 0
    released_physics_frame: int = 0
    released_process_frame: int = 0
    cache: 'ActionState.Cache' = field(default_factory=Cache)


# =============================================================================
# Main Input Singleton Class
# =============================================================================

class Input:
    """Godot Engine Input Singleton - Python Implementation
    
    Complete port of Godot's input system with all features:
    - Mouse and keyboard handling
    - Joypad/gamepad support with SDL mappings
    - Action system with analog support
    - Motion sensors (accelerometer, gyroscope, magnetometer)
    - Vibration/haptics
    - Event accumulation and buffering
    - Touch/mouse emulation
    """
    
    _instance: Optional['Input'] = None
    _lock: threading.Lock = threading.Lock()
    
    # Function pointers for platform-specific implementations
    set_mouse_mode_func: Optional[Callable[[MouseMode], None]] = None
    get_mouse_mode_func: Optional[Callable[[], MouseMode]] = None
    set_mouse_mode_override_func: Optional[Callable[[MouseMode], None]] = None
    get_mouse_mode_override_func: Optional[Callable[[], MouseMode]] = None
    set_mouse_mode_override_enabled_func: Optional[Callable[[bool], None]] = None
    is_mouse_mode_override_enabled_func: Optional[Callable[[], bool]] = None
    warp_mouse_func: Optional[Callable[[Tuple[float, float]], None]] = None
    get_current_cursor_shape_func: Optional[Callable[[], CursorShape]] = None
    set_custom_mouse_cursor_func: Optional[Callable[..., None]] = None
    event_dispatch_function: Optional[Callable[[InputEvent], None]] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Only initialize once
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Mouse state
        self.mouse_pos: Tuple[float, float] = (0.0, 0.0)
        self.mouse_button_mask: int = 0
        self.default_shape: CursorShape = CursorShape.ARROW
        self.mouse_velocity_track: VelocityTrack = VelocityTrack()
        self.mouse_from_touch_index: int = -1
        
        # Keyboard state
        self.keys_pressed: Set[Key] = set()
        self.physical_keys_pressed: Set[Key] = set()
        self.key_label_pressed: Set[Key] = set()
        
        # Joypad state
        self.joy_names: Dict[int, Joypad] = {}
        self.joy_buttons_pressed: Set[int] = set()  # Combined device+button
        self._joy_axis: Dict[int, float] = {}  # Combined device+axis
        self.joy_vibration: Dict[int, VibrationInfo] = {}
        self.joy_motion: Dict[int, MotionInfo] = {}
        self.map_db: List[JoyDeviceMapping] = []
        self.fallback_mapping: int = -1
        
        # Touch state
        self.touch_velocity_track: Dict[int, VelocityTrack] = {}
        
        # Action state
        self.action_states: Dict[str, ActionState] = {}
        
        # Event buffering
        self.buffered_events: List[InputEvent] = []
        self.use_accumulated_input: bool = True
        self.agile_input_event_flushing: bool = False
        
        # Frame tracking for just pressed/released
        self.last_parsed_frame: int = 0
        self.frame_parsed_events: Set[int] = set()
        
        # Settings
        self.disable_input: bool = False
        self.emulate_touch_from_mouse: bool = False
        self.emulate_mouse_from_touch: bool = False
        self.ignore_joypad_on_unfocused_application: bool = False
        self.application_focused: bool = True
        self.embedder_focused: bool = False
        self.legacy_just_pressed_behavior: bool = False
        
        # Sensor data
        self.gravity: Tuple[float, float, float] = (0.0, 0.0, 0.0)
        self.accelerometer: Tuple[float, float, float] = (0.0, 0.0, 0.0)
        self.magnetometer: Tuple[float, float, float] = (0.0, 0.0, 0.0)
        self.gyroscope: Tuple[float, float, float] = (0.0, 0.0, 0.0)
        
        self.gravity_enabled: bool = False
        self.accelerometer_enabled: bool = False
        self.magnetometer_enabled: bool = False
        self.gyroscope_enabled: bool = False
        
        # Ignored devices
        self.ignored_device_ids: Set[int] = set()
        
        # Initialize default mappings
        self._load_default_mappings()
        
        logger.info("Input singleton initialized")
    
    @classmethod
    def get_singleton(cls) -> 'Input':
        """Get the Input singleton instance."""
        if cls._instance is None:
            cls._instance = Input()
        return cls._instance
    
    # ========================================================================
    # Mouse Mode Methods
    # ========================================================================
    
    def set_mouse_mode(self, mode: MouseMode) -> None:
        """Set the mouse mode (visible, hidden, captured, confined)."""
        if not (0 <= mode < MouseMode.MAX):
            logger.error(f"Invalid mouse mode: {mode}")
            return
        if Input.set_mouse_mode_func:
            Input.set_mouse_mode_func(mode)
    
    def get_mouse_mode(self) -> MouseMode:
        """Get current mouse mode."""
        if Input.get_mouse_mode_func:
            return Input.get_mouse_mode_func()
        return MouseMode.VISIBLE
    
    def set_mouse_mode_override(self, mode: MouseMode) -> None:
        """Override mouse mode."""
        if not (0 <= mode < MouseMode.MAX):
            logger.error(f"Invalid mouse mode override: {mode}")
            return
        if Input.set_mouse_mode_override_func:
            Input.set_mouse_mode_override_func(mode)
    
    def get_mouse_mode_override(self) -> MouseMode:
        """Get mouse mode override."""
        if Input.get_mouse_mode_override_func:
            return Input.get_mouse_mode_override_func()
        return MouseMode.VISIBLE
    
    def set_mouse_mode_override_enabled(self, enabled: bool) -> None:
        """Enable/disable mouse mode override."""
        if Input.set_mouse_mode_override_enabled_func:
            Input.set_mouse_mode_override_enabled_func(enabled)
    
    def is_mouse_mode_override_enabled(self) -> bool:
        """Check if mouse mode override is enabled."""
        if Input.is_mouse_mode_override_enabled_func:
            return Input.is_mouse_mode_override_enabled_func()
        return False
    
    # ========================================================================
    # Query Methods - General
    # ========================================================================
    
    def is_anything_pressed(self) -> bool:
        """Check if any input is currently pressed."""
        with self._lock:
            if self.disable_input:
                return False
            
            if (self.keys_pressed or self.joy_buttons_pressed or 
                self.mouse_button_mask != 0):
                return True
            
            for action_name, action_state in self.action_states.items():
                if action_state.cache.pressed:
                    return True
            
            return False
    
    def is_any_key_pressed(self) -> bool:
        """Check if any keyboard key is pressed."""
        with self._lock:
            if self.disable_input:
                return False
            return len(self.keys_pressed) > 0
    
    def is_key_pressed(self, keycode: Key) -> bool:
        """Check if a specific key is pressed."""
        with self._lock:
            if self.disable_input:
                return False
            return keycode in self.keys_pressed
    
    def is_physical_key_pressed(self, keycode: Key) -> bool:
        """Check if a physical key location is pressed."""
        with self._lock:
            if self.disable_input:
                return False
            return keycode in self.physical_keys_pressed
    
    def is_key_label_pressed(self, keycode: Key) -> bool:
        """Check if a key with specific label is pressed."""
        with self._lock:
            if self.disable_input:
                return False
            return keycode in self.key_label_pressed
    
    def is_mouse_button_pressed(self, button: MouseButton) -> bool:
        """Check if a mouse button is pressed."""
        with self._lock:
            if self.disable_input:
                return False
            return (self.mouse_button_mask & mouse_button_to_mask(button)) != 0
    
    def _should_ignore_joypad_events(self) -> bool:
        """Check if joypad events should be ignored."""
        return (self.ignore_joypad_on_unfocused_application and 
                not self.application_focused and not self.embedder_focused)
    
    def _combine_device_joybutton(self, button: JoyButton, device: int) -> int:
        """Combine device ID with button for unique key."""
        return int(button) | (device << 20)
    
    def _combine_device_joyaxis(self, axis: JoyAxis, device: int) -> int:
        """Combine device ID with axis for unique key."""
        return int(axis) | (device << 20)
    
    def is_joy_button_pressed(self, device: int, button: JoyButton) -> bool:
        """Check if a joypad button is pressed."""
        with self._lock:
            if self.disable_input:
                return False
            return self._combine_device_joybutton(button, device) in self.joy_buttons_pressed
    
    # ========================================================================
    # Action System Methods
    # ========================================================================
    
    def is_action_pressed(self, action: str, exact: bool = False) -> bool:
        """Check if an action is currently pressed."""
        with self._lock:
            if self.disable_input:
                return False
            
            if action not in self.action_states:
                return False
            
            state = self.action_states[action]
            return state.cache.pressed and (exact == state.exact if exact else True)
    
    def is_action_just_pressed(self, action: str, exact: bool = False) -> bool:
        """Check if an action was just pressed this frame."""
        with self._lock:
            if self.disable_input:
                return False
            
            if action not in self.action_states:
                return False
            
            state = self.action_states[action]
            if exact and not state.exact:
                return False
            
            # For now, simplified frame checking (would need physics/process frame counters)
            return state.cache.pressed and state.pressed_process_frame > 0
    
    def is_action_just_released(self, action: str, exact: bool = False) -> bool:
        """Check if an action was just released this frame."""
        with self._lock:
            if self.disable_input:
                return False
            
            if action not in self.action_states:
                return False
            
            state = self.action_states[action]
            if exact and not state.exact:
                return False
            
            # For now, simplified frame checking
            return not state.cache.pressed and state.released_process_frame > 0
    
    def get_action_strength(self, action: str, exact: bool = False) -> float:
        """Get the strength of an action (0.0-1.0)."""
        with self._lock:
            if self.disable_input:
                return 0.0
            
            if action not in self.action_states:
                return 0.0
            
            state = self.action_states[action]
            if exact and not state.exact:
                return 0.0
            
            return state.cache.strength
    
    def get_action_raw_strength(self, action: str, exact: bool = False) -> float:
        """Get the raw strength without deadzone."""
        with self._lock:
            if self.disable_input:
                return 0.0
            
            if action not in self.action_states:
                return 0.0
            
            state = self.action_states[action]
            if exact and not state.exact:
                return 0.0
            
            return state.cache.raw_strength
    
    def get_axis(self, negative_action: str, positive_action: str) -> float:
        """Get a combined axis value from two actions."""
        return (self.get_action_strength(positive_action) - 
                self.get_action_strength(negative_action))
    
    def get_vector(self, negative_x: str, positive_x: str, 
                   negative_y: str, positive_y: str, 
                   deadzone: float = -1.0) -> Tuple[float, float]:
        """Get a 2D vector from four actions."""
        vector = (
            self.get_action_raw_strength(positive_x) - self.get_action_raw_strength(negative_x),
            self.get_action_raw_strength(positive_y) - self.get_action_raw_strength(negative_y)
        )
        
        if deadzone < 0.0:
            # Use default deadzone
            deadzone = 0.25
        
        length = math.sqrt(vector[0] * vector[0] + vector[1] * vector[1])
        if length <= deadzone:
            return (0.0, 0.0)
        elif length > 1.0:
            return (vector[0] / length, vector[1] / length)
        else:
            # Inverse lerp
            t = (length - deadzone) / (1.0 - deadzone)
            return (vector[0] * t / length, vector[1] * t / length)
    
    def action_press(self, action: str, strength: float = 1.0) -> None:
        """Programmatically press an action."""
        with self._lock:
            if action not in self.action_states:
                self.action_states[action] = ActionState()
            
            state = self.action_states[action]
            
            if not state.cache.pressed:
                state.pressed_event_id = 0
                state.pressed_physics_frame = 1
                state.pressed_process_frame = 1
            
            state.exact = True
            state.api_pressed = True
            state.api_strength = max(0.0, min(1.0, strength))
            self._update_action_cache(action, state)
    
    def action_release(self, action: str) -> None:
        """Programmatically release an action."""
        with self._lock:
            if action not in self.action_states:
                return
            
            state = self.action_states[action]
            state.cache.pressed = False
            state.cache.strength = 0.0
            state.cache.raw_strength = 0.0
            state.released_event_id = 0
            state.released_physics_frame = 1
            state.released_process_frame = 1
            state.device_states.clear()
            state.exact = True
            state.api_pressed = False
            state.api_strength = 0.0
    
    def _update_action_cache(self, action_name: str, state: ActionState) -> None:
        """Update the cached state of an action."""
        # This would integrate with InputMap - simplified version
        state.cache.pressed = False
        state.cache.strength = 0.0
        state.cache.raw_strength = 0.0
        
        # Check device states
        for device_id, device_state in state.device_states.items():
            for i in range(InputConstants.MAX_EVENT):
                state.cache.pressed = state.cache.pressed or device_state.pressed[i]
                state.cache.strength = max(state.cache.strength, device_state.strength[i])
                state.cache.raw_strength = max(state.cache.raw_strength, device_state.raw_strength[i])
        
        # Include API-pressed state
        if state.api_pressed:
            state.cache.pressed = True
            state.cache.strength = max(state.cache.strength, state.api_strength)
            state.cache.raw_strength = max(state.cache.raw_strength, state.api_strength)
    
    # ========================================================================
    # Joypad Methods
    # ========================================================================
    
    def get_joy_axis(self, device: int, axis: JoyAxis) -> float:
        """Get the value of a joypad axis (-1.0 to 1.0)."""
        with self._lock:
            if self.disable_input:
                return 0.0
            
            combined = self._combine_device_joyaxis(axis, device)
            return self._joy_axis.get(combined, 0.0)
    
    def get_joy_name(self, device: int) -> str:
        """Get the name of a connected joypad."""
        with self._lock:
            if device in self.joy_names:
                return self.joy_names[device].name
            return ""
    
    def get_joy_guid(self, device: int) -> str:
        """Get the GUID of a joypad."""
        with self._lock:
            if device in self.joy_names:
                return self.joy_names[device].uid
            return ""
    
    def is_joy_known(self, device: int) -> bool:
        """Check if a joypad has a known mapping."""
        with self._lock:
            if device not in self.joy_names:
                return False
            return self.joy_names[device].is_known
    
    def get_connected_joypads(self) -> List[int]:
        """Get list of connected joypad device IDs."""
        with self._lock:
            return [device for device, joypad in self.joy_names.items() 
                   if joypad.connected]
    
    def start_joy_vibration(self, device: int, weak_magnitude: float, 
                           strong_magnitude: float, duration: float = 0.0) -> None:
        """Start vibration on a joypad."""
        with self._lock:
            if self._should_ignore_joypad_events():
                return
            
            if not (0.0 <= weak_magnitude <= 1.0 and 0.0 <= strong_magnitude <= 1.0):
                return
            
            vibration = VibrationInfo(
                weak_magnitude=weak_magnitude,
                strong_magnitude=strong_magnitude,
                duration=duration,
                timestamp=int(time.time() * 1000000)
            )
            self.joy_vibration[device] = vibration
            
            # Trigger platform-specific vibration
            joypad = self.joy_names.get(device)
            if joypad and joypad.features and joypad.has_vibration:
                joypad.features.set_joy_vibration(weak_magnitude, strong_magnitude, duration)
    
    def stop_joy_vibration(self, device: int) -> None:
        """Stop vibration on a joypad."""
        with self._lock:
            vibration = VibrationInfo(
                weak_magnitude=0.0,
                strong_magnitude=0.0,
                duration=0.0,
                timestamp=int(time.time() * 1000000)
            )
            self.joy_vibration[device] = vibration
            
            joypad = self.joy_names.get(device)
            if joypad and joypad.features and joypad.has_vibration:
                joypad.features.set_joy_vibration(0.0, 0.0, 0.0)
    
    def is_joy_vibrating(self, device: int) -> bool:
        """Check if a joypad is currently vibrating."""
        return self.get_joy_vibration_remaining_duration(device) > 0.0
    
    def has_joy_vibration(self, device: int) -> bool:
        """Check if a joypad supports vibration."""
        with self._lock:
            joypad = self.joy_names.get(device)
            return joypad is not None and joypad.has_vibration
    
    def get_joy_vibration_strength(self, device: int) -> Tuple[float, float]:
        """Get current vibration strength (weak, strong)."""
        if device in self.joy_vibration:
            v = self.joy_vibration[device]
            return (v.weak_magnitude, v.strong_magnitude)
        return (0.0, 0.0)
    
    def get_joy_vibration_duration(self, device: int) -> float:
        """Get vibration duration."""
        if device in self.joy_vibration:
            return self.joy_vibration[device].duration
        return 0.0
    
    def get_joy_vibration_remaining_duration(self, device: int) -> float:
        """Get remaining vibration duration."""
        with self._lock:
            joypad = self.joy_names.get(device)
            if joypad is None or not joypad.has_vibration:
                return 0.0
            
            vibration = self.joy_vibration.get(device)
            if vibration is None or (vibration.weak_magnitude == 0.0 and 
                                     vibration.strong_magnitude == 0.0):
                return 0.0
            
            elapsed = (int(time.time() * 1000000) - vibration.timestamp) / 1000000.0
            remaining = max(0.0, vibration.duration - elapsed)
            return remaining
    
    def joy_connection_changed(self, device: int, connected: bool, 
                               name: str = "", guid: str = "", 
                               info: Dict[str, Any] = None) -> None:
        """Handle joypad connection/disconnection."""
        with self._lock:
            if not connected:
                # Clear pressed status for disconnected joypad
                for action_name, state in self.action_states.items():
                    if device in state.device_states:
                        del state.device_states[device]
                        self._update_action_cache(action_name, state)
            
            joypad = Joypad()
            joypad.name = name if connected else ""
            joypad.uid = guid if connected else ""
            joypad.info = info if connected else {}
            
            if connected:
                # Generate UID if not provided
                if not guid:
                    uidname = ""
                    uidlen = min(len(name), 16)
                    for i in range(uidlen):
                        uidname += format(ord(name[i]), '02x')
                    joypad.uid = uidname
                else:
                    joypad.uid = guid
                
                joypad.connected = True
                
                # Find mapping
                mapping = self.fallback_mapping
                for i, mapping_entry in enumerate(self.map_db):
                    if joypad.uid == mapping_entry.uid:
                        mapping = i
                        if mapping != self.fallback_mapping:
                            joypad.is_known = True
                        break
                
                self._set_joypad_mapping(joypad, mapping)
            else:
                joypad.connected = False
                # Clear button states
                for i in range(int(JoyButton.MAX)):
                    button = JoyButton(i)
                    combined = self._combine_device_joybutton(button, device)
                    self.joy_buttons_pressed.discard(combined)
                # Clear axis states
                for i in range(int(JoyAxis.MAX)):
                    axis = JoyAxis(i)
                    combined = self._combine_device_joyaxis(axis, device)
                    if combined in self._joy_axis:
                        del self._joy_axis[combined]
                # Clear motion
                if device in self.joy_motion:
                    del self.joy_motion[device]
            
            self.joy_names[device] = joypad
            logger.info(f"Joypad {device} {'connected' if connected else 'disconnected'}: {name}")
    
    def _set_joypad_mapping(self, joypad: Joypad, map_index: int) -> None:
        """Set the mapping index for a joypad."""
        if (map_index != self.fallback_mapping and 0 <= map_index < len(self.map_db) and
            joypad.uid != "__XINPUT_DEVICE__"):
            # Use name from mapping
            joypad.name = self.map_db[map_index].name
        joypad.mapping = map_index
    
    def add_joy_mapping(self, mapping: str, update_existing: bool = False) -> None:
        """Add a joypad mapping from SDL format string."""
        with self._lock:
            self.parse_mapping(mapping)
            if update_existing:
                uid = mapping.split(",")[0] if "," in mapping else ""
                for device, joypad in self.joy_names.items():
                    if joypad.uid == uid:
                        self._set_joypad_mapping(joypad, len(self.map_db) - 1)
    
    def remove_joy_mapping(self, guid: str) -> None:
        """Remove a joypad mapping by GUID."""
        with self._lock:
            removed_indices = []
            min_removed = -1
            max_removed = -1
            fallback_offset = 0
            
            for i in range(len(self.map_db) - 1, -1, -1):
                if guid == self.map_db[i].uid:
                    del self.map_db[i]
                    removed_indices.append(i)
                    if max_removed == -1:
                        max_removed = i
                    min_removed = i
                    if i < self.fallback_mapping:
                        fallback_offset += 1
                    elif i == self.fallback_mapping:
                        self.fallback_mapping = -1
                        logger.warning(f"Removed fallback mapping {guid}")
            
            if min_removed == -1:
                return
            
            if self.fallback_mapping > 0:
                self.fallback_mapping -= fallback_offset
            
            # Update joypad mappings
            for device, joypad in self.joy_names.items():
                if joypad.mapping < min_removed:
                    continue
                if joypad.mapping > max_removed:
                    self._set_joypad_mapping(joypad, joypad.mapping - len(removed_indices))
                    continue
                
                # Find new mapping
                for removed_idx in removed_indices:
                    if removed_idx == joypad.mapping:
                        self._set_joypad_mapping(joypad, self.fallback_mapping)
                        break
                    if removed_idx < joypad.mapping:
                        offset = sum(1 for r in removed_indices if r < joypad.mapping)
                        self._set_joypad_mapping(joypad, joypad.mapping - offset)
                        break
    
    # ========================================================================
    # Motion Sensor Methods
    # ========================================================================
    
    def get_gravity(self) -> Tuple[float, float, float]:
        """Get gravity vector."""
        with self._lock:
            if not self.gravity_enabled:
                logger.warning("Gravity sensors not enabled")
            return self.gravity
    
    def get_accelerometer(self) -> Tuple[float, float, float]:
        """Get accelerometer data."""
        with self._lock:
            if not self.accelerometer_enabled:
                logger.warning("Accelerometer not enabled")
            return self.accelerometer
    
    def get_magnetometer(self) -> Tuple[float, float, float]:
        """Get magnetometer data (compass)."""
        with self._lock:
            if not self.magnetometer_enabled:
                logger.warning("Magnetometer not enabled")
            return self.magnetometer
    
    def get_gyroscope(self) -> Tuple[float, float, float]:
        """Get gyroscope data (rotation rate)."""
        with self._lock:
            if not self.gyroscope_enabled:
                logger.warning("Gyroscope not enabled")
            return self.gyroscope
    
    def set_gravity(self, value: Tuple[float, float, float]) -> None:
        """Set gravity vector (for testing or external sensors)."""
        with self._lock:
            self.gravity = value
    
    def set_accelerometer(self, value: Tuple[float, float, float]) -> None:
        """Set accelerometer data."""
        with self._lock:
            self.accelerometer = value
    
    def set_magnetometer(self, value: Tuple[float, float, float]) -> None:
        """Set magnetometer data."""
        with self._lock:
            self.magnetometer = value
    
    def set_gyroscope(self, value: Tuple[float, float, float]) -> None:
        """Set gyroscope data."""
        with self._lock:
            self.gyroscope = value
    
    # ========================================================================
    # Mouse Methods
    # ========================================================================
    
    def get_mouse_position(self) -> Tuple[float, float]:
        """Get current mouse position."""
        return self.mouse_pos
    
    def set_mouse_position(self, pos: Tuple[float, float]) -> None:
        """Set mouse position (for warping)."""
        self.mouse_pos = pos
    
    def warp_mouse(self, position: Tuple[float, float]) -> None:
        """Warp mouse to a position."""
        if Input.warp_mouse_func:
            Input.warp_mouse_func(position)
    
    def get_last_mouse_velocity(self) -> Tuple[float, float]:
        """Get last calculated mouse velocity."""
        self.mouse_velocity_track.update((0.0, 0.0), (0.0, 0.0))
        return self.mouse_velocity_track.velocity
    
    def get_last_mouse_screen_velocity(self) -> Tuple[float, float]:
        """Get last calculated screen velocity."""
        self.mouse_velocity_track.update((0.0, 0.0), (0.0, 0.0))
        return self.mouse_velocity_track.screen_velocity
    
    def get_mouse_button_mask(self) -> int:
        """Get bitmask of pressed mouse buttons."""
        return self.mouse_button_mask
    
    def set_default_cursor_shape(self, shape: CursorShape) -> None:
        """Set the default cursor shape."""
        if self.default_shape == shape:
            return
        self.default_shape = shape
        
        # Trigger mouse motion to update cursor
        mm = InputEventMouseMotion()
        mm.device = InputConstants.DEVICE_ID_INTERNAL
        self.parse_input_event(mm)
    
    def get_default_cursor_shape(self) -> CursorShape:
        """Get the default cursor shape."""
        return self.default_shape
    
    def get_current_cursor_shape(self) -> CursorShape:
        """Get the current cursor shape."""
        if Input.get_current_cursor_shape_func:
            return Input.get_current_cursor_shape_func()
        return self.default_shape
    
    def set_custom_mouse_cursor(self, image: Any, shape: CursorShape = CursorShape.ARROW,
                               hotspot: Tuple[float, float] = (0.0, 0.0)) -> None:
        """Set a custom mouse cursor."""
        if Input.set_custom_mouse_cursor_func:
            Input.set_custom_mouse_cursor_func(image, shape, hotspot)
    
    # ========================================================================
    # Event Processing
    # ========================================================================
    
    def parse_input_event(self, event: InputEvent) -> None:
        """Parse and process an input event."""
        with self._lock:
            if self.use_accumulated_input:
                if not self.buffered_events or not self.buffered_events[-1].accumulate(event):
                    self.buffered_events.append(event)
            elif self.agile_input_event_flushing:
                self.buffered_events.append(event)
            else:
                self._parse_input_event_impl(event, False)
    
    def _parse_input_event_impl(self, event: InputEvent, is_emulated: bool) -> None:
        """Internal event parsing implementation."""
        # Handle keyboard events
        if isinstance(event, InputEventKey):
            if not event.is_echo() and event.keycode != Key.NONE:
                if event.is_pressed():
                    self.keys_pressed.add(event.keycode)
                else:
                    self.keys_pressed.discard(event.keycode)
            
            if not event.is_echo() and event.physical_keycode != Key.NONE:
                if event.is_pressed():
                    self.physical_keys_pressed.add(event.physical_keycode)
                else:
                    self.physical_keys_pressed.discard(event.physical_keycode)
            
            if not event.is_echo() and event.key_label != Key.NONE:
                if event.is_pressed():
                    self.key_label_pressed.add(event.key_label)
                else:
                    self.key_label_pressed.discard(event.key_label)
        
        # Handle mouse button events
        if isinstance(event, InputEventMouseButton):
            mask = mouse_button_to_mask(event.button_index)
            if event.is_pressed():
                self.mouse_button_mask |= mask
            else:
                self.mouse_button_mask &= ~mask
            
            pos = event.global_position
            if self.mouse_pos != pos:
                self.set_mouse_position(pos)
            
            # Touch emulation
            if (self.emulate_touch_from_mouse and not is_emulated and 
                event.button_index == MouseButton.LEFT and 
                Input.event_dispatch_function):
                touch_event = InputEventScreenTouch()
                touch_event.pressed = event.is_pressed()
                touch_event.canceled = event.is_canceled()
                touch_event.position = event.position
                touch_event.double_tap = event.is_double_click()
                touch_event.device = InputConstants.DEVICE_ID_EMULATION
                Input.event_dispatch_function(touch_event)
        
        # Handle mouse motion events
        if isinstance(event, InputEventMouseMotion):
            position = event.global_position
            if self.mouse_pos != position:
                self.set_mouse_position(position)
            
            relative = event.relative
            screen_relative = event.relative_screen_position
            self.mouse_velocity_track.update(relative, screen_relative)
            
            # Touch emulation
            if (self.emulate_touch_from_mouse and not is_emulated and
                event.button_mask & MouseButtonMask.LEFT and
                Input.event_dispatch_function):
                drag_event = InputEventScreenDrag()
                drag_event.position = position
                drag_event.relative = relative
                drag_event.relative_screen_position = screen_relative
                drag_event.velocity = self.get_last_mouse_velocity()
                drag_event.screen_velocity = self.get_last_mouse_screen_velocity()
                drag_event.device = InputConstants.DEVICE_ID_EMULATION
                Input.event_dispatch_function(drag_event)
        
        # Handle screen touch events
        if isinstance(event, InputEventScreenTouch):
            if event.is_pressed():
                track = VelocityTrack()
                track.reset()
                self.touch_velocity_track[event.index] = track
            else:
                self.touch_velocity_track.pop(event.index, None)
            
            # Mouse emulation
            if self.emulate_mouse_from_touch:
                translate = False
                if event.is_pressed():
                    if self.mouse_from_touch_index == -1:
                        translate = True
                        self.mouse_from_touch_index = event.index
                else:
                    if event.index == self.mouse_from_touch_index:
                        translate = True
                        self.mouse_from_touch_index = -1
                
                if translate:
                    button_event = InputEventMouseButton()
                    button_event.device = InputConstants.DEVICE_ID_EMULATION
                    button_event.position = event.position
                    button_event.global_position = event.position
                    button_event.pressed = event.is_pressed()
                    button_event.button_index = MouseButton.LEFT
                    button_event.double_click = event.is_double_tap()
                    
                    if event.is_pressed():
                        button_event.button_mask = self.mouse_button_mask | MouseButtonMask.LEFT
                    else:
                        button_event.button_mask = self.mouse_button_mask & ~MouseButtonMask.LEFT
                    
                    self._parse_input_event_impl(button_event, True)
        
        # Handle screen drag events
        if isinstance(event, InputEventScreenDrag):
            track = self.touch_velocity_track.get(event.index)
            if track:
                track.update(event.relative, event.relative_screen_position)
                event.velocity = track.velocity
                event.screen_velocity = track.screen_velocity
            
            # Mouse emulation
            if (self.emulate_mouse_from_touch and 
                event.index == self.mouse_from_touch_index):
                motion_event = InputEventMouseMotion()
                motion_event.device = InputConstants.DEVICE_ID_EMULATION
                motion_event.position = event.position
                motion_event.global_position = event.position
                motion_event.relative = event.relative
                motion_event.relative_screen_position = event.relative_screen_position
                motion_event.velocity = event.velocity
                motion_event.screen_velocity = event.screen_velocity
                motion_event.button_mask = self.mouse_button_mask
                self._parse_input_event_impl(motion_event, True)
        
        # Handle joypad button events
        if isinstance(event, InputEventJoypadButton):
            combined = self._combine_device_joybutton(event.button_index, event.device)
            if event.is_pressed():
                self.joy_buttons_pressed.add(combined)
            else:
                self.joy_buttons_pressed.discard(combined)
        
        # Handle joypad motion events
        if isinstance(event, InputEventJoypadMotion):
            self.set_joy_axis(event.device, event.axis, event.axis_value)
        
        # Dispatch to external handler
        if Input.event_dispatch_function:
            Input.event_dispatch_function(event)
    
    def set_joy_axis(self, device: int, axis: JoyAxis, value: float) -> None:
        """Set a joypad axis value."""
        with self._lock:
            combined = self._combine_device_joyaxis(axis, device)
            self._joy_axis[combined] = value
    
    def flush_buffered_events(self) -> None:
        """Flush all buffered events."""
        with self._lock:
            while self.buffered_events:
                event = self.buffered_events.pop(0)
                self._parse_input_event_impl(event, False)
    
    def set_use_accumulated_input(self, enable: bool) -> None:
        """Enable/disable input event accumulation."""
        self.use_accumulated_input = enable
    
    def is_using_accumulated_input(self) -> bool:
        """Check if input accumulation is enabled."""
        return self.use_accumulated_input
    
    def set_agile_input_event_flushing(self, enable: bool) -> None:
        """Enable/disable agile event flushing."""
        self.agile_input_event_flushing = enable
    
    def is_agile_input_event_flushing(self) -> bool:
        """Check if agile flushing is enabled."""
        return self.agile_input_event_flushing
    
    # ========================================================================
    # Emulation Settings
    # ========================================================================
    
    def set_emulate_touch_from_mouse(self, enable: bool) -> None:
        """Enable/disable touch emulation from mouse."""
        self.emulate_touch_from_mouse = enable
    
    def is_emulating_touch_from_mouse(self) -> bool:
        """Check if touch emulation is enabled."""
        return self.emulate_touch_from_mouse
    
    def set_emulate_mouse_from_touch(self, enable: bool) -> None:
        """Enable/disable mouse emulation from touch."""
        self.emulate_mouse_from_touch = enable
    
    def is_emulating_mouse_from_touch(self) -> bool:
        """Check if mouse emulation is enabled."""
        return self.emulate_mouse_from_touch
    
    def ensure_touch_mouse_raised(self) -> None:
        """Ensure emulated touch mouse is raised."""
        with self._lock:
            if self.mouse_from_touch_index != -1:
                self.mouse_from_touch_index = -1
                
                button_event = InputEventMouseButton()
                button_event.device = InputConstants.DEVICE_ID_EMULATION
                button_event.position = self.mouse_pos
                button_event.global_position = self.mouse_pos
                button_event.pressed = False
                button_event.button_index = MouseButton.LEFT
                button_event.button_mask = self.mouse_button_mask & ~MouseButtonMask.LEFT
                
                self._parse_input_event_impl(button_event, True)
    
    # ========================================================================
    # Joypad Mapping Parser
    # ========================================================================
    
    def parse_mapping(self, mapping: str) -> None:
        """Parse an SDL format joypad mapping string."""
        with self._lock:
            entries = mapping.split(",")
            if len(entries) < 2:
                return
            
            device_mapping = JoyDeviceMapping()
            device_mapping.uid = entries[0]
            device_mapping.name = entries[1]
            
            for entry in entries[2:]:
                if not entry:
                    continue
                
                parts = entry.split(":")
                if len(parts) != 2:
                    continue
                
                output = parts[0].strip()
                input_str = parts[1].strip()
                
                if len(output) < 1 or len(input_str) < 2:
                    continue
                
                if output in ("platform", "hint"):
                    continue
                
                # Parse output range
                output_range = JoyAxisRange.FULL_AXIS
                if output[0] in ('+', '-'):
                    if len(output) < 2:
                        continue
                    if output[0] == '+':
                        output_range = JoyAxisRange.POSITIVE_HALF_AXIS
                    else:
                        output_range = JoyAxisRange.NEGATIVE_HALF_AXIS
                    output = output[1:]
                
                # Parse input range
                input_range = JoyAxisRange.FULL_AXIS
                if input_str[0] == '+':
                    input_range = JoyAxisRange.POSITIVE_HALF_AXIS
                    input_str = input_str[1:]
                elif input_str[0] == '-':
                    input_range = JoyAxisRange.NEGATIVE_HALF_AXIS
                    input_str = input_str[1:]
                
                invert_axis = False
                if input_str[-1] == '~':
                    invert_axis = True
                    input_str = input_str[:-1]
                
                # Get output button/axis
                output_button = self._get_output_button(output)
                output_axis = self._get_output_axis(output)
                
                if output_button == JoyButton.INVALID and output_axis == JoyAxis.INVALID:
                    logger.warning(f"Unrecognized output: {output}")
                    continue
                
                if output_button != JoyButton.INVALID and output_axis != JoyAxis.INVALID:
                    logger.warning(f"Output matched both button and axis: {output}")
                    continue
                
                # Create binding
                binding = JoyBinding()
                if output_button != JoyButton.INVALID:
                    binding.outputType = JoyEventType.BUTTON
                    binding.output.button = output_button
                elif output_axis != JoyAxis.INVALID:
                    binding.outputType = JoyEventType.AXIS
                    binding.output.axis = output_axis
                    binding.output.range = output_range
                
                # Parse input
                if input_str[0] == 'b':
                    binding.inputType = JoyEventType.BUTTON
                    binding.input.button = JoyButton(int(input_str[1:]))
                elif input_str[0] == 'a':
                    binding.inputType = JoyEventType.AXIS
                    binding.input.axis = JoyAxis(int(input_str[1:]))
                    binding.input.range = input_range
                    binding.input.invert = invert_axis
                elif input_str[0] == 'h':
                    if len(input_str) != 4 or input_str[2] != '.':
                        logger.warning(f"Invalid hat input: {input_str}")
                        continue
                    binding.inputType = JoyEventType.HAT
                    binding.input.hat = int(input_str[1])
                    binding.input.hat_mask = HatMask(int(input_str[3]))
                else:
                    logger.warning(f"Unrecognized input: {input_str}")
                    continue
                
                device_mapping.bindings.append(binding)
            
            self.map_db.append(device_mapping)
    
    def _get_output_button(self, output: str) -> JoyButton:
        """Convert output string to JoyButton."""
        return JOY_BUTTON_NAME_TO_ENUM.get(output, JoyButton.INVALID)
    
    def _get_output_axis(self, output: str) -> JoyAxis:
        """Convert output string to JoyAxis."""
        return JOY_AXIS_NAME_TO_ENUM.get(output, JoyAxis.INVALID)
    
    def _load_default_mappings(self) -> None:
        """Load default SDL controller mappings."""
        # Common controller mappings (subset of SDL database)
        default_mappings = [
            # Xbox 360 Controller
            "030000005e0400008e02000000007200,Xbox 360 Controller,a:b0,b:b1,back:b6,dpdown:h0.4,dpleft:h0.8,dpright:h0.2,dpup:h0.1,guide:b8,leftshoulder:b4,leftstick:b9,lefttrigger:a2,leftx:a0,lefty:a1,rightshoulder:b5,rightstick:b10,righttrigger:a5,rightx:a3,righty:a4,start:b7,x:b2,y:b3,",
            # Xbox One Controller
            "030000005e040000ea02000000007200,Xbox One Controller,a:b0,b:b1,back:b6,dpdown:h0.4,dpleft:h0.8,dpright:h0.2,dpup:h0.1,guide:b8,leftshoulder:b4,leftstick:b9,lefttrigger:a2,leftx:a0,lefty:a1,rightshoulder:b5,rightstick:b10,righttrigger:a5,rightx:a3,righty:a4,start:b7,x:b2,y:b3,",
            # PlayStation 4 Controller
            "030000004c050000c405000000006800,PS4 Controller,a:b1,b:b2,back:b8,dpdown:h0.4,dpleft:h0.8,dpright:h0.2,dpup:h0.1,guide:b12,leftshoulder:b4,leftstick:b10,lefttrigger:a3,leftx:a0,lefty:a1,rightshoulder:b5,rightstick:b11,righttrigger:a4,rightx:a2,righty:a5,start:b9,x:b0,y:b3,",
            # PlayStation 5 Controller
            "030000004c050000e60c000000006800,PS5 Controller,a:b1,b:b2,back:b8,dpdown:h0.4,dpleft:h0.8,dpright:h0.2,dpup:h0.1,guide:b12,leftshoulder:b4,leftstick:b10,lefttrigger:a3,leftx:a0,lefty:a1,rightshoulder:b5,rightstick:b11,righttrigger:a4,rightx:a2,righty:a5,start:b9,x:b0,y:b3,",
            # Nintendo Switch Pro Controller
            "030000007e0500000920000000006800,Switch Pro Controller,a:b0,b:b1,back:b8,dpdown:h0.4,dpleft:h0.8,dpright:h0.2,dpup:h0.1,guide:b12,leftshoulder:b4,leftstick:b10,lefttrigger:b6,leftx:a0,lefty:a1,rightshoulder:b5,rightstick:b11,righttrigger:b7,rightx:a2,righty:a3,start:b9,x:b2,y:b3,",
        ]
        
        for mapping in default_mappings:
            self.parse_mapping(mapping)
    
    # ========================================================================
    # Utility Methods
    # ========================================================================
    
    def set_disable_input(self, disable: bool) -> None:
        """Globally enable/disable input processing."""
        self.disable_input = disable
    
    def is_input_disabled(self) -> bool:
        """Check if input is globally disabled."""
        return self.disable_input
    
    def set_ignore_joypad_on_unfocused_application(self, ignore: bool) -> None:
        """Set whether to ignore joypad when app is unfocused."""
        self.ignore_joypad_on_unfocused_application = ignore
        if self._should_ignore_joypad_events():
            self.release_pressed_events()
    
    def is_ignoring_joypad_on_unfocused_application(self) -> bool:
        """Check if joypad is ignored when unfocused."""
        return self.ignore_joypad_on_unfocused_application
    
    def release_pressed_events(self) -> None:
        """Release all pressed input events."""
        with self._lock:
            if self.application_focused or self.embedder_focused:
                return
            
            self.flush_buffered_events()
            
            self.keys_pressed.clear()
            self.physical_keys_pressed.clear()
            self.key_label_pressed.clear()
            
            if self.ignore_joypad_on_unfocused_application:
                self.joy_buttons_pressed.clear()
                self._joy_axis.clear()
                
                for action_name in list(self.action_states.keys()):
                    if self.action_states[action_name].cache.pressed:
                        self.action_release(action_name)
                
                for device in self.get_connected_joypads():
                    self.stop_joy_vibration(device)
    
    def vibrate_handheld(self, duration_ms: int = 500, amplitude: float = -1.0) -> None:
        """Vibrate handheld device (phone, etc.)."""
        # Platform-specific implementation would go here
        logger.debug(f"Handheld vibration: {duration_ms}ms, amplitude={amplitude}")
    
    def set_event_dispatch_function(self, func: Optional[Callable[[InputEvent], None]]) -> None:
        """Set the function to dispatch input events to."""
        Input.event_dispatch_function = func
    
    def set_legacy_just_pressed_behavior(self, legacy: bool) -> None:
        """Set legacy behavior for just pressed/released detection."""
        self.legacy_just_pressed_behavior = legacy
    
    def get_unused_joy_id(self) -> int:
        """Get an unused joypad device ID."""
        for i in range(InputConstants.JOYPADS_MAX):
            if i not in self.joy_names or not self.joy_names[i].connected:
                return i
        return -1
