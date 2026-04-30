# Game Engine Studio Tutorial

## Table of Contents

1. [Getting Started](#getting-started)
2. [Pixel Art Editor Basics](#pixel-art-editor-basics)
3. [Working with Documents](#working-with-documents)
4. [Drawing and Painting](#drawing-and-painting)
5. [Animation](#animation)
6. [Using Signals](#using-signals)
7. [Threading and Async Operations](#threading-and-async-operations)
8. [Headless Mode](#headless-mode)
9. [Advanced Topics](#advanced-topics)

## Getting Started

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/game_engine_studio.git
cd game_engine_studio
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Verify installation:
```bash
python -c "from engine.tools.pixel_art_editor.core import Document; print('Success!')"
```

### Your First Pixel Art

Let's create a simple 32x32 pixel smiley face:

```python
from engine.tools.pixel_art_editor.core import Document
from engine.io import BinaryFormat

# Create a new document
doc = Document(32, 32, 'Smiley')
layer = doc.sprite.layers[0]  # Get default layer

# Draw the face (yellow circle)
def draw_circle(center_x, center_y, radius, color):
    for y in range(32):
        for x in range(32):
            dx = x - center_x
            dy = y - center_y
            if dx*dx + dy*dy <= radius*radius:
                layer.set_pixel(x, y, color)

draw_circle(16, 16, 12, (255, 255, 0, 255))  # Yellow face

# Draw eyes
layer.set_pixel(10, 12, (0, 0, 0, 255))
layer.set_pixel(22, 12, (0, 0, 0, 255))

# Draw smile
for x in range(10, 23):
    y = 20 + int(((x-16)*(x-16)) / 25)
    layer.set_pixel(x, y, (0, 0, 0, 255))

# Save the result
BinaryFormat.save(doc, 'smiley.ges')
print("Smiley face saved to smiley.ges")
```

## Pixel Art Editor Basics

### Understanding the Document Model

The pixel art editor uses a layered model similar to professional graphics software:

```
Document
├── Sprite (the actual image)
│   ├── Layers (stacked drawing surfaces)
│   │   ├── Layer 0 (background)
│   │   ├── Layer 1 (main drawing)
│   │   └── Layer 2 (effects)
│   ├── Frames (for animation)
│   │   ├── Frame 0 (100ms)
│   │   ├── Frame 1 (100ms)
│   │   └── Frame 2 (200ms)
│   └── Tags (frame groups for animation)
│       ├── "Walk" (frames 0-3, loop)
│       └── "Jump" (frames 4-6, ping-pong)
└── Metadata (author, description, etc.)
```

### Creating and Managing Layers

```python
from engine.tools.pixel_art_editor.core import Document, Layer, BlendMode

doc = Document(64, 64, 'Character')

# Add layers with different properties
background = doc.sprite.add_layer('Background')
background.is_background = True
background.locked = True

main_layer = doc.sprite.add_layer('Character')
main_layer.opacity = 255
main_layer.blend_mode = BlendMode.NORMAL

effects_layer = doc.sprite.add_layer('Effects')
effects_layer.opacity = 128  # Semi-transparent
effects_layer.blend_mode = BlendMode.ADD

# Layer operations
main_layer.move_up()    # Move up in stack
main_layer.move_down()  # Move down in stack
main_layer.duplicate()  # Create copy

# Hide/show layers
effects_layer.is_visible = False
```

## Working with Documents

### Loading and Saving

```python
from engine.io import BinaryFormat

# Save document
success = BinaryFormat.save(doc, 'character.ges')
if success:
    print("Document saved successfully")

# Load document
loaded_doc = BinaryFormat.load('character.ges')
if loaded_doc:
    print(f"Loaded: {loaded_doc.name}")
    print(f"Size: {loaded_doc.width}x{loaded_doc.height}")
    print(f"Layers: {loaded_doc.sprite.layer_count}")

# Get file info without loading
info = BinaryFormat.get_info('character.ges')
print(f"Version: {info['version']}")
print(f"Created: {info['created']}")
```

### Document Properties

```python
# Metadata
doc.author = "Artist Name"
doc.description = "Main character sprite"
doc.license = "CC-BY-SA 4.0"

# Color mode
from engine.tools.pixel_art_editor.core import ColorMode
doc.sprite.color_mode = ColorMode.RGBA  # Full color
# doc.sprite.color_mode = ColorMode.INDEXED  # Palette-based
# doc.sprite.color_mode = ColorMode.GRAYSCALE  # Black and white

# Palette (for indexed mode)
if doc.sprite.color_mode == ColorMode.INDEXED:
    from engine.tools.pixel_art_editor.core import Palette
    palette = Palette()
    palette.add_color((255, 0, 0, 255))    # Red
    palette.add_color((0, 255, 0, 255))    # Green
    palette.add_color((0, 0, 255, 255))    # Blue
    doc.sprite.palette = palette
```

## Drawing and Painting

### Using the Brush System

```python
from engine.tools.pixel_art_editor.brushes import BrushManager, BrushPresets
from engine.tools.pixel_art_editor.brushes.pressure_curve import PressureCurve

# Setup brush manager
manager = BrushManager()
BrushPresets.register_all_to_manager(manager)

# Get a brush
brush = manager.get_brush('Pencil')
brush.size = 2

# Apply brush with pressure (simulating tablet)
pressure = 0.5  # 0.0 to 1.0
brush.set_pressure(pressure)

# Draw a line
def draw_line(layer, x1, y1, x2, y2, brush):
    from engine.tools.pixel_art_editor.algorithms import line_points
    
    for x, y in line_points(x1, y1, x2, y2):
        color = (255, 0, 0, int(255 * pressure))
        layer.set_pixel(x, y, color)

draw_layer = doc.sprite.get_layer('Character')
draw_line(draw_layer, 10, 10, 50, 30, brush)
```

### Custom Brushes

```python
from engine.tools.pixel_art_editor.core import Brush, BrushType

# Create custom brush
custom_brush = Brush.rectangle(8, 4, 'Custom Rect')

# Create brush from image
from PIL import Image
img = Image.open('brush_pattern.png')
image_brush = Brush.from_image(img, 'Image Brush')

# Apply brush dynamics
from engine.tools.pixel_art_editor.brushes.pressure_curve import BrushDynamics

dynamics = BrushDynamics()
dynamics.size_enabled = True
dynamics.opacity_enabled = True
dynamics.min_size = 1.0
dynamics.max_size = brush.size

# Apply with varying pressure
for pressure in [0.2, 0.5, 0.8, 1.0]:
    temp_brush = brush.copy()
    dynamics.apply(temp_brush, pressure)
    # Use temp_brush for drawing
```

### Flood Fill

```python
from engine.tools.pixel_art_editor.algorithms import flood_fill_simple

# Fill an area
filled = flood_fill_simple(
    x=20, y=20,
    get_pixel=lambda x, y: layer.get_pixel(x, y),
    set_pixel=lambda x, y, c: layer.set_pixel(x, y, c),
    match_color=(255, 255, 255, 255),  # White
    fill_color=(255, 0, 0, 255),        # Red
    bounds=(0, 0, layer.width, layer.height)
)

print(f"Filled {filled} pixels")
```

## Animation

### Creating Animations

```python
# Add frames for animation
doc.sprite.add_frame(100)  # Frame 1, 100ms duration
doc.sprite.add_frame(100)  # Frame 2, 100ms duration
doc.sprite.add_frame(200)  # Frame 3, 200ms duration

# Draw on different frames
for frame_idx, frame in enumerate(doc.sprite.frames):
    # Get layer for this frame
    layer = doc.sprite.get_layer(0, frame_idx)
    
    # Draw animation frame
    x = 10 + frame_idx * 5
    layer.set_pixel(x, 20, (255, 0, 0, 255))

# Create animation tags
from engine.tools.pixel_art_editor.core import Tag, TagRepeat

walk_tag = Tag('Walk', 0, 2, (255, 0, 0), TagRepeat.LOOP)
doc.sprite.add_tag(walk_tag)

jump_tag = Tag('Jump', 3, 5, (0, 255, 0), TagRepeat.PING_PONG)
doc.sprite.add_tag(jump_tag)
```

### Playing Animation

```python
# Simple animation player
import time

def play_animation(doc, tag_name, fps=10):
    tag = doc.sprite.get_tag(tag_name)
    if not tag:
        return
    
    frame_indices = list(range(tag.from_frame, tag.to_frame + 1))
    if tag.repeat == TagRepeat.PING_PONG:
        frame_indices += frame_indices[-2:0:-1]
    
    while True:
        for frame_idx in frame_indices:
            # Display frame (in real app, you'd render to screen)
            print(f"Showing frame {frame_idx}")
            time.sleep(1.0 / fps)

# play_animation(doc, 'Walk')
```

## Using Signals

### Basic Signal Usage

```python
from engine.signals import Signal

class Button:
    def __init__(self, name):
        self.name = name
        self.clicked = Signal()  # Signal for click events
        self.hovered = Signal(str)  # Signal with data
    
    def on_click(self):
        print(f"Button {self.name} clicked!")
        self.clicked.emit()
    
    def on_hover(self):
        print(f"Button {self.name} hovered!")
        self.hovered.emit(self.name)

# Connect handlers
def on_button_click():
    print("Button was clicked!")

def on_button_hover(button_name):
    print(f"Hovering over: {button_name}")

button = Button('OK')
button.clicked.connect(on_button_click)
button.hovered.connect(on_button_hover)

# Trigger events
button.on_click()
button.on_hover()
```

### Advanced Signal Features

```python
# Priority handling
def high_priority_handler():
    print("High priority")

def low_priority_handler():
    print("Low priority")

signal = Signal()
signal.connect(low_priority_handler, priority=0)
signal.connect(high_priority_handler, priority=10)
signal.emit()  # High priority runs first

# One-shot connections
signal.connect(lambda: print("Once only"), one_shot=True)

# Blocking connections
conn = signal.connect(lambda: print("Can be blocked"))
conn.block()
signal.emit()  # Handler won't run
conn.unblock()
signal.emit()  # Handler runs again
```

### Signal Manager

```python
from engine.signals import SignalManager

manager = SignalManager()

# Add global signals
manager.add_signal('player_died', Signal())
manager.add_signal('level_completed', Signal(str))

# Create groups
ui_group = manager.create_group('ui')
ui_group.add_signal('button_clicked', Signal(str))

game_group = manager.create_group('game')
game_group.add_signal('enemy_spawned', Signal(str, int, int))

# Connect handlers
def on_player_died():
    print("Game over!")

def on_level_complete(level_name):
    print(f"Completed: {level_name}")

manager.connect('player_died', on_player_died)
manager.connect('level_completed', on_level_complete)

# Emit signals
manager.emit('player_died')
manager.emit('level_completed', 'Level 1')
```

## Threading and Async Operations

### Using ThreadPool

```python
from engine.threading import ThreadPool

# Create thread pool
pool = ThreadPool(max_workers=4)

# Define CPU-intensive task
def process_image_chunk(chunk_data):
    """Process a chunk of image data"""
    result = []
    for pixel in chunk_data:
        # Simulate heavy processing
        processed = apply_filter(pixel)
        result.append(processed)
    return result

# Submit tasks
image_chunks = split_image_into_chunks(large_image)
futures = []

for chunk in image_chunks:
    future = pool.submit(process_image_chunk, chunk)
    futures.append(future)

# Collect results
processed_chunks = []
for future in futures:
    result = future.result(timeout=30)  # Wait up to 30 seconds
    processed_chunks.append(result)

# Combine results
final_image = combine_chunks(processed_chunks)

pool.shutdown()
```

### Async File Operations

```python
from engine.threading import ThreadPool

def save_documents_async(docs, output_dir):
    """Save multiple documents in parallel"""
    pool = ThreadPool(max_workers=4)
    
    def save_single(doc, path):
        from engine.io import BinaryFormat
        return BinaryFormat.save(doc, path)
    
    futures = []
    for i, doc in enumerate(docs):
        path = f"{output_dir}/doc_{i}.ges"
        future = pool.submit(save_single, doc, path)
        futures.append(future)
    
    # Wait for all to complete
    results = []
    for future in futures:
        try:
            success = future.result()
            results.append(success)
        except Exception as e:
            print(f"Error saving document: {e}")
            results.append(False)
    
    pool.shutdown()
    return results
```

## Headless Mode

### CLI Operations

```python
from engine.headless import HeadlessEngine

# Initialize headless engine
engine = HeadlessEngine()
engine.initialize()

# Load and process documents
doc = engine.load_project('character.ges')
if doc:
    print(f"Loaded: {doc.name}")
    
    # Export to different formats
    engine.export('character.png', format='PNG')
    engine.export('character.gif', format='GIF')
    engine.export_sheet('character_sheet.png', columns=4, rows=4)

# Batch processing
def process_all(input_dir, output_dir):
    import os
    for filename in os.listdir(input_dir):
        if filename.endswith('.ges'):
            path = os.path.join(input_dir, filename)
            doc = engine.load_project(path)
            if doc:
                output_path = os.path.join(output_dir, filename.replace('.ges', '.png'))
                engine.export(output_path, format='PNG')

engine.shutdown()
```

### Command Line Interface

```bash
# Convert files
python -m engine.headless convert input.ges output.png --format PNG

# Batch convert directory
python -m engine.headless batch -i ./assets -o ./exports -f PNG

# Validate files
python -m engine.headless validate project.ges

# Show file information
python -m engine.headless info project.ges

# Export spritesheet
python -m engine.headless export-sheet character.ges -o sheet.png --cols 4 --rows 4
```

## Advanced Topics

### Custom Commands

```python
from engine.core.commands import Command, CommandResult, CommandHistory

class BlendColorsCommand(Command):
    """Blend two colors and apply to layer"""
    
    def __init__(self, layer, color1, color2, blend_mode):
        super().__init__('BlendColors')
        self.layer = layer
        self.color1 = color1
        self.color2 = color2
        self.blend_mode = blend_mode
        self._original_pixels = {}
    
    def execute(self):
        # Store original pixels for undo
        for y in range(self.layer.height):
            for x in range(self.layer.width):
                self._original_pixels[(x, y)] = self.layer.get_pixel(x, y)
        
        # Apply blend
        for y in range(self.layer.height):
            for x in range(self.layer.width):
                original = self._original_pixels[(x, y)]
                blended = blend_colors(original, self.color1, self.color2, self.blend_mode)
                self.layer.set_pixel(x, y, blended)
        
        self._mark_executed()
        return CommandResult.SUCCESS
    
    def undo(self):
        # Restore original pixels
        for (x, y), color in self._original_pixels.items():
            self.layer.set_pixel(x, y, color)
        
        self._mark_undone()
        return CommandResult.SUCCESS

# Use with command history
history = CommandHistory()
cmd = BlendColorsCommand(layer, (255, 0, 0), (0, 0, 255), 'multiply')
history.execute(cmd)

# Undo if needed
history.undo()
```

### Performance Optimization Tips

1. **Use bulk operations**:
```python
# Fast
layer.clear((255, 255, 255, 255))

# Slow
for y in range(layer.height):
    for x in range(layer.width):
        layer.set_pixel(x, y, (255, 255, 255, 255))
```

2. **Batch signal emissions**:
```python
# Fast - one emit with list
signal.emit([item1, item2, item3])

# Slow - multiple emits
signal.emit(item1)
signal.emit(item2)
signal.emit(item3)
```

3. **Use appropriate thread pool size**:
```python
import multiprocessing

# Use number of CPU cores
pool = ThreadPool(max_workers=multiprocessing.cpu_count())
```

### Error Handling

```python
from engine.io import BinaryFormat

# Always check return values
success = BinaryFormat.save(doc, 'output.ges')
if not success:
    print("Failed to save document")
    return

# Handle load errors
loaded = BinaryFormat.load('input.ges')
if loaded is None:
    print("Failed to load document")
    return

# Use try-catch for operations
try:
    doc = BinaryFormat.load('corrupted.ges')
except Exception as e:
    print(f"Error loading file: {e}")
```

---

## Next Steps

Now that you've completed the tutorial, you might want to:

1. Check out the [API Reference](API_REFERENCE.md) for detailed documentation
2. Look at the examples in the `examples/` directory
3. Read the [Contributing Guide](CONTRIBUTING.md) if you want to help develop
4. Join our Discord community for support and discussions

Happy pixel art creation! 🎨
