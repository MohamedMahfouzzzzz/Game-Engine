import gc

import pytest

from engine.core.node_base import Node, Node2D
from engine.dialogue.parser import Call, DialogueTree, Line
from engine.dialogue.runtime import DialogueRuntime, dialogue_to_json
from engine.interop.godot_importer import GodotImporter
from engine.signals.signal_manager import get_signal_manager
from engine.tools.pixel_art_editor.canvas import Canvas
from engine.tools.pixel_art_editor.core.image_buffer import ImageBuffer


def test_image_buffer_is_lazy_and_tracks_dirty_rect():
    buffer = ImageBuffer(2048, 2048)

    assert buffer.get_memory_size() == 0
    assert buffer.get_pixel(12, 12) == (0, 0, 0, 0)

    delta = buffer.set_pixel(12, 12, (255, 0, 0, 255))

    assert delta is not None
    assert delta.before == (0, 0, 0, 0)
    assert delta.after == (255, 0, 0, 255)
    assert buffer.dirty_rect == (12, 12, 1, 1)
    assert buffer.get_memory_size() > 0


def test_canvas_delta_undo_and_dirty_rect():
    canvas = Canvas(16, 16)

    canvas.set_pixel(1, 1, (10, 20, 30, 255))
    canvas.set_pixel(3, 4, (40, 50, 60, 255))
    canvas.save_state()

    assert canvas.dirty_rect == (1, 1, 3, 4)
    assert canvas.get_current_layer().get_pixel(3, 4) == (40, 50, 60, 255)

    assert canvas.undo() is True
    assert canvas.get_current_layer().get_pixel(1, 1) == (0, 0, 0, 0)
    assert canvas.get_current_layer().get_pixel(3, 4) == (0, 0, 0, 0)

    assert canvas.redo() is True
    assert canvas.get_current_layer().get_pixel(1, 1) == (10, 20, 30, 255)


def test_dialogue_runtime_detects_goto_cycle_and_exports_json():
    runtime = DialogueRuntime()
    runtime.load_dialogue([
        DialogueTree("A", [Call("goto", ["B"])]),
        DialogueTree("B", [Call("goto", ["A"])]),
    ])

    with pytest.raises(RuntimeError, match="Dialogue cycle"):
        runtime.start("A")

    payload = dialogue_to_json({"Intro": DialogueTree("Intro", [Line("Hero", "Hello")])})
    assert '"Intro"' in payload
    assert '"Hello"' in payload


def test_node_child_index_and_signal_cleanup():
    parent = Node("parent")
    child = Node("child")

    parent.add_child(child)
    assert parent.get_child("child") is child

    manager = get_signal_manager()

    class Receiver:
        def called(self):
            pass

    receiver = Receiver()
    manager.connect("audit_cleanup", receiver.called)
    assert manager.connection_count("audit_cleanup") == 1

    del receiver
    gc.collect()
    manager.prune_dead()
    assert manager.connection_count("audit_cleanup") == 0

    parent.remove_child(child)
    assert parent.get_child("child") is None


def test_importer_keeps_2d_animation_nodes_and_reports_3d_skip(tmp_path):
    tscn = tmp_path / "scene.tscn"
    tscn.write_text(
        """
[gd_scene load_steps=2 format=3]

[node name="Root" type="Node2D"]

[node name="Animator" type="AnimationPlayer" parent="."]
autoplay = "idle"
speed_scale = 1.25

[node name="MoveTween" type="Tween" parent="."]
active = true

[node name="Camera" type="Camera3D" parent="."]
        """,
        encoding="utf-8",
    )

    project = GodotImporter().import_project(str(tscn))
    root = project.active_scene.root

    animator = root.get_child("Animator")
    tween = root.get_child("MoveTween")

    assert animator is not None
    assert animator.get_property("autoplay") == "idle"
    assert tween is not None
    assert tween.get_property("active") is True
    assert "Camera3D" in root.get_property("interop_report")["skipped_3d_node_types"]


def test_sorted_children_cache_uses_z_and_y_sort():
    from ui.widgets.viewport import ViewportWidget

    parent = Node2D("parent")
    parent.y_sort_enabled = True
    low = Node2D("low")
    high = Node2D("high")
    low.z_index = 0
    high.z_index = 10
    low.set_position(0, 100)
    high.set_position(0, 0)
    parent.add_child(high)
    parent.add_child(low)

    widget = type("ViewportStub", (), {"_sorted_children_cache": {}})()

    assert ViewportWidget._get_sorted_children(widget, parent) == [low, high]
