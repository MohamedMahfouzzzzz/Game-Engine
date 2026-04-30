# /**************************************************************************/
# /*  test_input_godot.py                                                   */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Unit tests for Godot Input System port."""

import unittest
import time
from typing import Tuple

from engine.input.input_enums import (
    JoyButton, JoyAxis, Key, MouseButton, MouseButtonMask,
    MouseMode, CursorShape, HatMask, InputConstants
)
from engine.input.input_events import (
    InputEventKey, InputEventMouseButton, InputEventMouseMotion,
    InputEventScreenTouch, InputEventScreenDrag, InputEventJoypadButton,
    InputEventJoypadMotion, InputEventGesture, InputEventAction,
    mouse_button_to_mask
)
from engine.input.input_godot import (
    Input, VelocityTrack, JoyBinding, JoyDeviceMapping,
    Joypad, VibrationInfo, MotionInfo
)
from engine.input.input_map import (
    InputMap, ActionMapping, get_input_map
)


class TestInputEnums(unittest.TestCase):
    """Test input enum definitions."""
    
    def test_joybutton_values(self):
        """Test joypad button enum values match SDL."""
        self.assertEqual(JoyButton.A, 0)
        self.assertEqual(JoyButton.B, 1)
        self.assertEqual(JoyButton.X, 2)
        self.assertEqual(JoyButton.Y, 3)
        self.assertEqual(JoyButton.INVALID, -1)
        self.assertEqual(int(JoyButton.MAX), 26)
    
    def test_joyaxis_values(self):
        """Test joypad axis enum values match SDL."""
        self.assertEqual(JoyAxis.LEFT_X, 0)
        self.assertEqual(JoyAxis.LEFT_Y, 1)
        self.assertEqual(JoyAxis.TRIGGER_LEFT, 4)
        self.assertEqual(JoyAxis.TRIGGER_RIGHT, 5)
        self.assertEqual(JoyAxis.INVALID, -1)
        self.assertEqual(int(JoyAxis.MAX), 6)
    
    def test_mouse_button_mask(self):
        """Test mouse button bitmask generation."""
        self.assertEqual(mouse_button_to_mask(MouseButton.LEFT), MouseButtonMask.LEFT)
        self.assertEqual(mouse_button_to_mask(MouseButton.RIGHT), MouseButtonMask.RIGHT)
        self.assertEqual(mouse_button_to_mask(MouseButton.MIDDLE), MouseButtonMask.MIDDLE)
        
        # Test combining masks
        combined = MouseButtonMask.LEFT | MouseButtonMask.RIGHT
        self.assertIn(MouseButtonMask.LEFT, [combined & MouseButtonMask.LEFT])
        self.assertIn(MouseButtonMask.RIGHT, [combined & MouseButtonMask.RIGHT])
    
    def test_key_constants(self):
        """Test key code constants."""
        self.assertEqual(Key.SPACE, 32)
        self.assertEqual(Key.ESCAPE, 16777217)
        self.assertEqual(Key.ENTER, 16777220)
        self.assertEqual(Key.A, 65)
        self.assertEqual(Key.Z, 90)


