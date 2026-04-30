# /**************************************************************************/
# /*  __init__.py                                                           */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Input management system - Godot Engine port to Python.

This module provides a complete port of Godot Engine's input system:
- Input: Main singleton for query methods and state
- InputMap: Action to event mapping
- InputEvent: Event hierarchy for all input types
- Joypad support with SDL controller mappings
- Motion sensors (accelerometer, gyroscope, magnetometer)
- Vibration/haptics
"""

# Legacy input system (for backward compatibility)
from engine.input.input_manager import InputManager, get_input_manager
from engine.input.action_map import ActionMap, InputAction
from engine.input.tablet import (
    TabletInputManager, TabletDevice, TabletEvent,
    TabletHandler, TabletDeviceType, get_tablet_manager
)

# Godot input system (new)
from engine.input.input_enums import (
    JoyButton, JoyAxis, Key, MouseButton, MouseButtonMask,
    MouseMode, CursorShape, HatMask, HatDir, JoyAxisRange,
    JoyEventType, InputEventType, InputConstants
)

from engine.input.input_events import (
    InputEvent, InputEventKey, InputEventMouseButton, InputEventMouseMotion,
    InputEventScreenTouch, InputEventScreenDrag, InputEventJoypadButton,
    InputEventJoypadMotion, InputEventGesture, InputEventAction,
    mouse_button_to_mask
)

from engine.input.input_godot import (
    Input, Joypad, JoypadFeatures, VibrationInfo, MotionInfo,
    VelocityTrack, JoyBinding, JoyBindingInput, JoyBindingOutput,
    JoyDeviceMapping, ActionState
)

from engine.input.input_map import (
    InputMap, ActionMapping, InputEventMagnitude, get_input_map
)

import logging

logger = logging.getLogger(__name__)

__all__ = [
    # Legacy system
    "InputManager",
    "get_input_manager",
    "ActionMap",
    "InputAction",
    # Tablet support
    "TabletInputManager",
    "get_tablet_manager",
    "TabletDevice",
    "TabletEvent",
    "TabletHandler",
    "TabletDeviceType",
    # Godot Enums
    "JoyButton",
    "JoyAxis",
    "Key",
    "MouseButton",
    "MouseButtonMask",
    "MouseMode",
    "CursorShape",
    "HatMask",
    "HatDir",
    "JoyAxisRange",
    "JoyEventType",
    "InputEventType",
    "InputConstants",
    # Godot Events
    "InputEvent",
    "InputEventKey",
    "InputEventMouseButton",
    "InputEventMouseMotion",
    "InputEventScreenTouch",
    "InputEventScreenDrag",
    "InputEventJoypadButton",
    "InputEventJoypadMotion",
    "InputEventGesture",
    "InputEventAction",
    "mouse_button_to_mask",
    # Godot Input System
    "Input",
    "Joypad",
    "JoypadFeatures",
    "VibrationInfo",
    "MotionInfo",
    "VelocityTrack",
    "JoyBinding",
    "JoyBindingInput",
    "JoyBindingOutput",
    "JoyDeviceMapping",
    "ActionState",
    # Godot InputMap
    "InputMap",
    "ActionMapping",
    "InputEventMagnitude",
    "get_input_map",
]
