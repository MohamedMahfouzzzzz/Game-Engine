# Game Engine API Reference

## Core Model (`engine.tools.pixel_art_editor.core`)

### Document
Main project container for pixel art documents.

```python
from engine.tools.pixel_art_editor.core import Document

# Create document
doc = Document(64, 64, 'MySprite')
doc.author = 'Your Name'
doc.description = 'A pixel art character'

# Add layers
layer = doc.sprite.add_layer('Character')
layer2 = doc.sprite.add_layer('Background', is_background=True)

# Add frames
doc.sprite.add_frame(100)  # 100ms duration
```

### ImageBuffer
Low-level pixel data storage.

```python
from engine.tools.pixel_art_editor.core import ImageBuffer, ColorMode

# Create buffer
img = ImageBuffer(64, 64, ColorMode.RGBA)

# Pixel operations
img.set_pixel(10, 10, (255, 0, 0, 255))
color = img.get_pixel(10, 10)

# Bulk operations
img.clear((0, 0, 0, 0))
copy = img.copy()
```

### Brush
Brush for painting operations.

```python
from engine.tools.pixel_art_editor.core import Brush

# Create brushes
brush = Brush.circle(8, 'Circle8')
brush2 = Brush.square(4, 'Square4')
brush3 = Brush.rectangle(8, 4, 'Rect8x4')

# Apply pressure
brush.set_pressure(0.5)
```

## Binary Format (`engine.io`)

### Save/Load

```python
from engine.io import BinaryFormat

# Save document
BinaryFormat.save(doc, 'sprite.ges')

# Load document
loaded = BinaryFormat.load('sprite.ges')

# Get file info without loading
info = BinaryFormat.get_info('sprite.ges')
print(f"Size: {info['width']}x{info['height']}")
print(f"Layers: {info['layers']}, Frames: {info['frames']}")
```

## Commands (`engine.core.commands`)

### Command Pattern

```python
from engine.core.commands import Command, CommandResult, CommandHistory

class PaintCommand(Command):
    def __init__(self, layer, x, y, color):
        super().__init__('Paint')
        self.layer = layer
        self.x = x
        self.y = y
        self.color = color
        self._old_color = None
    
    def execute(self):
        self._old_color = self.layer.get_pixel(self.x, self.y)
        self.layer.set_pixel(self.x, self.y, self.color)
        self._mark_executed()
        return CommandResult.SUCCESS
    
    def undo(self):
        self.layer.set_pixel(self.x, self.y, self._old_color)
        self._mark_undone()
        return CommandResult.SUCCESS

# Use history
history = CommandHistory()
cmd = PaintCommand(layer, 5, 5, (255, 0, 0, 255))
history.execute(cmd)

# Undo/redo
history.undo()
history.redo()
```

### Transactions

```python
from engine.core.commands import Transaction

# Batch operations
with Transaction(history, 'Batch Paint'):
    for x, y in points:
        cmd = PaintCommand(layer, x, y, color)
        history.execute(cmd)
# Undoes as a single group
```

## Brushes (`engine.tools.pixel_art_editor.brushes`)

### Brush Manager

```python
from engine.tools.pixel_art_editor.brushes import BrushManager, BrushPresets

# Setup
manager = BrushManager()
BrushPresets.register_all_to_manager(manager)

# Get brushes
brush = manager.get_brush('Pencil')
all_brushes = manager.get_all_brushes()
```

### Pressure Curves

```python
from engine.tools.pixel_art_editor.brushes import PressureCurve

# Curves
linear = PressureCurve.linear()
quad = PressureCurve.quadratic()
s_curve = PressureCurve.s_curve()

# Map pressure
opacity = s_curve.map(0.5)  # Returns 0.0-1.0
```

### Brush Dynamics

```python
from engine.tools.pixel_art_editor.brushes.pressure_curve import BrushDynamics

dynamics = BrushDynamics()
dynamics.size_enabled = True
dynamics.opacity_enabled = True
dynamics.min_size = 1.0
dynamics.max_size = 20.0

# Apply to brush
brush = Brush.circle(10)
dynamics.apply(brush, pressure=0.5)
```

## Algorithms (`engine.tools.pixel_art_editor.algorithms`)

### Line Drawing

```python
from engine.tools.pixel_art_editor.algorithms import line_points

# Bresenham line
points = line_points(0, 0, 100, 50)
for x, y in points:
    layer.set_pixel(x, y, color)
```

### Shapes

```python
from engine.tools.pixel_art_editor.algorithms import rectangle, ellipse

# Rectangle (outline or filled)
rectangle(x1, y1, x2, y2, set_pixel_func, filled=False)

# Ellipse
ellipse(cx, cy, rx, ry, set_pixel_func)
```

### Flood Fill

```python
from engine.tools.pixel_art_editor.algorithms import flood_fill_simple

filled_count = flood_fill_simple(
    x, y,
    lambda x, y: layer.get_pixel(x, y),
    lambda x, y, c: layer.set_pixel(x, y, c),
    match_color=(255, 255, 255, 255),
    fill_color=(255, 0, 0, 255),
    bounds=(0, 0, width, height)
)
```

