# /**************************************************************************/
# /*  godot_input_demo.py                                                   */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Demo of the Godot Input System port.

This example demonstrates the key features of the Godot Input System
ported to Python, including:
- Action-based input mapping
- Keyboard and mouse input
- Joypad/gamepad support
- Motion sensors
- Vibration/haptics
- Touch emulation
"""

import sys
import time
sys.path.insert(0, "..")

from engine.input.input_godot import Input
from engine.input.input_map import InputMap
from engine.input.input_enums import (
    Key, MouseButton, JoyButton, JoyAxis, MouseButtonMask
)
from engine.input.input_events import (
    InputEventKey, InputEventMouseButton, InputEventJoypadButton,
    InputEventJoypadMotion
)


def demo_action_system():
    """Demonstrate action-based input."""
    print("\n" + "=" * 60)
    print("ACTION SYSTEM DEMO")
    print("=" * 60)
    
    inp = Input.get_singleton()
    inp_map = InputMap.get_singleton()
    
    # Setup actions
    print("\nSetting up actions...")
    inp_map.load_default_actions()
    
    actions = inp_map.get_actions()
    print(f"Available actions: {len(actions)}")
    for action in actions[:10]:  # Show first 10
        events = inp_map.action_get_events(action)
        print(f"  - {action} ({len(events)} events, deadzone={inp_map.action_get_deadzone(action)})")
    
    # Programmatically press an action
    print("\nSimulating 'jump' action press...")
    inp.action_press("jump", strength=1.0)
    
    print(f"  is_action_pressed('jump'): {inp.is_action_pressed('jump')}")
    print(f"  get_action_strength('jump'): {inp.get_action_strength('jump')}")
    
    # Get 2D movement vector
    inp.action_press("move_right", strength=1.0)
    vector = inp.get_vector("move_left", "move_right", "move_up", "move_down")
    print(f"\nMovement vector (right pressed): {vector}")
    
    inp.action_release("jump")
    inp.action_release("move_right")
    
    print(f"\nAfter releasing:")
    print(f"  is_action_pressed('jump'): {inp.is_action_pressed('jump')}")


def demo_keyboard_input():
    """Demonstrate keyboard input."""
    print("\n" + "=" * 60)
    print("KEYBOARD INPUT DEMO")
    print("=" * 60)
    
    inp = Input.get_singleton()
    
    # Simulate key presses
    print("\nSimulating key presses...")
    
    # Press W key
    event = InputEventKey(
        keycode=Key.W,
        physical_keycode=Key.W,
        key_label=Key.W,
        pressed=True
    )
    inp._parse_input_event_impl(event, False)
    
    print(f"  is_key_pressed(Key.W): {inp.is_key_pressed(Key.W)}")
    print(f"  is_physical_key_pressed(Key.W): {inp.is_physical_key_pressed(Key.W)}")
    print(f"  is_any_key_pressed(): {inp.is_any_key_pressed()}")
    print(f"  is_anything_pressed(): {inp.is_anything_pressed()}")
    
    # Release key
    event.pressed = False
    inp._parse_input_event_impl(event, False)
    
    print(f"\nAfter release:")
    print(f"  is_key_pressed(Key.W): {inp.is_key_pressed(Key.W)}")


def demo_mouse_input():
    """Demonstrate mouse input."""
    print("\n" + "=" * 60)
    print("MOUSE INPUT DEMO")
    print("=" * 60)
    
    inp = Input.get_singleton()
    
    # Simulate mouse click
    print("\nSimulating mouse button press...")
    
    click_event = InputEventMouseButton(
        button_index=MouseButton.LEFT,
        pressed=True,
        button_mask=MouseButtonMask.LEFT,
        position=(100, 200)
    )
    inp._parse_input_event_impl(click_event, False)
    
    print(f"  is_mouse_button_pressed(MouseButton.LEFT): {inp.is_mouse_button_pressed(MouseButton.LEFT)}")
    print(f"  Mouse button mask: 0x{inp.get_mouse_button_mask():08x}")
    print(f"  Mouse position: {inp.get_mouse_position()}")
    
    # Release
    click_event.pressed = False
    click_event.button_mask = 0
    inp._parse_input_event_impl(click_event, False)
    
    print(f"\nAfter release:")
    print(f"  is_mouse_button_pressed(MouseButton.LEFT): {inp.is_mouse_button_pressed(MouseButton.LEFT)}")


def demo_joypad_input():
    """Demonstrate joypad/gamepad input."""
    print("\n" + "=" * 60)
    print("JOYPAD INPUT DEMO")
    print("=" * 60)
    
    inp = Input.get_singleton()
    
    # Simulate joypad connection
    print("\nSimulating joypad connection...")
    inp.joy_connection_changed(
        device=0,
        connected=True,
        name="Xbox 360 Controller",
        guid="030000005e0400008e02000000007200"
    )
    
    print(f"  Joypad name: {inp.get_joy_name(0)}")
    print(f"  Joypad GUID: {inp.get_joy_guid(0)}")
    print(f"  Connected joypads: {inp.get_connected_joypads()}")
    print(f"  Is known mapping: {inp.is_joy_known(0)}")
    
    # Simulate button press
    print("\nSimulating joypad button press...")
    
    button_event = InputEventJoypadButton(
        device=0,
        button_index=JoyButton.A,
        pressed=True
    )
    inp._parse_input_event_impl(button_event, False)
    
    print(f"  is_joy_button_pressed(0, JoyButton.A): {inp.is_joy_button_pressed(0, JoyButton.A)}")
    
    # Simulate axis movement
    print("\nSimulating joypad axis movement...")
    
    axis_event = InputEventJoypadMotion(
        device=0,
        axis=JoyAxis.LEFT_X,
        axis_value=0.75
    )
    inp._parse_input_event_impl(axis_event, False)
    
    print(f"  get_joy_axis(0, JoyAxis.LEFT_X): {inp.get_joy_axis(0, JoyAxis.LEFT_X)}")
    
    # Test vibration
    print("\nTesting vibration...")
    inp.start_joy_vibration(0, weak_magnitude=0.5, strong_magnitude=0.8, duration=1.0)
    
    strength = inp.get_joy_vibration_strength(0)
    print(f"  Vibration strength: weak={strength[0]}, strong={strength[1]}")
    print(f"  Vibration duration: {inp.get_joy_vibration_duration(0)}s")
    print(f"  Has vibration: {inp.has_joy_vibration(0)}")
    
    # Disconnect
    inp.joy_connection_changed(device=0, connected=False)
    print(f"\nAfter disconnect:")
    print(f"  Connected joypads: {inp.get_connected_joypads()}")


def demo_sensors():
    """Demonstrate motion sensors."""
    print("\n" + "=" * 60)
    print("MOTION SENSOR DEMO")
    print("=" * 60)
    
    inp = Input.get_singleton()
    
    print("\nSetting sensor values...")
    
    # Gravity (pointing down on Earth)
    inp.set_gravity((0.0, 0.0, -9.8))
    print(f"  Gravity: {inp.get_gravity()}")
    
    # Accelerometer
    inp.set_accelerometer((0.1, 0.2, 9.7))
    print(f"  Accelerometer: {inp.get_accelerometer()}")
    
    # Gyroscope
    inp.set_gyroscope((0.5, -0.3, 1.2))
    print(f"  Gyroscope: {inp.get_gyroscope()}")
    
    # Magnetometer
    inp.set_magnetometer((25.0, 0.0, 45.0))
    print(f"  Magnetometer: {inp.get_magnetometer()}")


def demo_mappings():
    """Demonstrate controller mappings."""
    print("\n" + "=" * 60)
    print("CONTROLLER MAPPING DEMO")
    print("=" * 60)
    
    inp = Input.get_singleton()
    
    print(f"\nDefault mappings loaded: {len(inp.map_db)}")
    
    # Show some mappings
    for mapping in inp.map_db[:3]:
        print(f"  - {mapping.name} (UID: {mapping.uid[:16]}...)")
        print(f"    Bindings: {len(mapping.bindings)}")
    
    # Add custom mapping
    print("\nAdding custom mapping...")
    custom_mapping = "00000000,Custom Controller,a:b0,b:b1,x:b2,y:b3"
    inp.parse_mapping(custom_mapping)
    
    print(f"  Total mappings: {len(inp.map_db)}")


def demo_event_accumulation():
    """Demonstrate event accumulation."""
    print("\n" + "=" * 60)
    print("EVENT ACCUMULATION DEMO")
    print("=" * 60)
    
    inp = Input.get_singleton()
    
    # Enable accumulation
    inp.set_use_accumulated_input(True)
    print(f"\nAccumulation enabled: {inp.is_using_accumulated_input()}")
    
    # Queue some events
    print("\nQueuing events...")
    for i in range(5):
        event = InputEventKey(
            keycode=Key.SPACE,
            pressed=(i % 2 == 0)
        )
        inp.parse_input_event(event)
        print(f"  Buffered events: {len(inp.buffered_events)}")
    
    # Flush
    print("\nFlushing buffered events...")
    inp.flush_buffered_events()
    print(f"  Buffered events after flush: {len(inp.buffered_events)}")


def demo_velocity_tracking():
    """Demonstrate velocity tracking."""
    print("\n" + "=" * 60)
    print("VELOCITY TRACKING DEMO")
    print("=" * 60)
    
    from engine.input.input_godot import VelocityTrack
    
    track = VelocityTrack()
    track.reset()
    
    print("\nSimulating mouse movement...")
    
    # Simulate some movement
    movements = [
        (10, 0),   # 10 pixels right
        (10, 0),   # 10 pixels right
        (5, 5),    # diagonal
        (0, 10),   # down
    ]
    
    for delta in movements:
        track.update(delta, delta)
        velocity = track.velocity
        print(f"  Movement: {delta:15} -> Velocity: ({velocity[0]:.1f}, {velocity[1]:.1f})")


def demo_emulation():
    """Demonstrate touch/mouse emulation."""
    print("\n" + "=" * 60)
    print("INPUT EMULATION DEMO")
    print("=" * 60)
    
    inp = Input.get_singleton()
    
    print("\nTouch from mouse emulation...")
    inp.set_emulate_touch_from_mouse(True)
    print(f"  Enabled: {inp.is_emulating_touch_from_mouse()}")
    
    print("\nMouse from touch emulation...")
    inp.set_emulate_mouse_from_touch(True)
    print(f"  Enabled: {inp.is_emulating_mouse_from_touch()}")
    
    inp.set_emulate_touch_from_mouse(False)
    inp.set_emulate_mouse_from_touch(False)


def demo_complete_game_example():
    """Demonstrate complete game input setup."""
    print("\n" + "=" * 60)
    print("COMPLETE GAME INPUT SETUP")
    print("=" * 60)
    
    # Reset singletons
    Input._instance = None
    InputMap._instance = None
    
    inp = Input.get_singleton()
    inp_map = InputMap.get_singleton()
    
    print("\n1. Loading default action mappings...")
    inp_map.load_default_actions()
    
    print("\n2. Adding custom actions...")
    custom_actions = [
        ("crouch", 0.3),
        ("sprint", 0.3),
        ("melee", 0.2),
        ("throw", 0.2),
        ("swap_weapon", 0.1),
    ]
    
    for action, deadzone in custom_actions:
        inp_map.add_action(action, deadzone)
        print(f"  Added: {action} (deadzone={deadzone})")
    
    print("\n3. Simulating player input...")
    
    # Simulate movement
    inputs_to_simulate = [
        ("move_right", 1.0),
        ("move_up", 0.5),
        ("sprint", 1.0),
        ("jump", 1.0),
        ("fire", 1.0),
    ]
    
    for action, strength in inputs_to_simulate:
        inp.action_press(action, strength)
    
    # Query state
    print("\n4. Querying input state...")
    
    movement = inp.get_vector("move_left", "move_right", "move_up", "move_down")
    print(f"  Movement vector: ({movement[0]:.2f}, {movement[1]:.2f})")
    
    print(f"  Is jumping: {inp.is_action_pressed('jump')}")
    print(f"  Jump strength: {inp.get_action_strength('jump')}")
    
    print(f"  Is firing: {inp.is_action_pressed('fire')}")
    print(f"  Is sprinting: {inp.is_action_pressed('sprint')}")
    
    # Check for any input
    print(f"\n  Anything pressed: {inp.is_anything_pressed()}")
    
    # Release all
    print("\n5. Releasing all inputs...")
    for action, _ in inputs_to_simulate:
        inp.action_release(action)
    
    print(f"  Anything pressed: {inp.is_anything_pressed()}")


def main():
    """Run all demos."""
    print("\n" + "#" * 60)
    print("# GODOT INPUT SYSTEM DEMO")
    print("# Python Port of Godot Engine Input System")
    print("#" * 60)
    
    demo_action_system()
    demo_keyboard_input()
    demo_mouse_input()
    demo_joypad_input()
    demo_sensors()
    demo_mappings()
    demo_event_accumulation()
    demo_velocity_tracking()
    demo_emulation()
    demo_complete_game_example()
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    print("\nThe Godot Input System has been successfully ported to Python!")
    print("All features demonstrated:")
    print("  - Action-based input mapping")
    print("  - Keyboard/mouse/joypad input")
    print("  - SDL controller mappings")
    print("  - Motion sensors")
    print("  - Vibration/haptics")
    print("  - Event accumulation")
    print("  - Touch/mouse emulation")
    print("  - Velocity tracking")
    print()


if __name__ == "__main__":
    main()