class TestInputEvents(unittest.TestCase):
    """Test input event classes."""
    
    def test_key_event(self):
        """Test keyboard event creation and properties."""
        event = InputEventKey(
            keycode=Key.SPACE,
            physical_keycode=Key.SPACE,
            key_label=Key.SPACE,
            pressed=True,
            ctrl_pressed=True
        )
        
        self.assertTrue(event.is_pressed())
        self.assertFalse(event.is_echo())
        self.assertEqual(event.get_keycode(), Key.SPACE)
        self.assertTrue(event.ctrl_pressed)
    
    def test_mouse_button_event(self):
        """Test mouse button event."""
        event = InputEventMouseButton(
            button_index=MouseButton.LEFT,
            pressed=True,
            position=(100, 200),
            double_click=True
        )
        
        self.assertTrue(event.is_pressed())
        self.assertTrue(event.is_double_click())
        self.assertEqual(event.get_position(), (100, 200))
        self.assertEqual(event.get_button_index(), MouseButton.LEFT)
    
    def test_mouse_motion_event(self):
        """Test mouse motion event with accumulation."""
        event1 = InputEventMouseMotion(
            position=(10, 20),
            relative=(5, 5),
            velocity=(100, 100)
        )
        
        event2 = InputEventMouseMotion(
            position=(15, 25),
            relative=(5, 5),
            velocity=(150, 150)
        )
        
        # Test accumulation
        result = event1.accumulate(event2)
        self.assertTrue(result)
        self.assertEqual(event1.relative, (10, 10))
        self.assertEqual(event1.position, (15, 25))
        self.assertEqual(event1.velocity, (150, 150))
    
    def test_mouse_motion_no_accumulate_different_device(self):
        """Test motion events don't accumulate across devices."""
        event1 = InputEventMouseMotion(device=0, relative=(1, 1))
        event2 = InputEventMouseMotion(device=1, relative=(1, 1))
        
        result = event1.accumulate(event2)
        self.assertFalse(result)
    
    def test_screen_touch_event(self):
        """Test touch screen event."""
        event = InputEventScreenTouch(
            index=1,
            pressed=True,
            position=(50, 75),
            double_tap=True
        )
        
        self.assertTrue(event.is_pressed())
        self.assertTrue(event.is_double_tap())
        self.assertEqual(event.get_index(), 1)
        self.assertEqual(event.get_position(), (50, 75))
    
    def test_joy_button_event(self):
        """Test joypad button event."""
        event = InputEventJoypadButton(
            device=0,
            button_index=JoyButton.A,
            pressed=True,
            pressure=1.0
        )
        
        self.assertTrue(event.is_pressed())
        self.assertEqual(event.get_button_index(), JoyButton.A)
        self.assertEqual(event.get_pressure(), 1.0)
    
    def test_joy_motion_event(self):
        """Test joypad axis motion event."""
        event = InputEventJoypadMotion(
            device=0,
            axis=JoyAxis.LEFT_X,
            axis_value=0.75
        )
        
        self.assertEqual(event.get_axis(), JoyAxis.LEFT_X)
        self.assertEqual(event.get_axis_value(), 0.75)
    
    def test_gesture_event(self):
        """Test gesture event."""
        event = InputEventGesture(
            gesture_type="pinch",
            scale=2.0,
            rotation=45.0
        )
        
        self.assertEqual(event.get_gesture_type(), "pinch")
        self.assertEqual(event.get_scale(), 2.0)
        self.assertEqual(event.get_rotation(), 45.0)
    
    def test_action_event(self):
        """Test virtual action event."""
        event = InputEventAction(
            action="jump",
            pressed=True,
            strength=0.8
        )
        
        self.assertTrue(event.is_pressed())
        self.assertEqual(event.get_action(), "jump")
        self.assertEqual(event.get_strength(), 0.8)


class TestVelocityTrack(unittest.TestCase):
    """Test velocity tracking."""
    
    def test_velocity_tracking(self):
        """Test velocity calculation."""
        track = VelocityTrack()
        track.reset()
        
        # Simulate movement over time
        track.update((10, 0), (10, 0))
        track.update((10, 0), (10, 0))
        
        # Velocity should be calculated
        velocity = track.velocity
        self.assertGreater(abs(velocity[0]), 0)
    
    def test_velocity_reset(self):
        """Test velocity track reset."""
        track = VelocityTrack()
        track.reset()
        
        track.update((100, 100), (100, 100))
        track.reset()
        
        self.assertEqual(track.velocity, (0.0, 0.0))
        self.assertEqual(track.accum, (0.0, 0.0))


