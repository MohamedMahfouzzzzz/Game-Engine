# Godot Input System - Python Port

Complete Python port of Godot Engine's input system, maintaining 1:1 compatibility with the original C++ implementation.

## Overview

This is a line-by-line translation of Godot's input.cpp and input.h to Python, including:
- **Input** singleton: Main input query and state management
- **InputMap**: Action-to-event mapping system
- **InputEvent** hierarchy: All event types (Key, Mouse, Joypad, Touch, etc.)
- **Joypad** support: SDL controller mappings, vibration, motion sensors
- **Motion sensors**: Accelerometer, gyroscope, magnetometer, gravity
- **Event accumulation**: Buffered input processing
- **Touch/mouse emulation**: Cross-device input compatibility

## Architecture

### Core Classes

```
engine.input.input_godot.Input          # Main singleton (like Input::get_singleton())
engine.input.input_map.InputMap         # Action mapping system
engine.input.input_enums                # All enum definitions
engine.input.input_events               # Event class hierarchy
```

### File Structure

```
engine/input/
├── __init__.py           # Module exports
├── input_godot.py        # Input singleton + Joypad classes
├── input_map.py          # InputMap + ActionMapping
├── input_enums.py        # All enums (JoyButton, Key, etc.)
├── input_events.py       # InputEvent hierarchy
├── input_manager.py      # Legacy system (backward compatible)
├── action_map.py         # Legacy action system
└── tablet.py             # Tablet input support
```

## Quick Start

### Basic Usage

```python
from engine.input.input_godot import Input
from engine.input.input_map import InputMap

# Get singletons
inp = Input.get_singleton()
inp_map = InputMap.get_singleton()

# Load default actions
inp_map.load_default_actions()

# Check if jump is pressed
if inp.is_action_pressed("jump"):
    player.jump()

# Get movement vector
movement = inp.get_vector("move_left", "move_right", "move_up", "move_down")
player.velocity = movement * speed
```

### Keyboard Input

```python
from engine.input.input_enums import Key

# Check key state
if inp.is_key_pressed(Key.SPACE):
    print("Space is pressed")

# Check physical key location
if inp.is_physical_key_pressed(Key.W):
    print("W key is pressed (regardless of layout)")

# Check any key
if inp.is_any_key_pressed():
    print("Some key is pressed")
```

### Mouse Input

```python
from engine.input.input_enums import MouseButton

# Check mouse buttons
if inp.is_mouse_button_pressed(MouseButton.LEFT):
    print("Left click")

if inp.is_mouse_button_pressed(MouseButton.RIGHT):
    print("Right click")

# Get mouse position
x, y = inp.get_mouse_position()
print(f"Mouse at: ({x}, {y})")

# Get mouse velocity
velocity = inp.get_last_mouse_velocity()
print(f"Mouse velocity: {velocity}")
```

### Joypad/Gamepad Input

```python
from engine.input.input_enums import JoyButton, JoyAxis

# Check joypad button
if inp.is_joy_button_pressed(0, JoyButton.A):  # Device 0, A button
    print("A button pressed on controller 0")

# Get axis value (analog sticks, triggers)
stick_x = inp.get_joy_axis(0, JoyAxis.LEFT_X)
stick_y = inp.get_joy_axis(0, JoyAxis.LEFT_Y)
print(f"Left stick: ({stick_x}, {stick_y})")

# Vibration (requires platform implementation)
inp.start_joy_vibration(0, weak=0.5, strong=0.8, duration=1.0)
```

### Action System

```python
# Define actions
inp_map.add_action("fire", deadzone=0.3)
inp_map.add_action("aim", deadzone=0.3)

# Map events to actions
from engine.input.input_events import InputEventKey, InputEventMouseButton

# Map space key to "jump"
inp_map.action_add_event("jump", InputEventKey(keycode=Key.SPACE))

# Map mouse left to "fire"
inp_map.action_add_event("fire", InputEventMouseButton(button_index=MouseButton.LEFT))

# Query action state
if inp.is_action_pressed("fire"):
    shoot()

strength = inp.get_action_strength("fire")  # 0.0 - 1.0
raw_strength = inp.get_action_raw_strength("fire")  # Without deadzone

# Get combined axis
steering = inp.get_axis("turn_left", "turn_right")

# Get 2D vector
movement = inp.get_vector("move_left", "move_right", "move_up", "move_down", deadzone=0.1)
```

