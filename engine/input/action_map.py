# /**************************************************************************/
# /*  action_map.py                                                         */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Action mapping system for binding keys to game actions."""

from typing import Dict, List, Optional, Set, Callable
from dataclasses import dataclass, field
from enum import Enum, auto

import logging



logger = logging.getLogger(__name__)

class ActionType(Enum):
    """Types of input actions."""
    PRESS = auto()      # Trigger on press
    RELEASE = auto()    # Trigger on release
    HOLD = auto()       # Trigger while held
    AXIS = auto()       # Analog axis input


@dataclass
class InputAction:
    """Definition of an input action."""
    name: str
    keys: List[int] = field(default_factory=list)
    action_type: ActionType = ActionType.PRESS
    deadzone: float = 0.1  # For analog inputs
    scale: float = 1.0     # Scale factor for analog values

    def add_key(self, key: int) -> None:
        """Add a key binding."""
        if key not in self.keys:
            self.keys.append(key)

    def remove_key(self, key: int) -> None:
        """Remove a key binding."""
        if key in self.keys:
            self.keys.remove(key)

    def has_key(self, key: int) -> bool:
        """Check if action has key binding."""
        return key in self.keys


class ActionMap:
    """Maps input keys to game actions."""

    def __init__(self, name: str = "default"):
        self.name = name
        self._actions: Dict[str, InputAction] = {}
        self._key_to_actions: Dict[int, Set[str]] = {}

        # Default common actions
        self._add_default_actions()

    def _add_default_actions(self) -> None:
        """Add default common actions."""
        # Movement
        self.add_action("move_left", [65, 16777234])  # A, Left
        self.add_action("move_right", [68, 16777236])  # D, Right
        self.add_action("move_up", [87, 16777235])  # W, Up
        self.add_action("move_down", [83, 16777237])  # S, Down

        # Actions
        self.add_action("jump", [32])  # Space
        self.add_action("attack", [16777220])  # Enter
        self.add_action("interact", [69])  # E
        self.add_action("pause", [16777265])  # Escape

        # UI
        self.add_action("ui_accept", [32, 16777220])  # Space, Enter
        self.add_action("ui_cancel", [16777265])  # Escape
        self.add_action("ui_up", [87, 16777235])  # W, Up
        self.add_action("ui_down", [83, 16777237])  # S, Down

    def add_action(self, name: str, keys: List[int] = None, action_type: ActionType = ActionType.PRESS) -> InputAction:
        """Add a new action."""
        action = InputAction(name, keys or [], action_type)
        self._actions[name] = action

        # Update key mappings
        for key in action.keys:
            if key not in self._key_to_actions:
                self._key_to_actions[key] = set()
            self._key_to_actions[key].add(name)

        return action

    def remove_action(self, name: str) -> None:
        """Remove an action."""
        if name in self._actions:
            action = self._actions[name]
            for key in action.keys:
                if key in self._key_to_actions:
                    self._key_to_actions[key].discard(name)
            del self._actions[name]

    def get_action(self, name: str) -> Optional[InputAction]:
        """Get action by name."""
        return self._actions.get(name)

    def get_keys_for_action(self, name: str) -> List[int]:
        """Get all keys bound to an action."""
        action = self._actions.get(name)
        if action:
            return action.keys.copy()
        return []

    def get_actions_for_key(self, key: int) -> List[str]:
        """Get all actions bound to a key."""
        return list(self._key_to_actions.get(key, set()))

    def bind_key(self, action_name: str, key: int) -> bool:
        """Bind a key to an action."""
        action = self._actions.get(action_name)
        if not action:
            return False

        action.add_key(key)

        if key not in self._key_to_actions:
            self._key_to_actions[key] = set()
        self._key_to_actions[key].add(action_name)

        return True

    def unbind_key(self, action_name: str, key: int) -> bool:
        """Unbind a key from an action."""
        action = self._actions.get(action_name)
        if not action:
            return False

        action.remove_key(key)
        if key in self._key_to_actions:
            self._key_to_actions[key].discard(action_name)

        return True

    def remap_action(self, action_name: str, new_keys: List[int]) -> bool:
        """Remap an action to new keys."""
        action = self._actions.get(action_name)
        if not action:
            return False

        # Remove old mappings
        for key in action.keys:
            if key in self._key_to_actions:
                self._key_to_actions[key].discard(action_name)

        # Set new keys
        action.keys = new_keys.copy()

        # Add new mappings
        for key in new_keys:
            if key not in self._key_to_actions:
                self._key_to_actions[key] = set()
            self._key_to_actions[key].add(action_name)

        return True

    def get_all_actions(self) -> List[str]:
        """Get list of all action names."""
        return list(self._actions.keys())

    def get_action_count(self) -> int:
        """Get number of actions."""
        return len(self._actions)

    def duplicate(self, new_name: str) -> "ActionMap":
        """Create a copy of this action map."""
        new_map = ActionMap(new_name)

        for name, action in self._actions.items():
            new_map.add_action(name, action.keys.copy(), action.action_type)

        return new_map

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "name": self.name,
            "actions": {
                name: {
                    "keys": action.keys,
                    "type": action.action_type.name,
                    "deadzone": action.deadzone,
                    "scale": action.scale,
                }
                for name, action in self._actions.items()
            }
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ActionMap":
        """Create from dictionary."""
        action_map = cls(data.get("name", "default"))
        action_map._actions.clear()
        action_map._key_to_actions.clear()

        actions_data = data.get("actions", {})
        for name, action_data in actions_data.items():
            action_type = ActionType[action_data.get("type", "PRESS")]
            action = action_map.add_action(
                name,
                action_data.get("keys", []),
                action_type
            )
            action.deadzone = action_data.get("deadzone", 0.1)
            action.scale = action_data.get("scale", 1.0)

        return action_map

    def save_to_file(self, path: str) -> bool:
        """Save action map to JSON file."""
        import json
        try:
            with open(path, "w") as f:
                json.dump(self.to_dict(), f, indent=2)
            return True
        except Exception:
            return False

    @classmethod
    def load_from_file(cls, path: str) -> Optional["ActionMap"]:
        """Load action map from JSON file."""
        import json
        try:
            with open(path, "r") as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception:
            return None
