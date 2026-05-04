"""Comprehensive demo of advanced Game Engine features.

This example demonstrates:
- GD Language features
- Database save/load system
- Encryption
- Dialogue manager
- Kanban board
- Project debugging
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.project import ProjectManager, ProjectInitializer
from engine.gd_lang import GDArray, GDDictionary, Type, setup_builtins
from engine.database import SaveManager, DatabaseManager
from engine.dialogue import DialogueManager, DialogueNode, DialogueType, DialogueChoice
from engine.editor import KanbanBoard, Task, TaskStatus, TaskPriority
from engine.debug import GlobalDebugger, BuildValidator
from engine.diagnostics import TelemetryTree, EventType, PerformanceMetrics
from engine.build import ExportManager, ExportConfig, Platform


def demo_gd_language():
    """Demo GD Language features."""
    print("\n" + "=" * 60)
    print("GD LANGUAGE FEATURES")
    print("=" * 60)

    # Type-safe arrays
    print("\n1. Type-Safe Arrays:")
    inventory = GDArray(element_type=Type.STRING)
    inventory.append("sword")
    inventory.append("shield")
    inventory.append("potion")

    print(f"  Inventory: {inventory.to_list()}")
    print(f"  Size: {inventory.size()}")
    print(f"  Has shield: {inventory.has('shield')}")

    # Type-safe dictionaries
    print("\n2. Type-Safe Dictionaries:")
    player_stats = GDDictionary(value_type=Type.INT)
    player_stats.set("health", 100)
    player_stats.set("mana", 50)
    player_stats.set("stamina", 80)

    for stat, value in player_stats.items():
        print(f"  {stat}: {value}")

    # Built-in functions
    print("\n3. Built-in Functions:")
    globals_dict = {}
    setup_builtins(globals_dict)

    print(f"  sqrt(16) = {globals_dict['sqrt'](16)}")
    print(f"  clamp(150, 0, 100) = {globals_dict['clamp'](150, 0, 100)}")
    print(f"  typeof('hello') = {globals_dict['typeof']('hello')}")


def demo_database_and_saves():
    """Demo database and save system."""
    print("\n" + "=" * 60)
    print("DATABASE & SAVE SYSTEM")
    print("=" * 60)

    project_path = Path("./temp_demo_project")
    project_path.mkdir(exist_ok=True)

    # Initialize project
    initializer = ProjectInitializer()
    initializer.create_project_structure(str(project_path), "DemoGame")

    save_mgr = SaveManager(str(project_path))

    # Create save data
    print("\n1. Creating Save Data:")
    game_state = {
        'level': 1,
        'player': {
            'name': 'Hero',
            'health': 100,
            'position': [50, 100]
        },
        'inventory': ['sword', 'shield', 'potion'],
        'enemies': [
            {'id': 1, 'health': 30},
            {'id': 2, 'health': 45}
        ]
    }

    print(f"  Game State: {game_state}")

    # Save with encryption
    print("\n2. Saving with Encryption:")
    save_mgr.save_game(1, game_state, encrypt=True)
    print("  ✓ Saved to encrypted slot 1")

    # List saves
    print("\n3. Available Saves:")
    all_saves = save_mgr.get_all_saves()
    for save in all_saves:
        print(f"  - Slot {save.slot}: {save.name}")

    # Load save
    print("\n4. Loading Save:")
    loaded, metadata = save_mgr.load_game(1)
    print(f"  Loaded level: {loaded['level']}")
    print(f"  Loaded player: {loaded['player']}")

    return project_path


def demo_dialogue_system(project_path):
    """Demo dialogue manager."""
    print("\n" + "=" * 60)
    print("DIALOGUE MANAGER")
    print("=" * 60)

    dialogue_mgr = DialogueManager(str(project_path))

    # Create dialogue
    print("\n1. Creating Dialogue Tree:")
    dialogue = dialogue_mgr.create_dialogue("greeting", "NPC Greeting")

    # Create nodes
    start_node = DialogueNode(
        id="start",
        type=DialogueType.START,
        character="NPC",
        text="Greetings, traveler! What brings you here?"
    )

    choice_node = DialogueNode(
        id="choice_main",
        type=DialogueType.CHOICE,
        character="You",
        text=""
    )

    # Add choices with conditions
    choice_node.add_choice(DialogueChoice(
        id="choice_help",
        text="I'm looking for a quest",
        next_node_id="quest_node",
        flag_set={"seeking_quest": True}
    ))

    choice_node.add_choice(DialogueChoice(
        id="choice_trade",
        text="Do you have anything to trade?",
        next_node_id="trade_node"
    ))

    quest_node = DialogueNode(
        id="quest_node",
        type=DialogueType.DIALOGUE,
        character="NPC",
        text="Excellent! I have a quest for you...",
        next_node_id="end"
    )

    end_node = DialogueNode(
        id="end",
        type=DialogueType.END,
        character="NPC",
        text="Good luck, hero!"
    )

    # Add nodes
    for node in [start_node, choice_node, quest_node, end_node]:
        dialogue.add_node(node)

    print(f"  Created dialogue with {len(dialogue.nodes)} nodes")

    # Save dialogue
    dialogue_mgr.save_dialogue("greeting")
    print("  ✓ Saved dialogue to disk")

    # Play dialogue
    print("\n2. Playing Dialogue:")
    current = dialogue_mgr.start_dialogue("greeting")
    print(f"  {current.character}: {current.text}")

    choices = dialogue_mgr.get_current_choices()
    print(f"  Available choices: {len(choices)}")
    for choice in choices:
        print(f"    - {choice.text}")


def demo_kanban_board():
    """Demo Kanban board system."""
    print("\n" + "=" * 60)
    print("KANBAN BOARD")
    print("=" * 60)

    # Create board
    print("\n1. Creating Board:")
    board = KanbanBoard("Game Development")

    # Create tasks
    print("\n2. Adding Tasks:")
    tasks = [
        ("feat_player", "Implement player movement", TaskPriority.HIGH),
        ("feat_enemies", "Create enemy AI", TaskPriority.HIGH),
        ("feat_ui", "Design UI layout", TaskPriority.MEDIUM),
        ("bug_collision", "Fix collision detection", TaskPriority.CRITICAL),
    ]

    for task_id, title, priority in tasks:
        board.create_task(task_id, title, priority=priority)
        print(f"  ✓ {title}")

    # Move some tasks
    print("\n3. Moving Tasks:")
    board.move_task("feat_player", TaskStatus.IN_PROGRESS)
    board.move_task("feat_enemies", TaskStatus.IN_PROGRESS)
    print("  ✓ Moved tasks to In Progress")

    # Get statistics
    print("\n4. Board Statistics:")
    stats = board.get_board_stats()
    print(f"  Total Tasks: {stats['total_tasks']}")
    print(f"  Completion Rate: {stats['completion_rate']:.1f}%")
    print(f"  By Status:")
    for status, count in stats['tasks_by_status'].items():
        print(f"    - {status}: {count}")


def demo_debug_system(project_path):
    """Demo debugging and validation."""
    print("\n" + "=" * 60)
    print("DEBUG & VALIDATION SYSTEM")
    print("=" * 60)

    # Global debugger
    print("\n1. Running Full Project Debug:")
    debugger = GlobalDebugger(str(project_path))
    report = debugger.debug_project()

    print(f"  Total Issues Found: {report.summary['total']}")
    print(f"  Errors: {report.summary['error']}")
    print(f"  Warnings: {report.summary['warning']}")
    print(f"  Info: {report.summary['info']}")

    # Build validator
    print("\n2. Build Validation:")
    validator = BuildValidator(str(project_path))
    can_build, validate_report = validator.validate_for_build()

    if can_build:
        print("  ✓ Project is ready to build!")
    else:
        blockers = validator.get_build_blockers()
        print(f"  ✗ Build blockers found: {len(blockers)}")


def demo_telemetry():
    """Demo telemetry and performance monitoring."""
    print("\n" + "=" * 60)
    print("TELEMETRY & PERFORMANCE")
    print("=" * 60)

    # Create telemetry tree
    print("\n1. Event Telemetry:")
    telemetry = TelemetryTree("Game Session")

    # Log some events
    telemetry.push_event("scene_load", EventType.SCENE_LOAD)
    telemetry.pop_event(duration=125.5)

    telemetry.push_event("entity_spawn", EventType.ENTITY_SPAWN)
    telemetry.pop_event(duration=5.2)

    telemetry.log_event("collision", EventType.COLLISION)

    print(f"  Total Events: {telemetry.event_count}")
    print(f"  Event Types:")
    stats = telemetry.get_stats()
    for event_type, stat in stats.items():
        print(f"    - {event_type}: {stat['count']} events, " +
              f"{stat['average_duration_ms']:.2f}ms avg")

    # Performance metrics
    print("\n2. Performance Metrics:")
    metrics = PerformanceMetrics(max_history=60)

    # Simulate frames
    import time
    for i in range(10):
        start = time.time()
        time.sleep(0.016)  # ~60 FPS
        metrics.record_frame(active_entities=50, draw_calls=100)

    print(f"  Average FPS: {metrics.get_average_fps():.1f}")
    print(f"  Min FPS: {metrics.get_min_fps():.1f}")
    print(f"  Max FPS: {metrics.get_max_fps():.1f}")


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("GAME ENGINE ADVANCED FEATURES DEMONSTRATION")
    print("=" * 60)

    try:
        # Run demos
        demo_gd_language()

        project_path = demo_database_and_saves()

        demo_dialogue_system(project_path)

        demo_kanban_board()

        demo_debug_system(project_path)

        demo_telemetry()

        # Cleanup
        import shutil
        if project_path.exists():
            shutil.rmtree(project_path)
            print(f"\n✓ Cleaned up temporary project")

        print("\n" + "=" * 60)
        print("ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\n✗ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
