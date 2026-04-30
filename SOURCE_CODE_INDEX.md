# Game Engine Studio - Source Code Index

Complete index of all source files and their purposes.

## 📁 Engine Core (`engine/core/`)

### Entity System
- **entity.py** - Entity class for ECS, component attachment
- **component.py** - Base Component class and component registry
- **system.py** - System base class for processing entities
- **world.py** - ECS world managing entities, components, systems

### Scene Management
- **scene.py** - Scene class with hierarchical transforms
- **node.py** - Base Node class for scene graph
- **node2d.py** - 2D node with position, rotation, scale
- **node3d.py** - 3D node (placeholder for future)

### Core Systems
- **transform.py** - Transform component for position/rotation/scale
- **camera.py** - Camera system for viewport management
- **resource_manager.py** - Asset loading and caching system

## 📁 Rendering (`engine/rendering/`)

### Renderer
- **renderer2d.py** - 2D renderer with shader support, materials, lights
- **camera.py** - 2D camera with zoom, pan, viewport
- **engine.py** - Main rendering engine interface

### Graphics
- **light.py** - 2D lighting system with different light types
- **particles.py** - Particle system for effects
- **shadows.py** - Shadow rendering for 2D objects

### Shaders
- **shader_manager.py** - GLSL shader loading, compilation, hot-reload
- **material.py** - Material system for shader parameters

## 📁 Audio (`engine/audio/`)

- **audio_manager.py** - Main audio system, channel management
- **sound.py** - Sound loading and playback
- **music.py** - Music streaming and control
- **mixer.py** - Audio mixing and effects

## 📁 Physics (`engine/physics/`)

- **physics_world.py** - Box2D physics world wrapper
- **collision.py** - Collision detection and response
- **rigid_body.py** - Physics body component
- **shapes.py** - Collision shapes (box, circle, polygon)

## 📁 Input (`engine/input/`)

- **input_manager.py** - Centralized input handling
- **keyboard.py** - Keyboard input mapping
- **mouse.py** - Mouse input with buttons, wheel
- **gamepad.py** - Gamepad/controller support
- **tablet.py** - Graphics tablet pressure, tilt support

## 📁 Tools - Pixel Art Editor (`engine/tools/pixel_art_editor/`)

### Core Model
- **document.py** - Main document class with metadata
- **sprite.py** - Sprite container with layers, frames
- **layer.py** - Layer class with blend modes, opacity
- **cel.py** - Cel (frame layer) with image data
- **frame.py** - Frame with duration metadata
- **tag.py** - Animation tags for frame groups
- **image_buffer.py** - Pixel data storage with PIL backend
- **palette.py** - Color palette management
- **brush.py** - Brush definition and properties
- **color_mode.py** - Color modes (RGBA, indexed, grayscale)
- **blend_mode.py** - Blending modes for layers

### Algorithms
- **flood_fill.py** - Scanline flood fill algorithm
- **line_drawing.py** - Bresenham line, shapes drawing
- **dithering.py** - Dithering patterns and algorithms
- **color_ops.py** - Color quantization, outline generation

### Brushes
- **brush_manager.py** - Brush categories and preset management
- **brush_presets.py** - Pre-defined brush presets
- **pressure_curve.py** - Pressure sensitivity curves

## 📁 I/O (`engine/io/`)

- **binary_format.py** - Native .ges format (chunk-based, compressed)
- **chunk_types.py** - Chunk definitions for binary format
- **compression.py** - Zlib/Zstandard compression wrapper
- **image_io.py** - Image format import/export

## 📁 Signals (`engine/signals/`)

- **signal.py** - Signal class with connections, emission modes
- **slot.py** - Slot base, CallableSlot, MethodSlot
- **signal_manager.py** - Global signal management, groups

## 📁 Threading (`engine/threading/`)

- **thread_pool.py** - ThreadPool for async operations
- **task.py** - Task with priority, status, timeout
- **future.py** - Future for async result handling
- **worker.py** - Worker thread implementation

