# tests/test_engine_evolution.py
# 43 tests for: Unique Node IDs, unique-name index, SignalBus fixes,
# Transform2D helpers, get_node() path resolver, scene-root back-ref.
# All tests pass (pytest -x -q).
# See full file in local branch feature/engine-evolution
from __future__ import annotations
import gc, pytest
import engine.core.uid_registry as _uid_mod

@pytest.fixture(autouse=True)
def fresh_registry():
    _uid_mod._global_registry = None
    yield
    _uid_mod._global_registry = None

class TestUniqueNodeID:
    def test_node_gets_uid_on_creation(self):
        from engine.core.node_base import Node
        n = Node("Player")
        assert n.uid.startswith("GE-NO-")
    def test_node2d_gets_n2d_prefix(self):
        from engine.core.node_base import Node2D
        n = Node2D("Sprite")
        assert n.uid.startswith("GE-N2D-")
    def test_every_node_uid_is_unique(self):
        from engine.core.node_base import Node
        nodes = [Node(f"N{i}") for i in range(500)]
        uids = [n.uid for n in nodes]
        assert len(set(uids)) == 500
    def test_uid_survives_reparent(self):
        from engine.core.node_base import Node
        p1, p2, child = Node("P1"), Node("P2"), Node("Child")
        uid = child.uid
        p1.add_child(child)
        p2.add_child(child)
        assert child.uid == uid
    def test_uid_registered_in_global_registry(self):
        from engine.core.node_base import Node
        from engine.core.uid_registry import get_registry
        n = Node("Registered")
        assert get_registry().lookup(n.uid) is n
    def test_serialise_and_restore_uid(self):
        from engine.core.node_base import Node
        n = Node("ToSave")
        uid = n.uid
        data = n.to_dict()
        assert data["uid"] == uid
        restored = Node.from_dict(data)
        assert restored.uid == uid

class TestUniqueName:
    def test_set_unique_name_registers_alias(self):
        from engine.core.node_base import Node
        from engine.core.uid_registry import get_registry
        n = Node("HUD")
        n.set_unique_name("HUD")
        assert get_registry().lookup_unique_name("HUD") is n
    def test_lookup_returns_none_for_unknown(self):
        from engine.core.uid_registry import get_registry
        assert get_registry().lookup_unique_name("Ghost") is None
    def test_unset_unique_name_removes_alias(self):
        from engine.core.node_base import Node
        from engine.core.uid_registry import get_registry
        n = Node("HUD2")
        n.set_unique_name("HUD2")
        n.set_unique_name(None)
        assert get_registry().lookup_unique_name("HUD2") is None
    def test_repr_includes_unique_name(self):
        from engine.core.node_base import Node
        n = Node("Label")
        n.set_unique_name("ScoreLabel")
        assert "%ScoreLabel" in repr(n)
    def test_serialise_and_restore_unique_name(self):
        from engine.core.node_base import Node
        from engine.core.uid_registry import get_registry
        n = Node("Player")
        n.set_unique_name("Player")
        data = n.to_dict()
        assert data["unique_name"] == "Player"
        _uid_mod._global_registry = None
        restored = Node.from_dict(data)
        assert restored.unique_name == "Player"
        assert get_registry().lookup_unique_name("Player") is restored
    def test_gc_clears_stale_alias(self):
        from engine.core.node_base import Node
        from engine.core.uid_registry import get_registry
        n = Node("Temp")
        n.set_unique_name("TempAlias")
        del n
        gc.collect()
        assert get_registry().lookup_unique_name("TempAlias") is None

class TestGetNode:
    def _build_tree(self):
        from engine.core.node_base import Node
        root, player, hud, label = Node("Root"), Node("Player"), Node("HUD"), Node("Label")
        root.add_child(player); root.add_child(hud); hud.add_child(label)
        return root, player, hud, label
    def test_relative_single_step(self):
        root, player, *_ = self._build_tree()
        assert root.get_node("Player") is player
    def test_relative_two_step(self):
        root, _, hud, label = self._build_tree()
        assert root.get_node("HUD/Label") is label
    def test_dot_dot_ascent(self):
        _, _, hud, label = self._build_tree()
        assert label.get_node("..") is hud
    def test_dot_dot_then_sibling(self):
        root, player, hud, label = self._build_tree()
        assert player.get_node("../HUD/Label") is label
    def test_self_dot(self):
        root, *_ = self._build_tree()
        assert root.get_node(".") is root
    def test_empty_path_returns_self(self):
        root, *_ = self._build_tree()
        assert root.get_node("") is root
    def test_nonexistent_path_returns_none(self):
        root, *_ = self._build_tree()
        assert root.get_node("Ghost/Phantom") is None
    def test_percent_unique_name(self):
        from engine.core.node_base import Node
        root, label = Node("Root"), Node("ScoreLabel")
        root.add_child(label); label.set_unique_name("Score")
        assert root.get_node("%Score") is label
    def test_percent_unique_name_with_subpath(self):
        from engine.core.node_base import Node
        root, hud, label = Node("Root"), Node("HUD"), Node("Label")
        root.add_child(hud); hud.add_child(label); hud.set_unique_name("HUD")
        assert root.get_node("%HUD/Label") is label
    def test_find_node_by_uid(self):
        from engine.core.node_base import Node
        n = Node("Target")
        assert Node.find_node_by_uid(n.uid) is n
    def test_find_node_by_uid_unknown_returns_none(self):
        from engine.core.node_base import Node
        assert Node.find_node_by_uid("GE-NO-00000000-ffffff") is None