### Dithering

```python
from engine.tools.pixel_art_editor.algorithms import apply_dither, DitherPattern

# Check if pixel should be drawn based on dither pattern
if apply_dither(x, y, opacity, DitherPattern.CHECKERBOARD):
    layer.set_pixel(x, y, color)
```

### Color Operations

```python
from engine.tools.pixel_art_editor.algorithms import (
    quantize_colors, desaturate, create_outline
)

# Quantize palette
unique_colors = quantize_colors(all_colors, max_colors=32)

# Desaturate
gray = desaturate((255, 128, 0, 255), factor=1.0)

# Generate outline
outline = create_outline(pixels, outline_color, width=1)
```

## Signals (`engine.signals`)

### Basic Usage

```python
from engine.signals import Signal

class Button:
    clicked = Signal()  # No args
    
    def on_press(self):
        self.clicked.emit()

class Slider:
    value_changed = Signal(float)  # One arg
    
    def set_value(self, v):
        self.value_changed.emit(v)

# Connect
button = Button()
button.clicked.connect(on_click)

slider = Slider()
slider.value_changed.connect(lambda v: print(f'Value: {v}'))
```

### Advanced Features

```python
# One-shot connection
sig.connect(callback, one_shot=True)

# Priority (higher = called first)
sig.connect(low_priority, priority=0)
sig.connect(high_priority, priority=10)

# Block/unblock
conn = sig.connect(handler)
conn.block()
conn.unblock()

# Disconnect
conn.disconnect()
```

### Signal Manager

```python
from engine.signals import SignalManager

manager = SignalManager()

# Global signals
manager.add_signal('game_started', Signal())
manager.connect('game_started', on_game_start)
manager.emit('game_started')

# Signal groups
ui = manager.create_group('ui')
ui.add_signal('button_clicked', Signal(str))
manager.connect('ui.button_clicked', on_button)
manager.emit('ui.button_clicked', 'submit_btn')
```

## Threading (`engine.threading`)

### ThreadPool

```python
from engine.threading import ThreadPool

# Create pool
pool = ThreadPool(max_workers=4)

# Submit work
def process_image(data):
    # Heavy computation
    return result

future = pool.submit(process_image, data)
result = future.result()  # Wait for completion

# Multiple tasks
futures = [pool.submit(process_image, d) for d in data_list]
results = [f.result() for f in futures]

# Context manager
with ThreadPool(max_workers=4) as pool:
    future = pool.submit(task)

pool.shutdown()
```

### Futures

```python
from engine.threading import Future

# Get result with timeout
result = future.result(timeout=10)

# Check status
if future.done():
    result = future.result()

# Callbacks
future.add_callback(lambda f: print(f"Done: {f.result()}"))
future.add_done_callback(lambda f: print("Complete"))
```

## Tablet Input (`engine.input`)

```python
from engine.input import TabletInputManager, TabletDevice, TabletEvent
from engine.input.tablet import TabletDeviceType

# Setup
manager = TabletInputManager()

device = TabletDevice(1, 'Wacom Intuos', TabletDeviceType.STYLUS)
device.supports_pressure = True
device.supports_tilt = True
manager.register_device(device)

# Handle events
class MyHandler:
    def handle_event(self, event):
        print(f"Pressure: {event.pressure}")
        print(f"Tilt: {event.tilt_x}, {event.tilt_y}")
        print(f"Position: {event.x}, {event.y}")

manager.add_handler(MyHandler())

# Configure
manager.set_pressure_threshold(0.1)  # Ignore light touches
manager.set_smoothing(True, factor=0.3)  # Smooth movement
```

## Headless Mode (`engine.headless`)

### CLI Operations

```python
from engine.headless import HeadlessEngine

# Initialize
engine = HeadlessEngine()
engine.initialize()

# Load and export
doc = engine.load_project('input.ges')
engine.export('output.png', format='PNG')

# Batch processing
engine.set_progress_callback(lambda p, msg: print(f"{p*100:.0f}%: {msg}"))

# Validate
result = engine.validate('project.ges')
if result.success:
    print(f"Valid: {result.data}")

engine.shutdown()
```

### Batch Processing

```python
from engine.headless import HeadlessEngine, BatchProcessor

engine = HeadlessEngine()
engine.initialize()

processor = BatchProcessor(engine)

# Process directory
results = processor.process_directory(
    input_dir='./assets',
    output_dir='./exports',
    input_pattern='*.ges',
    output_format='PNG'
)

# Stats
stats = processor.get_stats(results)
print(f"Success: {stats['success']}/{stats['total']}")

engine.shutdown()
```

## CLI Usage

```bash
# Convert file
python -m engine.headless convert input.ges output.png --format PNG

# Validate
python -m engine.headless validate project.ges

# Batch process
python -m engine.headless batch -i ./assets -o ./exports -f PNG --recursive

# Show file info
python -m engine.headless info project.ges
```
