# /**************************************************************************/
# /*  input_manager.py                                                      */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Input manager for handling keyboard, mouse, and gamepad input."""

from typing import Dict, Set, Callable, Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum, auto

import logging



logger = logging.getLogger(__name__)

class InputDevice(Enum):
    """Input device types."""
    KEYBOARD = auto()
    MOUSE = auto()
    GAMEPAD = auto()
    TOUCH = auto()


@dataclass
class InputState:
    """Current state of an input."""
    pressed: bool = False
    just_pressed: bool = False
    just_released: bool = False
    value: float = 0.0  # For analog inputs (0.0 - 1.0)
    time_held: float = 0.0


class InputManager:
    """Manages all input devices and actions."""

    _instance: Optional["InputManager"] = None

    def __init__(self):
        # Keyboard state
        self._keys: Dict[int, InputState] = {}
        self._prev_keys: Set[int] = set()
        self._current_keys: Set[int] = set()

        # Mouse state
        self._mouse_position: Tuple[int, int] = (0, 0)
        self._mouse_delta: Tuple[int, int] = (0, 0)
        self._mouse_buttons: Dict[int, InputState] = {}
        self._mouse_wheel: float = 0.0

        # Action mappings
        self._action_map: Optional["ActionMap"] = None

        # Callbacks
        self._key_callbacks: Dict[int, List[Callable]] = {}
        self._action_callbacks: Dict[str, List[Callable]] = {}

        # Input enabled flag
        self._enabled: bool = True

    @classmethod
    def get_instance(cls) -> "InputManager":
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = InputManager()
        return cls._instance

    def enable(self) -> None:
        """Enable input processing."""
        self._enabled = True

    def disable(self) -> None:
        """Disable input processing."""
        self._enabled = False

    def update(self, delta_time: float) -> None:
        """Update input states (call every frame)."""
        if not self._enabled:
            return

        # Update keyboard states
        for key in self._keys:
            state = self._keys[key]
            state.just_pressed = key in self._current_keys and key not in self._prev_keys
            state.just_released = key not in self._current_keys and key in self._prev_keys
            state.pressed = key in self._current_keys

            if state.pressed:
                state.time_held += delta_time
            else:
                state.time_held = 0.0

        self._prev_keys = self._current_keys.copy()

        # Update mouse buttons
        for btn in self._mouse_buttons:
            state = self._mouse_buttons[btn]
            if state.just_pressed:
                state.pressed = True
                state.just_pressed = False
            elif state.just_released:
                state.pressed = False
                state.just_released = False

            if state.pressed:
                state.time_held += delta_time

        # Reset mouse wheel
        self._mouse_wheel = 0.0
        self._mouse_delta = (0, 0)

    # Keyboard methods
    def is_key_pressed(self, key: int) -> bool:
        """Check if key is currently held down."""
        return key in self._current_keys

    def is_key_just_pressed(self, key: int) -> bool:
        """Check if key was pressed this frame."""
        return key in self._keys and self._keys[key].just_pressed

    def is_key_just_released(self, key: int) -> bool:
        """Check if key was released this frame."""
        return key in self._keys and self._keys[key].just_released

    def get_key_hold_time(self, key: int) -> float:
        """Get how long key has been held."""
        if key in self._keys:
            return self._keys[key].time_held
        return 0.0

    def on_key_event(self, key: int, pressed: bool) -> None:
        """Process key event (called by window system)."""
        if key not in self._keys:
            self._keys[key] = InputState()

        if pressed:
            self._current_keys.add(key)
            self._keys[key].just_pressed = True
        else:
            self._current_keys.discard(key)
            self._keys[key].just_released = True

        # Trigger callbacks
        if key in self._key_callbacks:
            for callback in self._key_callbacks[key]:
                callback(pressed)

    def connect_key(self, key: int, callback: Callable[[bool], None]) -> None:
        """Connect callback to key event."""
        if key not in self._key_callbacks:
            self._key_callbacks[key] = []
        self._key_callbacks[key].append(callback)

    # Mouse methods
    def on_mouse_move(self, x: int, y: int) -> None:
        """Process mouse move event."""
        dx = x - self._mouse_position[0]
        dy = y - self._mouse_position[1]
        self._mouse_delta = (dx, dy)
        self._mouse_position = (x, y)

    def on_mouse_button(self, button: int, pressed: bool) -> None:
        """Process mouse button event."""
        if button not in self._mouse_buttons:
            self._mouse_buttons[button] = InputState()

        state = self._mouse_buttons[button]
        if pressed:
            state.just_pressed = True
        else:
            state.just_released = True

    def on_mouse_wheel(self, delta: float) -> None:
        """Process mouse wheel event."""
        self._mouse_wheel = delta

    def is_mouse_button_pressed(self, button: int) -> bool:
        """Check if mouse button is pressed."""
        return button in self._mouse_buttons and self._mouse_buttons[button].pressed

    def is_mouse_button_just_pressed(self, button: int) -> bool:
        """Check if mouse button was just pressed."""
        return button in self._mouse_buttons and self._mouse_buttons[button].just_pressed

    def get_mouse_position(self) -> Tuple[int, int]:
        """Get current mouse position."""
        return self._mouse_position

    def get_mouse_delta(self) -> Tuple[int, int]:
        """Get mouse movement since last frame."""
        return self._mouse_delta

    def get_mouse_wheel(self) -> float:
        """Get mouse wheel delta."""
        return self._mouse_wheel

    # Action mapping
    def set_action_map(self, action_map: "ActionMap") -> None:
        """Set the action map for input."""
        self._action_map = action_map

    def is_action_pressed(self, action_name: str) -> bool:
        """Check if action is currently active."""
        if not self._action_map:
            return False

        keys = self._action_map.get_keys_for_action(action_name)
        return any(self.is_key_pressed(k) for k in keys)

    def is_action_just_pressed(self, action_name: str) -> bool:
        """Check if action was just activated."""
        if not self._action_map:
            return False

        keys = self._action_map.get_keys_for_action(action_name)
        return any(self.is_key_just_pressed(k) for k in keys)

    def get_action_value(self, action_name: str) -> float:
        """Get analog value for action (0.0 - 1.0)."""
        if self.is_action_pressed(action_name):
            return 1.0
        return 0.0

    def connect_action(self, action_name: str, callback: Callable[[], None]) -> None:
        """Connect callback to action."""
        if action_name not in self._action_callbacks:
            self._action_callbacks[action_name] = []
        self._action_callbacks[action_name].append(callback)

    # Utility methods
    def get_any_key_pressed(self) -> bool:
        """Check if any key is pressed."""
        return len(self._current_keys) > 0

    def clear(self) -> None:
        """Clear all input states."""
        self._keys.clear()
        self._current_keys.clear()
        self._prev_keys.clear()
        self._mouse_buttons.clear()


def get_input_manager() -> InputManager:
    """Get global input manager instance."""
    return InputManager.get_instance()