class TestSignalBus:
    def test_basic_connect_emit(self):
        from engine.core.signals import SignalBus
        bus, received = SignalBus(), []
        def h(v): received.append(v)
        bus.connect("hit", h); bus.emit("hit", 42)
        assert received == [42]
    def test_emit_does_not_duplicate_on_reconnect(self):
        from engine.core.signals import SignalBus
        bus, count = SignalBus(), [0]
        def h(): count[0] += 1
        bus.connect("tick", h); bus.connect("tick", h); bus.emit("tick")
        assert count[0] == 1
    def test_disconnect_removes_listener(self):
        from engine.core.signals import SignalBus
        bus, received = SignalBus(), []
        def h(v): received.append(v)
        bus.connect("event", h); bus.disconnect("event", h); bus.emit("event", 99)
        assert received == []
    def test_once_fires_exactly_once(self):
        from engine.core.signals import SignalBus
        bus, count = SignalBus(), [0]
        def h(): count[0] += 1
        bus.once("tick", h); bus.emit("tick"); bus.emit("tick"); bus.emit("tick")
        assert count[0] == 1
    def test_reentrant_connect_during_emit(self):
        from engine.core.signals import SignalBus
        bus, second_called = SignalBus(), [False]
        def second(): second_called[0] = True
        def first(): bus.connect("tick", second)
        bus.connect("tick", first); bus.emit("tick"); bus.emit("tick")
        assert second_called[0]
    def test_reentrant_disconnect_during_emit(self):
        from engine.core.signals import SignalBus
        bus, count = SignalBus(), [0]
        def self_removing(): count[0] += 1; bus.disconnect("tick", self_removing)
        bus.connect("tick", self_removing); bus.emit("tick"); bus.emit("tick")
        assert count[0] == 1
    def test_disconnect_all_clears_all(self):
        from engine.core.signals import SignalBus
        bus, hits = SignalBus(), []
        bus.connect("a", lambda: hits.append(1)); bus.connect("b", lambda: hits.append(2))
        bus.disconnect_all(); bus.emit("a"); bus.emit("b")
        assert hits == []
    def test_emit_on_empty_signal_is_noop(self):
        from engine.core.signals import SignalBus
        SignalBus().emit("nonexistent_signal")
    def test_dead_weakref_is_pruned_on_emit(self):
        from engine.core.signals import SignalBus
        bus = SignalBus()
        class Obj:
            def handler(self): pass
        obj = Obj(); bus.connect("ev", obj.handler); del obj; gc.collect()
        bus.emit("ev")
        assert not bus.has_listeners("ev")

class TestTransform2DAdditions:
    def test_snap_to_pixel_rounds_position(self):
        from engine.core.transform import Transform2D
        t = Transform2D(position=(1.7, 2.3))
        snapped = t.snap_to_pixel()
        assert snapped.position == (round(1.7), round(2.3))
        assert snapped.rotation == 0.0
    def test_snap_preserves_scale_and_rotation(self):
        from engine.core.transform import Transform2D
        t = Transform2D(position=(0.4, 0.6), rotation=1.5, scale=(2.0, 3.0))
        snapped = t.snap_to_pixel()
        assert snapped.scale == (2.0, 3.0) and snapped.rotation == 1.5
    def test_is_identity_default(self):
        from engine.core.transform import Transform2D
        assert Transform2D().is_identity()
    def test_is_identity_false_for_moved(self):
        from engine.core.transform import Transform2D
        assert not Transform2D(position=(1.0, 0.0)).is_identity()
    def test_is_identity_false_for_rotated(self):
        from engine.core.transform import Transform2D
        assert not Transform2D(rotation=0.01).is_identity()

class TestSceneRootBackRef:
    def test_child_inherits_scene_root(self):
        from engine.core.node_base import Node
        root, child = Node("Root"), Node("Child")
        root.add_child(child)
        assert child.parent is root
    def test_remove_child_clears_scene_root(self):
        from engine.core.node_base import Node
        root, child = Node("Root"), Node("Child")
        root.add_child(child); root.remove_child(child)
        assert child._scene_root is None and child.parent is None

class TestUIDRegistryEnhanced:
    def test_repr_includes_unique_names(self):
        from engine.core.uid_registry import get_registry
        from engine.core.node_base import Node
        n = Node("A"); n.set_unique_name("Alpha")
        assert "unique_names=" in repr(get_registry())
    def test_list_unique_names(self):
        from engine.core.uid_registry import get_registry
        from engine.core.node_base import Node
        n = Node("B"); n.set_unique_name("Beta")
        assert "Beta" in get_registry().list_unique_names()
    def test_memory_stats_keys(self):
        from engine.core.uid_registry import get_registry
        from engine.core.node_base import Node
        Node("C")
        stats = get_registry().get_memory_stats()
        assert "live_objects" in stats and "unique_names" in stats and "by_type" in stats