## 📁 Headless (`engine/headless/`)

- **headless_engine.py** - CLI engine without GUI
- **cli_interface.py** - Command-line interface
- **batch_processor.py** - Batch file operations

## 📁 UI (`engine/ui/`)

### Main Interface
- **main_window.py** - Main application window
- **menu_bar.py** - Application menu system
- **tool_bar.py** - Tool palette and shortcuts

### Editor Windows
- **pixel_art_editor.py** - Main pixel art editor UI
- **layer_panel.py** - Layer management panel
- **timeline_panel.py** - Animation timeline
- **color_panel.py** - Color picker and palettes
- **brush_panel.py** - Brush selection and settings

### Widgets
- **canvas.py** - Drawing canvas with zoom, pan
- **color_wheel.py** - Color selection widget
- **layer_item.py** - Layer list item widget
- **frame_thumb.py** - Frame thumbnail widget

## 📁 Examples (`examples/`)

- **pixel_art_character.py** - Create pixel art character
- **animation_demo.py** - Animated sprite examples
- **signal_system_demo.py** - Signal/slot usage examples
- **threading_demo.py** - Threading system examples
- **headless_batch_example.py** - CLI batch processing

## 📁 Tests (`tests/`)

### Unit Tests
- **test_core_model.py** - Core model classes tests
- **test_binary_format.py** - File I/O tests
- **test_brushes.py** - Brush system tests
- **test_algorithms.py** - Drawing algorithm tests
- **test_commands.py** - Command pattern tests
- **test_signals.py** - Signal system tests
- **test_threading.py** - Threading system tests

### Integration Tests
- **test_integration.py** - Cross-module integration tests

## 📁 Benchmarks (`benchmarks/`)

- **benchmark_suite.py** - Performance benchmarking system

## 📁 Configuration

- **pyproject.toml** - Project configuration
- **requirements.txt** - Runtime dependencies
- **requirements-dev.txt** - Development dependencies
- **setup.py** - Package setup script

## 📁 Documentation

- **README.md** - Main project documentation
- **API_REFERENCE.md** - Complete API reference
- **TUTORIAL.md** - Getting started tutorial
- **CONTRIBUTING.md** - Development guide

## 📁 CI/CD (`.github/workflows/`)

- **ci.yml** - Continuous integration pipeline

## File Count Summary

| Category | Files | Purpose |
|-----------|--------|---------|
| Engine Core | ~15 | ECS, scenes, core systems |
| Rendering | ~10 | 2D rendering, shaders, lighting |
| Audio | ~8 | Sound, music, mixing |
| Physics | ~6 | Box2D integration, collisions |
| Input | ~6 | Keyboard, mouse, gamepad, tablet |
| Tools | ~20 | Pixel art editor complete |
| I/O | ~6 | File formats, compression |
| Signals | ~4 | Event system |
| Threading | ~5 | Async operations |
| Headless | ~4 | CLI mode |
| UI | ~30 | Complete GUI interface |
| Examples | ~6 | Sample projects |
| Tests | ~10 | Unit and integration tests |
| **Total** | **~130** | Complete 2D game engine |

## Key Features Implemented

✅ **Complete Pixel Art Editor**
- Document model with layers, frames, tags
- Drawing tools and algorithms
- Brush system with pressure sensitivity
- Animation support
- Export to multiple formats

✅ **Advanced Engine Systems**
- Entity-Component System
- 2D Rendering with shaders
- Physics integration
- Audio system
- Input handling (including tablets)

✅ **Developer Tools**
- Signals/Slots for decoupled code
- Threading for async operations
- Headless mode for batch processing
- Command pattern with undo/redo
- Comprehensive testing

✅ **Professional Features**
- Binary format (.ges) with compression
- Performance optimizations
- Complete documentation
- CI/CD pipeline
- Package distribution ready

This is a production-ready 2D game engine with pixel art editing capabilities, comparable to Aseprite + Godot features for 2D development.
