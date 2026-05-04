# Advanced Features Guide

Complete guide to new advanced features in Game Engine Studio.

## Table of Contents

1. [GD Language](#gd-language)
2. [Database & Save System](#database--save-system)
3. [Encryption & Security](#encryption--security)
4. [Dialogue Manager](#dialogue-manager)
5. [Kanban Board](#kanban-board)
6. [Export & Build System](#export--build-system)
7. [Pixel Scaling](#pixel-scaling)
8. [Debug & Diagnostics](#debug--diagnostics)

---

## GD Language

### Type-Safe Arrays

GDArray provides type-safe dynamic arrays with methods similar to Godot:

```python
from engine.gd_lang import GDArray, Type

# Create typed array
health_values = GDArray(element_type=Type.INT)

# Add items
health_values.append(100)
health_values.append(50)

# Array operations
health_values.insert(0, 150)
health_values.remove(50)
health_values.reverse()
health_values.sort()

# Access
size = health_values.size()  # 2
value = health_values.get(0)  # 150
index = health_values.find(100)  # 1

# Serialization
json_str = health_values.to_json()
```

### Type-Safe Dictionaries

GDDictionary provides key-value storage with type enforcement:

```python
from engine.gd_lang import GDDictionary, Type

# Create dictionary with value type checking
player_stats = GDDictionary(value_type=Type.INT)

player_stats.set("health", 100)
player_stats.set("mana", 50)

health = player_stats.get("health")  # 100
player_stats.update({"strength": 15})
```

### Built-in Functions

GD Language includes math, string, and type functions:

```python
from engine.gd_lang import setup_builtins

# Setup in globals
globals_dict = {}
setup_builtins(globals_dict)

# Now available: print, debug, typeof, int, float, str, bool
# Math: sin, cos, sqrt, pow, clamp, lerp, min, max
# Arrays: Array, range, len
# More...
```

---

## Database & Save System

### Save Game State

```python
from engine.database import SaveManager
from engine.diagnostics import EventLogger

save_manager = SaveManager("./my_project")

# Create save data
game_state = {
    'player': {'health': 100, 'position': [50, 100]},
    'enemies': [
        {'id': 1, 'health': 30},
        {'id': 2, 'health': 45}
    ],
    'playtime': 3600
}

# Save encrypted
save_manager.save_game(
    slot=1,
    game_state=game_state,
    metadata=None,
    encrypt=True
)

# Later: Load game
loaded_state, metadata = save_manager.load_game(1)
print(f"Playtime: {metadata.playtime}s")
```

### Multiple Save Slots

```python
# Create auto-save
auto_slot = save_manager.auto_save(game_state)

# List all saves
all_saves = save_manager.get_all_saves()
for save_meta in all_saves:
    print(f"Slot {save_meta.slot}: {save_meta.name}")

# Check if slot used
if save_manager.is_save_slot_used(2):
    print("Slot 2 has a save")

# Delete save
save_manager.delete_save(1)
```

### SQL Database Access

```python
from engine.database import DatabaseManager

db = DatabaseManager("./my_project")

# Execute queries
db.execute("INSERT INTO save_slots (slot_number, save_data) VALUES (?, ?)",
          (1, b'saved_data'))

# Fetch data
save = db.fetch_one("SELECT * FROM save_slots WHERE slot_number = ?", (1,))
all_saves = db.fetch_all("SELECT * FROM save_slots")

# Transactions
with db.transaction() as conn:
    db.insert('save_slots', {'slot_number': 2, 'save_data': b'...'})
    # Auto-commit on success
```

---

## Encryption & Security

### Encrypt Save Files

```python
from engine.security import CryptoManager, KeyManager

# Setup encryption
key_manager = KeyManager("./my_project")
key_manager.create_master_key(password="my_password")

crypto = CryptoManager()
key = key_manager.generate_save_key(slot=1)

# Encrypt data
plaintext = b"sensitive game data"
ciphertext, iv, hmac_tag = crypto.encrypt(plaintext, key)

# Later: Decrypt
decrypted = crypto.decrypt(ciphertext, key, iv, hmac_tag)
assert decrypted == plaintext
```

### Encrypted File Format

```python
from engine.io.encrypted_format import EncryptedFormat

encrypted_io = EncryptedFormat("./my_project")

# Save encrypted
save_data = {'player': {'health': 100}}
encrypted_io.save(save_data, slot=1, encrypt=True)

# Load encrypted
loaded = encrypted_io.load(slot=1, decrypt=True)
```

---

## Dialogue Manager

### Create Dialogue Tree

```python
from engine.dialogue import DialogueManager, DialogueNode, DialogueType, DialogueChoice

dialogue_mgr = DialogueManager("./my_project")

# Create dialogue
dialogue = dialogue_mgr.create_dialogue("intro", "Introduction")

# Create nodes
start = DialogueNode(
    id="start",
    type=DialogueType.START,
    character="Narrator",
    text="Welcome, traveler!"
)

choice_node = DialogueNode(
    id="choice1",
    type=DialogueType.CHOICE,
    character="You",
    text="What do you want from me?"
)

# Add choices with conditions
choice_node.add_choice(DialogueChoice(
    id="choice_yes",
    text="I will help you",
    next_node_id="end_good",
    flag_set={"helped_merchant": True}
))

choice_node.add_choice(DialogueChoice(
    id="choice_no",
    text="I refuse",
    next_node_id="end_bad",
    condition="gold > 100"  # Only if player has gold
))

dialogue.add_node(start)
dialogue.add_node(choice_node)

dialogue_mgr.save_dialogue("intro")
```

### Play Dialogue

```python
# Start dialogue
current_node = dialogue_mgr.start_dialogue("intro")
print(f"{current_node.character}: {current_node.text}")

# Get available choices
choices = dialogue_mgr.get_current_choices()
for choice in choices:
    print(f"  [{choice.id}] {choice.text}")

# Make choice
next_node = dialogue_mgr.advance_dialogue(choice_id="choice_yes")

# Continue...
while next_node and next_node.type != DialogueType.END:
    next_node = dialogue_mgr.advance_dialogue()
```

---

## Kanban Board

### Create Project Board

```python
from engine.editor import KanbanBoard, Task, TaskStatus, TaskPriority

# Create board
board = KanbanBoard("Development")

# Create tasks
board.create_task(
    "feat_1",
    "Implement player movement",
    description="Add WASD movement controls",
    priority=TaskPriority.HIGH
)

# Move task
board.move_task("feat_1", TaskStatus.IN_PROGRESS)

# Get tasks by status
todo_tasks = board.get_tasks_by_status(TaskStatus.TODO)
in_progress = board.get_tasks_by_status(TaskStatus.IN_PROGRESS)

# Add comments
board.add_comment("feat_1", "dev_user", "Started implementation")

# Board stats
stats = board.get_board_stats()
print(f"Completion: {stats['completion_rate']:.1f}%")
```

### Multi-Board Management

```python
from engine.editor.kanban import KanbanBoardManager

board_mgr = KanbanBoardManager("./my_project")

# Create multiple boards
dev_board = board_mgr.create_board("development", "Development Tasks")
art_board = board_mgr.create_board("art", "Art Assets")

# Save all
board_mgr.save_all_boards()

# Load later
dev_board = board_mgr.get_board("development")
```

---

## Export & Build System

### Export Project

```python
from engine.build import ExportManager, ExportConfig, Platform

exporter = ExportManager("./my_project")

# Export for specific platform
config = ExportConfig(
    project_path="./my_project",
    export_path="./exports",
    platform=Platform.WINDOWS,
    optimize=True,
    compress=True,
    version="1.0.0"
)

success = exporter.export(config)

if success:
    print(exporter.get_build_log())
```

### Bundle Creation

```python
from engine.build import BundleBuilder

bundler = BundleBuilder("./my_project", "./bundles")

# Create full bundle
bundle_path = bundler.build_bundle("game_v1.0")

# Get stats
stats = bundler.get_bundle_stats(bundle_path)
print(f"Bundle size: {stats['total_size_mb']:.2f} MB")
```

### Asset Analysis

```python
from engine.build import AssetPackager

packager = AssetPackager("./my_project")

# Find unused assets
unused = packager.find_unused_assets()
for asset in unused:
    print(f"Unused: {asset}")

# Get largest assets
largest = packager.get_largest_assets(limit=10)
for asset, size, type_ in largest:
    print(f"{asset.name}: {size / 1024 / 1024:.2f} MB ({type_})")
```

---

## Pixel Scaling

### Scale Pixel Art

```python
from engine.rendering.scaling import PixelScaler, ScaleFilter
from PIL import Image

scaler = PixelScaler(ScaleFilter.EPX)

# Load pixel art
image = Image.open("sprite.png")

# Scale 2x using EPX
scaled = scaler.scale(image, scale_factor=2)
scaled.save("sprite_2x.png")
```

### Multiple Algorithms

```python
from engine.rendering.scaling.filters import NearestNeighbor, Linear, EPX, XBR

# Different filters for different purposes
nn = NearestNeighbor()
linear = Linear()
epx = EPX()
xbr = XBR()

# Scale with each
scaled_nn = nn.apply(image, 4)
scaled_linear = linear.apply(image, 4)
scaled_epx = epx.apply(image, 4)
scaled_xbr = xbr.apply(image, 4)
```

---

## Debug & Diagnostics

### Project Validation

```python
from engine.debug import GlobalDebugger, BuildValidator

# Debug entire project
debugger = GlobalDebugger("./my_project")
report = debugger.debug_project()

# Print results
report.print_details()

# Check for build errors
if report.has_errors():
    print("Project has errors!")
```

### Pre-Build Validation

```python
# Validate before building
validator = BuildValidator("./my_project")
can_build, report = validator.validate_for_build()

if not can_build:
    blockers = validator.get_build_blockers()
    for blocker in blockers:
        print(f"Blocker: {blocker}")
```

### Project Analysis

```python
from engine.debug import ProjectScanner

scanner = ProjectScanner("./my_project")

# Get statistics
stats = scanner.get_statistics()
print(f"Total Files: {stats['total_files']}")
print(f"Total Size: {stats['total_size_mb']:.2f} MB")

# Find issues
broken_refs = scanner.find_broken_references()
duplicates = scanner.find_duplicate_files()
large_files = scanner.find_large_files(min_size_mb=5.0)

print(scanner.get_file_report())
```

### Performance Monitoring

```python
from engine.diagnostics import PerformanceMetrics, TelemetryTree, EventType

# Track performance
metrics = PerformanceMetrics(max_history=300)

# Each frame
frame_metrics = metrics.record_frame(active_entities=50, draw_calls=100)

# Get stats
print(f"Average FPS: {metrics.get_average_fps():.1f}")
print(f"Peak Memory: {metrics.get_peak_memory():.1f} MB")

# Detect issues
if metrics.detect_memory_leaks():
    print("Potential memory leak detected!")

stutters = metrics.detect_stutters()
```

### Event Logging

```python
from engine.diagnostics import TelemetryTree, EventType

# Create telemetry tree
telemetry = TelemetryTree("Game Session")

# Log events
telemetry.push_event("scene_load", EventType.SCENE_LOAD)
# ... do work ...
telemetry.pop_event(duration=45.5)

# Print statistics
telemetry.print_tree()
print(telemetry.get_stats())
```

---

## Integration Example

Complete example using multiple systems:

```python
from engine.project import ProjectManager
from engine.database import SaveManager
from engine.dialogue import DialogueManager
from engine.debug import BuildValidator

# Create project
project_mgr = ProjectManager()
project = project_mgr.create_project("MyGame", "./projects")

# Setup game systems
save_mgr = SaveManager(str(project.path))
dialogue_mgr = DialogueManager(str(project.path))

# Create initial save
initial_state = {'level': 1, 'health': 100}
save_mgr.save_game(1, initial_state, encrypt=True)

# Create dialogue
dialogue = dialogue_mgr.create_dialogue("intro", "Game Start")
# ... add nodes ...
dialogue_mgr.save_dialogue("intro")

# Validate before building
validator = BuildValidator(str(project.path))
can_build, report = validator.validate_for_build()

if can_build:
    print("Ready to export!")
else:
    print("Fix errors before exporting")
```

---

## Best Practices

1. **Always validate before building** - Use BuildValidator
2. **Use encryption for sensitive saves** - Protect player data
3. **Monitor performance** - Use PerformanceMetrics
4. **Test dialogues thoroughly** - Check all branches
5. **Organize with Kanban** - Track development progress
6. **Profile large projects** - Use ProjectScanner
7. **Use appropriate scaling** - EPX for pixel art, Linear for photos

---

**For more information, see API_REFERENCE.md**