class TestInputSingleton(unittest.TestCase):
    """Test Input singleton class."""
    
    def setUp(self):
        """Reset Input singleton state."""
        Input._instance = None
    
    def test_singleton(self):
        """Test Input is a singleton."""
        input1 = Input.get_singleton()
        input2 = Input.get_singleton()
        self.assertIs(input1, input2)
    
    def test_key_press_detection(self):
        """Test key press detection."""
        inp = Input.get_singleton()
        inp.set_disable_input(False)
        
        # Initially not pressed
        self.assertFalse(inp.is_key_pressed(Key.SPACE))
        
        # Simulate key press
        event = InputEventKey(
            keycode=Key.SPACE,
            physical_keycode=Key.SPACE,
            pressed=True
        )
        inp._parse_input_event_impl(event, False)
        
        self.assertTrue(inp.is_key_pressed(Key.SPACE))
        
        # Simulate key release
        event.pressed = False
        inp._parse_input_event_impl(event, False)
        
        self.assertFalse(inp.is_key_pressed(Key.SPACE))
    
    def test_mouse_button_detection(self):
        """Test mouse button detection."""
        inp = Input.get_singleton()
        
        # Simulate button press
        event = InputEventMouseButton(
            button_index=MouseButton.LEFT,
            pressed=True,
            button_mask=MouseButtonMask.LEFT
        )
        inp._parse_input_event_impl(event, False)
        
        self.assertTrue(inp.is_mouse_button_pressed(MouseButton.LEFT))
        self.assertEqual(inp.get_mouse_button_mask(), MouseButtonMask.LEFT)
    
    def test_joy_button_detection(self):
        """Test joypad button detection."""
        inp = Input.get_singleton()
        
        # Simulate joypad button press
        event = InputEventJoypadButton(
            device=0,
            button_index=JoyButton.A,
            pressed=True
        )
        inp._parse_input_event_impl(event, False)
        
        self.assertTrue(inp.is_joy_button_pressed(0, JoyButton.A))
    
    def test_joy_axis_detection(self):
        """Test joypad axis value."""
        inp = Input.get_singleton()
        
        # Set axis value
        inp.set_joy_axis(0, JoyAxis.LEFT_X, 0.5)
        
        self.assertEqual(inp.get_joy_axis(0, JoyAxis.LEFT_X), 0.5)
    
    def test_disable_input(self):
        """Test global input disable."""
        inp = Input.get_singleton()
        inp.set_disable_input(True)
        
        # Simulate key press (should be ignored)
        event = InputEventKey(
            keycode=Key.SPACE,
            physical_keycode=Key.SPACE,
            pressed=True
        )
        inp._parse_input_event_impl(event, False)
        
        self.assertFalse(inp.is_key_pressed(Key.SPACE))
        
        # Re-enable
        inp.set_disable_input(False)
    
    def test_action_system(self):
        """Test action system."""
        inp = Input.get_singleton()
        
        # Programmatically press action
        inp.action_press("test_action", 0.75)
        
        self.assertTrue(inp.is_action_pressed("test_action"))
        self.assertEqual(inp.get_action_strength("test_action"), 0.75)
        self.assertEqual(inp.get_action_raw_strength("test_action"), 0.75)
        
        # Release action
        inp.action_release("test_action")
        
        self.assertFalse(inp.is_action_pressed("test_action"))
        self.assertEqual(inp.get_action_strength("test_action"), 0.0)
    
    def test_get_axis(self):
        """Test combined axis from two actions."""
        inp = Input.get_singleton()
        
        inp.action_press("move_left", 1.0)
        result = inp.get_axis("move_left", "move_right")
        self.assertEqual(result, -1.0)
        
        inp.action_release("move_left")
        inp.action_press("move_right", 1.0)
        result = inp.get_axis("move_left", "move_right")
        self.assertEqual(result, 1.0)
    
    def test_get_vector(self):
        """Test 2D vector from four actions."""
        inp = Input.get_singleton()
        
        inp.action_press("move_right", 1.0)
        vector = inp.get_vector("move_left", "move_right", "move_up", "move_down")
        
        self.assertEqual(vector[0], 1.0)
        self.assertEqual(vector[1], 0.0)
        
        inp.action_release("move_right")
    
    def test_vibration(self):
        """Test vibration state tracking."""
        inp = Input.get_singleton()
        
        # Start vibration (without actual joypad)
        inp.start_joy_vibration(0, 0.5, 0.8, 1.0)
        
        strength = inp.get_joy_vibration_strength(0)
        self.assertEqual(strength[0], 0.5)
        self.assertEqual(strength[1], 0.8)
        self.assertEqual(inp.get_joy_vibration_duration(0), 1.0)
    
    def test_mouse_mode(self):
        """Test mouse mode getters/setters."""
        inp = Input.get_singleton()
        
        # Without platform functions, should return defaults
        self.assertEqual(inp.get_mouse_mode(), MouseMode.VISIBLE)
        self.assertEqual(inp.get_mouse_mode_override(), MouseMode.VISIBLE)
        self.assertFalse(inp.is_mouse_mode_override_enabled())
    
    def test_sensors(self):
        """Test motion sensor data."""
        inp = Input.get_singleton()
        
        # Set sensor values
        inp.set_gravity((0, 0, -9.8))
        inp.set_accelerometer((0.1, 0.2, 9.7))
        inp.set_gyroscope((0.5, 0.3, 0.1))
        inp.set_magnetometer((30, 45, 60))
        
        self.assertEqual(inp.get_gravity(), (0, 0, -9.8))
        self.assertEqual(inp.get_accelerometer(), (0.1, 0.2, 9.7))
        self.assertEqual(inp.get_gyroscope(), (0.5, 0.3, 0.1))
        self.assertEqual(inp.get_magnetometer(), (30, 45, 60))
    
    def test_anything_pressed(self):
        """Test any input detection."""
        inp = Input.get_singleton()
        
        # Initially nothing pressed
        self.assertFalse(inp.is_anything_pressed())
        
        # Press a key
        inp.action_press("test")
        self.assertTrue(inp.is_anything_pressed())
        
        inp.action_release("test")


