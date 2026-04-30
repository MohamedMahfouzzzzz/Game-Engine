# Game Engine Test Suite

## Test Structure

```
tests/
├── core/               # Engine core tests
│   ├── test_node_system.py
│   ├── test_project_system.py
│   ├── test_signals_instancing.py
│   └── test_engine_core.py
├── runtime/            # Runtime/execution tests
│   ├── test_game_loop.py
│   └── test_external_runtimes.py
├── scripts/            # Lua script tests
│   ├── test_sprite_api.lua
│   ├── test_color_api.lua
│   ├── test_geometry_api.lua
│   ├── test_app_api.lua
│   ├── test_image_api.lua
│   ├── test_all.lua
│   └── run_tests.py
├── security/           # Security tests
│   ├── test_extension_security.py
│   ├── test_project_security.py
│   ├── test_telemetry_security.py
│   ├── test_config_security.py
│   ├── test_scripting_security.py
│   └── test_project_io_security.py
├── performance/        # Performance tests
│   ├── test_memory_performance.py
│   ├── test_cpu_performance.py
│   └── test_soak_memory.py
├── load/               # Heavy load/stress tests
│   ├── test_stress_load.py
│   └── test_edge_cases.py
├── integration/        # Integration tests
│   └── test_full_workflow.py
├── interop/            # Interoperability tests
│   ├── test_godot_project_import.py
│   └── test_godot_tscn_interop.py
├── importers/          # Import system tests
│   ├── test_general_import.py
│   ├── test_import_cli.py
│   └── test_reimport_cache.py
└── unit/               # Unit tests
    ├── test_uid_registry.py
    └── test_transform2d.py
```

## Running Tests

### Python Tests
```bash
# All tests
python -m pytest tests/ -v

# Specific category
python -m pytest tests/core/ -v
python -m pytest tests/security/ -v
python -m pytest tests/performance/ -v

# With markers
python -m pytest tests/ -m "not slow" -v
```

### Lua Tests
```bash
# Via Python runner
python tests/scripts/run_tests.py

# Or manually in Aseprite/Engine
> dofile("tests/scripts/test_all.lua")
```

## Test Categories

1. **Core Tests** - Engine fundamentals (nodes, projects, scenes)
2. **Runtime Tests** - Game loop, external runtimes
3. **Script Tests** - Lua/Aseprite API compatibility
4. **Security Tests** - Path traversal, sandboxing, encryption
5. **Performance Tests** - Memory, CPU, benchmarks
6. **Load Tests** - Stress, edge cases, heavy load
7. **Integration Tests** - End-to-end workflows
8. **Interop Tests** - Godot import, format conversion
9. **Importer Tests** - Asset import pipeline
10. **Unit Tests** - Isolated component testing
