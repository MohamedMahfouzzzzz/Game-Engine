# /**************************************************************************/
# /*  input_map.py                                                          */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Input Map System - Action to Event Mapping

Godot Engine InputMap port to Python.
Maps named actions to specific input events (keyboard, mouse, joypad).
"""

from typing import Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
import logging

from engine.input.input_events import (
    InputEvent, InputEventKey, InputEventMouseButton, InputEventMouseMotion,
    InputEventJoypadButton, InputEventJoypadMotion
)
from engine.input.input_enums import Key, MouseButton, JoyButton, JoyAxis

logger = logging.getLogger(__name__)


# =============================================================================
# Input Event Magnitude (for deadzone handling)
# =============================================================================

@dataclass
class InputEventMagnitude:
    """Wrapper for input event with deadzone info."""
    event: InputEvent
    magnitude: float = 1.0


# =============================================================================
# Action Mapping
# =============================================================================

@dataclass
class ActionMapping:
    """Maps an input event to an action with optional deadzone."""
    event: InputEvent
    deadzone: float = 0.5
    
    def matches_event(self, other: InputEvent, exact_match: bool = False) -> bool:
        """Check if this mapping matches the given event."""
        # Check event type matches
        if type(self.event) != type(other):
            return False
        
        if isinstance(self.event, InputEventKey):
            # Key event matching
            key_ev = self.event
            other_key = other
            if exact_match:
                return (key_ev.keycode == other_key.keycode and 
                       key_ev.physical_keycode == other_key.physical_keycode and
                       key_ev.key_label == other_key.key_label)
            else:
                # Non-exact: match any of the key properties
                return (key_ev.keycode == other_key.keycode or
                       key_ev.physical_keycode == other_key.physical_keycode or
                       key_ev.key_label == other_key.key_label)
        
        elif isinstance(self.event, InputEventMouseButton):
            # Mouse button matching
            return self.event.button_index == other.button_index
        
        elif isinstance(self.event, InputEventJoypadButton):
            # Joypad button matching
            return self.event.button_index == other.button_index
        
        elif isinstance(self.event, InputEventJoypadMotion):
            # Joypad axis matching
            joy_ev = self.event
            other_joy = other
            if joy_ev.axis != other_joy.axis:
                return False
            # Check direction matches (positive/negative half axis)
            joy_value = joy_ev.axis_value
            other_value = other_joy.axis_value
            if (joy_value > 0 and other_value < 0) or (joy_value < 0 and other_value > 0):
                return False
            return True
        
        elif isinstance(self.event, InputEventMouseMotion):
            # Mouse motion matching
            return (self.event.button_mask == other.button_mask or 
                   self.event.button_mask == 0)
        
        return False
    
    def get_deadzone(self) -> float:
        """Get the deadzone for this mapping."""
        return self.deadzone


# =============================================================================
# Input Map Singleton
# =============================================================================

class InputMap:
    """Maps named actions to input events.
    
    This is the Godot InputMap port for Python. It allows defining
    named actions (like "jump", "move_left", "fire") and mapping
    them to specific input events.
    """
    
    _instance: Optional['InputMap'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        
        # action_name -> List[ActionMapping]
        self._action_map: Dict[str, List[ActionMapping]] = {}
        # action_name -> default deadzone
        self._action_deadzones: Dict[str, float] = {}
        # Track default actions
        self._default_actions: Set[str] = set()
        
        logger.info("InputMap singleton initialized")
    
    @classmethod
    def get_singleton(cls) -> 'InputMap':
        """Get the InputMap singleton instance."""
        if cls._instance is None:
            cls._instance = InputMap()
        return cls._instance
    
    # ========================================================================
    # Action Management
    # ========================================================================
    
    def has_action(self, action: str) -> bool:
        """Check if an action exists."""
        return action in self._action_map
    
    def add_action(self, action: str, deadzone: float = 0.5) -> None:
        """Add a new action."""
        if action in self._action_map:
            logger.warning(f"Action '{action}' already exists")
            return
        
        self._action_map[action] = []
        self._action_deadzones[action] = deadzone
        logger.debug(f"Added action: {action} with deadzone={deadzone}")
    
    def erase_action(self, action: str) -> None:
        """Remove an action."""
        if action not in self._action_map:
            logger.warning(f"Action '{action}' does not exist")
            return
        
        del self._action_map[action]
        if action in self._action_deadzones:
            del self._action_deadzones[action]
        self._default_actions.discard(action)
        logger.debug(f"Removed action: {action}")
    
    def get_actions(self) -> List[str]:
        """Get all action names."""
        return list(self._action_map.keys())
    
    def action_set_deadzone(self, action: str, deadzone: float) -> None:
        """Set the deadzone for an action."""
        if action not in self._action_map:
            logger.warning(f"Action '{action}' does not exist")
            return
        
        self._action_deadzones[action] = max(0.0, min(1.0, deadzone))
        # Update all mappings for this action
        for mapping in self._action_map[action]:
            mapping.deadzone = deadzone
    
    def action_get_deadzone(self, action: str) -> float:
        """Get the deadzone for an action."""
        return self._action_deadzones.get(action, 0.5)
    
    def action_add_event(self, action: str, event: InputEvent, deadzone: Optional[float] = None) -> None:
        """Add an input event to an action."""
        if action not in self._action_map:
            self.add_action(action)
        
        # Use action deadzone if not specified
        if deadzone is None:
            deadzone = self._action_deadzones.get(action, 0.5)
        
        mapping = ActionMapping(event=event, deadzone=deadzone)
        
        # Check for duplicates
        for existing in self._action_map[action]:
            if existing.matches_event(event, exact_match=True):
                logger.debug(f"Event already exists for action '{action}', skipping")
                return
        
        self._action_map[action].append(mapping)
        logger.debug(f"Added event to action '{action}'")
    
    def action_erase_event(self, action: str, event: InputEvent) -> bool:
        """Remove an input event from an action. Returns True if removed."""
        if action not in self._action_map:
            return False
        
        for i, mapping in enumerate(self._action_map[action]):
            if mapping.matches_event(event, exact_match=True):
                del self._action_map[action][i]
                logger.debug(f"Removed event from action '{action}'")
                return True
        
        return False
    
    def action_erase_events(self, action: str) -> None:
        """Remove all events from an action."""
        if action not in self._action_map:
            return
        
        self._action_map[action].clear()
        logger.debug(f"Cleared all events from action '{action}'")
    
    def action_get_events(self, action: str) -> List[InputEvent]:
        """Get all input events for an action."""
        if action not in self._action_map:
            return []
        
        return [mapping.event for mapping in self._action_map[action]]
    
    def event_is_action(self, event: InputEvent, action: str, exact_match: bool = False) -> bool:
        """Check if an event matches an action."""
        if action not in self._action_map:
            return False
        
        for mapping in self._action_map[action]:
            if mapping.matches_event(event, exact_match):
                return True
        
        return False
    
    def action_has_event(self, action: str, event: InputEvent) -> bool:
        """Check if an action has a specific event."""
        if action not in self._action_map:
            return False
        
        for mapping in self._action_map[action]:
            if mapping.matches_event(event, exact_match=True):
                return True
        
        return False
    
    # ========================================================================
    # Event Matching
    # ========================================================================
    
    def get_action_from_event(self, event: InputEvent) -> Optional[str]:
        """Find which action an event belongs to."""
        for action, mappings in self._action_map.items():
            for mapping in mappings:
                if mapping.matches_event(event):
                    return action
        return None
    
    def get_event_mapping(self, action: str, event: InputEvent, exact_match: bool = False) -> Optional[ActionMapping]:
        """Get the mapping for a specific event in an action."""
        if action not in self._action_map:
            return None
        
        for mapping in self._action_map[action]:
            if mapping.matches_event(event, exact_match):
                return mapping
        
        return None
    
    # ========================================================================
    # Default Actions
    # ========================================================================
    
    def load_default_actions(self) -> None:
        """Load common default actions for games."""
        # Movement
        self.add_action("ui_left", deadzone=0.5)
        self.add_action("ui_right", deadzone=0.5)
        self.add_action("ui_up", deadzone=0.5)
        self.add_action("ui_down", deadzone=0.5)
        self.add_action("move_left", deadzone=0.5)
        self.add_action("move_right", deadzone=0.5)
        self.add_action("move_up", deadzone=0.5)
        self.add_action("move_down", deadzone=0.5)
        self.add_action("run", deadzone=0.5)
        
        # Actions
        self.add_action("ui_accept", deadzone=0.5)
        self.add_action("ui_cancel", deadzone=0.5)
        self.add_action("ui_select", deadzone=0.5)
        self.add_action("jump", deadzone=0.5)
        self.add_action("attack", deadzone=0.5)
        self.add_action("interact", deadzone=0.5)
        self.add_action("fire", deadzone=0.5)
        self.add_action("aim", deadzone=0.5)
        self.add_action("reload", deadzone=0.5)
        self.add_action("use_item", deadzone=0.5)
        
        # Menu
        self.add_action("ui_menu", deadzone=0.5)
        self.add_action("ui_pause", deadzone=0.5)
        self.add_action("inventory", deadzone=0.5)
        self.add_action("map", deadzone=0.5)
        self.add_action("pause", deadzone=0.5)
        
        # Map events
        self._map_default_keys()
        
        self._default_actions = set(self._action_map.keys())
        logger.info("Loaded default actions")
    
    def _map_default_keys(self) -> None:
        """Map default keyboard and joypad inputs to actions."""
        # UI Navigation
        self.action_add_event("ui_left", self._create_key_event(Key.LEFT))
        self.action_add_event("ui_left", self._create_key_event(Key.A))
        self.action_add_event("ui_left", self._create_joy_axis_event(JoyAxis.LEFT_X, -1.0))
        self.action_add_event("ui_left", self._create_joy_button_event(JoyButton.DPAD_LEFT))
        
        self.action_add_event("ui_right", self._create_key_event(Key.RIGHT))
        self.action_add_event("ui_right", self._create_key_event(Key.D))
        self.action_add_event("ui_right", self._create_joy_axis_event(JoyAxis.LEFT_X, 1.0))
        self.action_add_event("ui_right", self._create_joy_button_event(JoyButton.DPAD_RIGHT))
        
        self.action_add_event("ui_up", self._create_key_event(Key.UP))
        self.action_add_event("ui_up", self._create_key_event(Key.W))
        self.action_add_event("ui_up", self._create_joy_axis_event(JoyAxis.LEFT_Y, -1.0))
        self.action_add_event("ui_up", self._create_joy_button_event(JoyButton.DPAD_UP))
        
        self.action_add_event("ui_down", self._create_key_event(Key.DOWN))
        self.action_add_event("ui_down", self._create_key_event(Key.S))
        self.action_add_event("ui_down", self._create_joy_axis_event(JoyAxis.LEFT_Y, 1.0))
        self.action_add_event("ui_down", self._create_joy_button_event(JoyButton.DPAD_DOWN))
        
        # Movement
        self.action_add_event("move_left", self._create_key_event(Key.A))
        self.action_add_event("move_left", self._create_key_event(Key.LEFT))
        self.action_add_event("move_left", self._create_joy_axis_event(JoyAxis.LEFT_X, -1.0))
        
        self.action_add_event("move_right", self._create_key_event(Key.D))
        self.action_add_event("move_right", self._create_key_event(Key.RIGHT))
        self.action_add_event("move_right", self._create_joy_axis_event(JoyAxis.LEFT_X, 1.0))
        
        self.action_add_event("move_up", self._create_key_event(Key.W))
        self.action_add_event("move_up", self._create_key_event(Key.UP))
        self.action_add_event("move_up", self._create_joy_axis_event(JoyAxis.LEFT_Y, -1.0))
        
        self.action_add_event("move_down", self._create_key_event(Key.S))
        self.action_add_event("move_down", self._create_key_event(Key.DOWN))
        self.action_add_event("move_down", self._create_joy_axis_event(JoyAxis.LEFT_Y, 1.0))
        
        self.action_add_event("run", self._create_key_event(Key.SHIFT))
        self.action_add_event("run", self._create_joy_button_event(JoyButton.LEFT_STICK))
        
        # Actions
        self.action_add_event("ui_accept", self._create_key_event(Key.ENTER))
        self.action_add_event("ui_accept", self._create_key_event(Key.SPACE))
        self.action_add_event("ui_accept", self._create_joy_button_event(JoyButton.A))
        
        self.action_add_event("ui_cancel", self._create_key_event(Key.ESCAPE))
        self.action_add_event("ui_cancel", self._create_key_event(Key.BACKSPACE))
        self.action_add_event("ui_cancel", self._create_joy_button_event(JoyButton.B))
        
        self.action_add_event("ui_select", self._create_key_event(Key.SPACE))
        self.action_add_event("ui_select", self._create_joy_button_event(JoyButton.X))
        
        self.action_add_event("jump", self._create_key_event(Key.SPACE))
        self.action_add_event("jump", self._create_joy_button_event(JoyButton.A))
        
        self.action_add_event("attack", self._create_key_event(Key.CTRL))
        self.action_add_event("attack", self._create_joy_button_event(JoyButton.X))
        self.action_add_event("attack", self._create_mouse_button_event(MouseButton.LEFT))
        
        self.action_add_event("interact", self._create_key_event(Key.E))
        self.action_add_event("interact", self._create_joy_button_event(JoyButton.Y))
        
        self.action_add_event("fire", self._create_mouse_button_event(MouseButton.LEFT))
        self.action_add_event("fire", self._create_joy_axis_event(JoyAxis.TRIGGER_RIGHT, 1.0))
        
        self.action_add_event("aim", self._create_mouse_button_event(MouseButton.RIGHT))
        self.action_add_event("aim", self._create_joy_axis_event(JoyAxis.TRIGGER_LEFT, 1.0))
        
        self.action_add_event("reload", self._create_key_event(Key.R))
        self.action_add_event("reload", self._create_joy_button_event(JoyButton.B))
        
        self.action_add_event("use_item", self._create_key_event(Key.Q))
        self.action_add_event("use_item", self._create_joy_button_event(JoyButton.LEFT_SHOULDER))
        
        # Menu
        self.action_add_event("ui_menu", self._create_key_event(Key.ESCAPE))
        self.action_add_event("ui_menu", self._create_joy_button_event(JoyButton.START))
        
        self.action_add_event("ui_pause", self._create_key_event(Key.ESCAPE))
        self.action_add_event("ui_pause", self._create_joy_button_event(JoyButton.START))
        
        self.action_add_event("inventory", self._create_key_event(Key.I))
        self.action_add_event("inventory", self._create_joy_button_event(JoyButton.BACK))
        
        self.action_add_event("map", self._create_key_event(Key.M))
        self.action_add_event("map", self._create_joy_button_event(JoyButton.GUIDE))
        
        self.action_add_event("pause", self._create_key_event(Key.ESCAPE))
        self.action_add_event("pause", self._create_joy_button_event(JoyButton.START))
    
    def _create_key_event(self, keycode: Key, pressed: bool = True) -> InputEventKey:
        """Create a key event."""
        return InputEventKey(
            keycode=keycode,
            physical_keycode=keycode,
            key_label=keycode,
            pressed=pressed
        )
    
    def _create_joy_button_event(self, button: JoyButton, pressed: bool = True) -> InputEventJoypadButton:
        """Create a joypad button event."""
        return InputEventJoypadButton(
            button_index=button,
            pressed=pressed
        )
    
    def _create_joy_axis_event(self, axis: JoyAxis, value: float) -> InputEventJoypadMotion:
        """Create a joypad axis event."""
        return InputEventJoypadMotion(
            axis=axis,
            axis_value=value
        )
    
    def _create_mouse_button_event(self, button: MouseButton, pressed: bool = True) -> InputEventMouseButton:
        """Create a mouse button event."""
        return InputEventMouseButton(
            button_index=button,
            pressed=pressed
        )
    
    def clear_default_actions(self) -> None:
        """Remove all default actions while keeping custom ones."""
        for action in list(self._action_map.keys()):
            if action in self._default_actions:
                self.erase_action(action)
        self._default_actions.clear()
        logger.info("Cleared default actions")
    
    def is_default_action(self, action: str) -> bool:
        """Check if an action is a default action."""
        return action in self._default_actions
    
    # ========================================================================
    # Utility
    # ========================================================================
    
    def serialize_action(self, action: str) -> Dict:
        """Serialize an action to a dictionary."""
        if action not in self._action_map:
            return {}
        
        return {
            "name": action,
            "deadzone": self._action_deadzones.get(action, 0.5),
            "events": [
                self._serialize_event(mapping.event) 
                for mapping in self._action_map[action]
            ]
        }
    
    def deserialize_action(self, data: Dict) -> None:
        """Deserialize an action from a dictionary."""
        name = data.get("name", "")
        deadzone = data.get("deadzone", 0.5)
        
        self.add_action(name, deadzone)
        
        for event_data in data.get("events", []):
            event = self._deserialize_event(event_data)
            if event:
                self.action_add_event(name, event, deadzone)
    
    def _serialize_event(self, event: InputEvent) -> Dict:
        """Serialize an input event to a dictionary."""
        data = {
            "type": event.get_type().name
        }
        
        if isinstance(event, InputEventKey):
            data["keycode"] = event.keycode.value
            data["physical_keycode"] = event.physical_keycode.value
            data["key_label"] = event.key_label.value
            data["pressed"] = event.pressed
        
        elif isinstance(event, InputEventMouseButton):
            data["button"] = event.button_index.value
            data["pressed"] = event.pressed
        
        elif isinstance(event, InputEventJoypadButton):
            data["button"] = event.button_index.value
            data["pressed"] = event.pressed
        
        elif isinstance(event, InputEventJoypadMotion):
            data["axis"] = event.axis.value
            data["value"] = event.axis_value
        
        return data
    
    def _deserialize_event(self, data: Dict) -> Optional[InputEvent]:
        """Deserialize an input event from a dictionary."""
        event_type = data.get("type", "")
        
        if event_type == "KEY":
            return InputEventKey(
                keycode=Key(data.get("keycode", 0)),
                physical_keycode=Key(data.get("physical_keycode", 0)),
                key_label=Key(data.get("key_label", 0)),
                pressed=data.get("pressed", True)
            )
        
        elif event_type == "MOUSE_BUTTON":
            return InputEventMouseButton(
                button_index=MouseButton(data.get("button", 0)),
                pressed=data.get("pressed", True)
            )
        
        elif event_type == "JOY_BUTTON":
            return InputEventJoypadButton(
                button_index=JoyButton(data.get("button", 0)),
                pressed=data.get("pressed", True)
            )
        
        elif event_type == "JOY_MOTION":
            return InputEventJoypadMotion(
                axis=JoyAxis(data.get("axis", 0)),
                axis_value=data.get("value", 0.0)
            )
        
        return None


# Global singleton accessor
def get_input_map() -> InputMap:
    """Get the global InputMap singleton."""
    return InputMap.get_singleton()