class TestInputMap(unittest.TestCase):
    """Test InputMap system."""
    
    def setUp(self):
        """Reset InputMap singleton."""
        InputMap._instance = None
    
    def test_singleton(self):
        """Test InputMap is singleton."""
        map1 = InputMap.get_singleton()
        map2 = InputMap.get_singleton()
        self.assertIs(map1, map2)
    
    def test_add_action(self):
        """Test adding actions."""
        inp_map = InputMap.get_singleton()
        
        inp_map.add_action("jump", deadzone=0.2)
        
        self.assertTrue(inp_map.has_action("jump"))
        self.assertEqual(inp_map.action_get_deadzone("jump"), 0.2)
    
    def test_add_event_to_action(self):
        """Test adding input events to actions."""
        inp_map = InputMap.get_singleton()
        
        inp_map.add_action("jump")
        
        key_event = InputEventKey(
            keycode=Key.SPACE,
            pressed=True
        )
        inp_map.action_add_event("jump", key_event)
        
        events = inp_map.action_get_events("jump")
        self.assertEqual(len(events), 1)
        self.assertIsInstance(events[0], InputEventKey)
    
    def test_event_matching(self):
        """Test event to action matching."""
        inp_map = InputMap.get_singleton()
        
        inp_map.add_action("fire")
        
        mouse_event = InputEventMouseButton(
            button_index=MouseButton.LEFT,
            pressed=True
        )
        inp_map.action_add_event("fire", mouse_event)
        
        # Check matching
        self.assertTrue(inp_map.event_is_action(mouse_event, "fire"))
        self.assertFalse(inp_map.event_is_action(mouse_event, "jump"))
    
    def test_default_actions(self):
        """Test loading default actions."""
        inp_map = InputMap.get_singleton()
        
        inp_map.load_default_actions()
        
        # Check common actions exist
        self.assertTrue(inp_map.has_action("ui_left"))
        self.assertTrue(inp_map.has_action("ui_right"))
        self.assertTrue(inp_map.has_action("ui_accept"))
        self.assertTrue(inp_map.has_action("jump"))
        self.assertTrue(inp_map.has_action("move_left"))
        self.assertTrue(inp_map.has_action("move_right"))


class TestJoypadMapping(unittest.TestCase):
    """Test joypad mapping system."""
    
    def setUp(self):
        """Reset Input singleton."""
        Input._instance = None
    
    def test_mapping_parsing(self):
        """Test SDL mapping string parsing."""
        inp = Input.get_singleton()
        
        # Parse a simple mapping
        mapping_str = "00000000,Test Controller,a:b0,b:b1,x:b2,y:b3"
        inp.parse_mapping(mapping_str)
        
        self.assertGreater(len(inp.map_db), 0)
        self.assertEqual(inp.map_db[-1].uid, "00000000")
        self.assertEqual(inp.map_db[-1].name, "Test Controller")
    
    def test_axis_mapping_parsing(self):
        """Test axis mapping parsing."""
        inp = Input.get_singleton()
        
        mapping_str = "00000000,Test,a:b0,leftx:a0,lefty:a1,+rightx:a2"
        inp.parse_mapping(mapping_str)
        
        mapping = inp.map_db[-1]
        self.assertGreater(len(mapping.bindings), 0)
    
    def test_hat_mapping_parsing(self):
        """Test hat/dpad mapping parsing."""
        inp = Input.get_singleton()
        
        mapping_str = "00000000,Test,dpup:h0.1,dpdown:h0.4,dpleft:h0.8,dpright:h0.2"
        inp.parse_mapping(mapping_str)
        
        mapping = inp.map_db[-1]
        # Should have 4 hat bindings
        hat_bindings = [b for b in mapping.bindings if b.inputType.name == "HAT"]
        self.assertEqual(len(hat_bindings), 4)