### Motion Sensors

```python
# Gravity (standard gravity is -9.8 m/s² on Z axis on Earth)
gravity = inp.get_gravity()  # (x, y, z)

# Raw acceleration
accel = inp.get_accelerometer()

# Rotation rate (gyroscope)
gyro = inp.get_gyroscope()

# Compass direction
mag = inp.get_magnetometer()

# Set sensor values (for external sensor integration)
inp.set_gravity((0, 0, -9.8))
inp.set_accelerometer(accel_data)
inp.set_gyroscope(gyro_data)
inp.set_magnetometer(mag_data)
```

### Event Processing

```python
# Parse events (usually done automatically by platform layer)
from engine.input.input_events import InputEventKey

event = InputEventKey(
    keycode=Key.SPACE,
    pressed=True
)
inp.parse_input_event(event)

# Enable event accumulation (buffers events until flush)
inp.set_use_accumulated_input(True)

# Flush buffered events
inp.flush_buffered_events()

# Enable agile flushing (flushes immediately but accumulates for querying)
inp.set_agile_input_event_flushing(True)
```

### Custom Controller Mappings

```python
# Add SDL-style mapping
mapping = "030000005e0400008e02000000007200,Xbox 360 Controller,a:b0,b:b1,x:b2,y:b3"
inp.add_joy_mapping(mapping)

# Mappings are automatically applied when joypads connect
inp.joy_connection_changed(
    device=0,
    connected=True,
    name="My Controller",
    guid="030000005e0400008e02000000007200"
)
```

## Godot C++ to Python Mapping

### Class Names

| Godot C++ | Python |
|-----------|--------|
| `Input` | `Input` |
| `InputMap` | `InputMap` |
| `InputEvent` | `InputEvent` |
| `InputEventKey` | `InputEventKey` |
| `InputEventMouseButton` | `InputEventMouseButton` |
| `InputEventMouseMotion` | `InputEventMouseMotion` |
| `InputEventScreenTouch` | `InputEventScreenTouch` |
| `InputEventScreenDrag` | `InputEventScreenDrag` |
| `InputEventJoypadButton` | `InputEventJoypadButton` |
| `InputEventJoypadMotion` | `InputEventJoypadMotion` |
| `JoyButton` | `JoyButton` (Enum) |
| `JoyAxis` | `JoyAxis` (Enum) |
| `Key` | `Key` (Enum) |
| `MouseButton` | `MouseButton` (Enum) |

### Method Mapping

| Godot C++ | Python |
|-----------|--------|
| `Input::get_singleton()` | `Input.get_singleton()` |
| `Input::is_action_pressed()` | `Input.is_action_pressed()` |
| `Input::is_action_just_pressed()` | `Input.is_action_just_pressed()` |
| `Input::is_key_pressed()` | `Input.is_key_pressed()` |
| `Input::is_mouse_button_pressed()` | `Input.is_mouse_button_pressed()` |
| `Input::get_vector()` | `Input.get_vector()` |
| `Input::get_axis()` | `Input.get_axis()` |
| `Input::get_action_strength()` | `Input.get_action_strength()` |
| `Input::parse_input_event()` | `Input.parse_input_event()` |
| `Input::set_mouse_mode()` | `Input.set_mouse_mode()` |
| `Input::warp_mouse()` | `Input.warp_mouse()` |
| `Input::start_joy_vibration()` | `Input.start_joy_vibration()` |

### Data Type Mapping

