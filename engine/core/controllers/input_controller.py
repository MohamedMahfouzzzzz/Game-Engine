# /**************************************************************************/
# /*  input_controller.py                                                   */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Native input controller for engine."""

from typing import Dict, Callable, Optional, List, Tuple
from enum import Enum

class InputAction(Enum):
    """Standard input actions."""
    MOVE_UP = "move_up"
    MOVE_DOWN = "move_down"
    MOVE_LEFT = "move_left"
    MOVE_RIGHT = "move_right"
    JUMP = "jump"
    ATTACK = "attack"
    INTERACT = "interact"
    CANCEL = "cancel"
    MENU = "menu"
    PAUSE = "pause"


class InputController:
    """Native engine input controller for handling game input."""

    def __init__(self):
        self._action_mappings: Dict[InputAction, List[int]] = {}
        self._action_callbacks: Dict[InputAction, List[Callable]] = {}
        self._key_states: Dict[int, bool] = {}
        self._mouse_position: Tuple[int, int] = (0, 0)
        self._mouse_buttons: Dict[int, bool] = {}

        # Default mappings (keyboard keys)
        self._default_mappings = {
            InputAction.MOVE_UP: [87],  # W
            InputAction.MOVE_DOWN: [83],  # S
            InputAction.MOVE_LEFT: [65],  # A
            InputAction.MOVE_RIGHT: [68],  # D
            InputAction.JUMP: [32],  # Space
            InputAction.ATTACK: [70],  # F
            InputAction.INTERACT: [69],  # E
            InputAction.CANCEL: [27],  # Escape
            InputAction.MENU: [9],  # Tab
            InputAction.PAUSE: [80],  # P
        }

        self._action_mappings = self._default_mappings.copy()

    def map_action(self, action: InputAction, keys: List[int]) -> None:
        """Map an action to one or more keys."""
        self._action_mappings[action] = keys

    def bind_action(self, action: InputAction, callback: Callable) -> None:
        """Bind a callback to an action."""
        if action not in self._action_callbacks:
            self._action_callbacks[action] = []
        self._action_callbacks[action].append(callback)

    def unbind_action(self, action: InputAction, callback: Callable) -> None:
        """Unbind a callback from an action."""
        if action in self._action_callbacks:
            if callback in self._action_callbacks[action]:
                self._action_callbacks[action].remove(callback)

    def on_key_press(self, key: int) -> None:
        """Handle key press event."""
        self._key_states[key] = True

        # Find actions mapped to this key
        for action, keys in self._action_mappings.items():
            if key in keys:
                self._trigger_action(action)

    def on_key_release(self, key: int) -> None:
        """Handle key release event."""
        self._key_states[key] = False

    def on_mouse_move(self, x: int, y: int) -> None:
        """Handle mouse move event."""
        self._mouse_position = (x, y)

    def on_mouse_press(self, button: int) -> None:
        """Handle mouse press event."""
        self._mouse_buttons[button] = True

    def on_mouse_release(self, button: int) -> None:
        """Handle mouse release event."""
        self._mouse_buttons[button] = False

    def is_action_pressed(self, action: InputAction) -> bool:
        """Check if an action is currently pressed."""
        if action not in self._action_mappings:
            return False
        return any(self._key_states.get(key, False) for key in self._action_mappings[action])

    def is_key_pressed(self, key: int) -> bool:
        """Check if a specific key is pressed."""
        return self._key_states.get(key, False)

    def get_mouse_position(self) -> Tuple[int, int]:
        """Get current mouse position."""
        return self._mouse_position

    def is_mouse_pressed(self, button: int) -> bool:
        """Check if a mouse button is pressed."""
        return self._mouse_buttons.get(button, False)

    def _trigger_action(self, action: InputAction) -> None:
        """Trigger all callbacks for an action."""
        if action in self._action_callbacks:
            for callback in self._action_callbacks[action]:
                callback()

    def reset_mappings(self) -> None:
        """Reset all mappings to defaults."""
        self._action_mappings = self._default_mappings.copy()

    def get_mappings(self) -> Dict[InputAction, List[int]]:
        """Get current action mappings."""
        return self._action_mappings.copy()

    def set_mappings(self, mappings: Dict[InputAction, List[int]]) -> None:
        """Set action mappings."""
        self._action_mappings = mappings.copy()