class TestTouchEmulation(unittest.TestCase):
    """Test touch/mouse emulation."""
    
    def setUp(self):
        """Reset Input singleton."""
        Input._instance = None
    
    def test_touch_from_mouse_emulation(self):
        """Test touch events from mouse."""
        inp = Input.get_singleton()
        
        inp.set_emulate_touch_from_mouse(True)
        self.assertTrue(inp.is_emulating_touch_from_mouse())
        
        inp.set_emulate_touch_from_mouse(False)
        self.assertFalse(inp.is_emulating_touch_from_mouse())
    
    def test_mouse_from_touch_emulation(self):
        """Test mouse events from touch."""
        inp = Input.get_singleton()
        
        inp.set_emulate_mouse_from_touch(True)
        self.assertTrue(inp.is_emulating_mouse_from_touch())
        
        inp.set_emulate_mouse_from_touch(False)
        self.assertFalse(inp.is_emulating_mouse_from_touch())


class TestEventAccumulation(unittest.TestCase):
    """Test input event accumulation."""
    
    def setUp(self):
        """Reset Input singleton."""
        Input._instance = None
    
    def test_accumulation_enabled(self):
        """Test that accumulation works when enabled."""
        inp = Input.get_singleton()
        
        inp.set_use_accumulated_input(True)
        self.assertTrue(inp.is_using_accumulated_input())
        
        # Events should be buffered
        event = InputEventKey(keycode=Key.SPACE, pressed=True)
        inp.parse_input_event(event)
        
        self.assertEqual(len(inp.buffered_events), 1)
        
        # Flush should clear buffer
        inp.flush_buffered_events()
        self.assertEqual(len(inp.buffered_events), 0)
    
    def test_accumulation_disabled(self):
        """Test that accumulation can be disabled."""
        inp = Input.get_singleton()
        
        inp.set_use_accumulated_input(False)
        self.assertFalse(inp.is_using_accumulated_input())


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete input system."""
    
    def setUp(self):
        """Reset singletons."""
        Input._instance = None
        InputMap._instance = None
    
    def test_full_input_pipeline(self):
        """Test complete input pipeline from event to action."""
        # Setup InputMap
        inp_map = InputMap.get_singleton()
        inp_map.add_action("shoot", deadzone=0.3)
        
        mouse_event = InputEventMouseButton(
            button_index=MouseButton.LEFT,
            pressed=True
        )
        inp_map.action_add_event("shoot", mouse_event, deadzone=0.3)
        
        # Setup Input
        inp = Input.get_singleton()
        
        # Parse event through Input
        inp._parse_input_event_impl(mouse_event, False)
        
        # Check mouse button state
        self.assertTrue(inp.is_mouse_button_pressed(MouseButton.LEFT))
    
    def test_joypad_connection(self):
        """Test joypad connection handling."""
        inp = Input.get_singleton()
        
        # Simulate joypad connection
        inp.joy_connection_changed(
            device=0,
            connected=True,
            name="Test Controller",
            guid="12345678"
        )
        
        self.assertEqual(inp.get_joy_name(0), "Test Controller")
        self.assertEqual(inp.get_joy_guid(0), "12345678")
        self.assertIn(0, inp.get_connected_joypads())
        
        # Disconnect
        inp.joy_connection_changed(
            device=0,
            connected=False
        )
        
        self.assertEqual(inp.get_joy_name(0), "")
        self.assertNotIn(0, inp.get_connected_joypads())


if __name__ == "__main__":
    unittest.main()