| Godot C++ | Python |
|-----------|--------|
| `Vector2` | `Tuple[float, float]` |
| `Vector3` | `Tuple[float, float, float]` |
| `StringName` | `str` |
| `BitField<Enum>` | `int` (bitwise operations) |
| `HashMap` | `dict` |
| `List` | `list` |
| `Set` | `set` |
| `Ref<T>` | Direct reference |

## Platform Integration

The Input singleton uses function pointers for platform-specific operations:

```python
# Set platform functions
Input.set_mouse_mode_func = my_set_mouse_mode
Input.get_mouse_mode_func = my_get_mouse_mode
Input.warp_mouse_func = my_warp_mouse
Input.event_dispatch_function = my_event_handler
```

### PyQt6/PySide6 Integration Example

```python
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from engine.input.input_godot import Input

class InputHandler:
    def __init__(self):
        self.inp = Input.get_singleton()
        
    def handle_key_press(self, qt_key):
        """Convert Qt key to Godot Key and parse."""
        from engine.input.input_enums import Key
        from engine.input.input_events import InputEventKey
        
        godot_key = self._qt_to_godot_key(qt_key)
        
        event = InputEventKey(
            keycode=godot_key,
            physical_keycode=godot_key,
            pressed=True
        )
        self.inp.parse_input_event(event)
    
    def _qt_to_godot_key(self, qt_key):
        # Mapping Qt keys to Godot keys
        mapping = {
            Qt.Key.Key_Space: Key.SPACE,
            Qt.Key.Key_A: Key.A,
            # ... etc
        }
        return mapping.get(qt_key, Key.NONE)
```

## Thread Safety

All Input methods are thread-safe using Python's `threading.Lock`:

```python
import threading

class Input:
    _lock = threading.Lock()
    
    def is_key_pressed(self, keycode):
        with self._lock:
            return keycode in self.keys_pressed
```

## Event Accumulation

For performance, input events can be accumulated:

```python
# Enable accumulation
inp.set_use_accumulated_input(True)

# Events are buffered
for event in events:
    inp.parse_input_event(event)

# Flush at end of frame
inp.flush_buffered_events()
```

Motion events are automatically accumulated (relative movement combines).

## Default Actions

The system includes common game actions:

- `ui_left`, `ui_right`, `ui_up`, `ui_down` - UI navigation
- `ui_accept`, `ui_cancel`, `ui_select` - UI actions
- `move_left`, `move_right`, `move_up`, `move_down` - Movement
- `jump`, `fire`, `attack`, `interact` - Game actions
- `inventory`, `map`, `pause` - Menu actions

```python
# Load all defaults
inp_map.load_default_actions()

# Clear defaults but keep custom
inp_map.clear_default_actions()
```

## Testing

Run the test suite:

```bash
cd game_engine_studio
python -m pytest tests/test_input_godot.py -v
```

Run the demo:

```bash
cd game_engine_studio/examples
python godot_input_demo.py
```

## Comparison with Original Godot

### Godot C++ (Original)

```cpp
void _input(const Ref<InputEvent> &event) {
    if (event->is_action_pressed("jump")) {
        velocity.y = JUMP_FORCE;
    }
    
    Vector2 input_dir = Input::get_singleton()->get_vector(
        "move_left", "move_right", "move_up", "move_down"
    );
    velocity.x = input_dir.x * SPEED;
    velocity.z = input_dir.y * SPEED;
}
```

### Python Port

```python
def _input(self, event: InputEvent):
    if event.is_action_pressed("jump"):
        self.velocity.y = JUMP_FORCE
    
    input_dir = Input.get_singleton().get_vector(
        "move_left", "move_right", "move_up", "move_down"
    )
    self.velocity.x = input_dir[0] * SPEED
    self.velocity.z = input_dir[1] * SPEED
```

## Performance Notes

- Uses `__slots__` where possible for memory efficiency
- Thread-safe with minimal lock contention
- Event accumulation reduces processing overhead
- Dictionary lookups for action state are O(1)
- Joypad state uses combined int keys for efficient lookup

## License

This port maintains compatibility with Godot Engine's input system architecture while being implemented in Python for use with the Game Engine Studio.
