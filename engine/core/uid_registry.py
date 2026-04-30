# engine/core/uid_registry.py
# Global UID registry — Godot 4.6 unique-name secondary index added
from __future__ import annotations
import logging, threading, time, weakref
from typing import Dict, Optional

logger = logging.getLogger(__name__)

_PREFIX_MAP: Dict[str, str] = {
    "Node": "NO", "Node2D": "N2D", "Sprite": "SPR", "Sprite2D": "SP2",
    "AnimatedSprite": "ANS", "AnimatedSprite2D": "AS2", "Camera2D": "CAM",
    "Light2D": "LGT", "Particle2D": "PAR", "RigidBody2D": "RBD",
    "StaticBody2D": "SBD", "KinematicBody2D": "KBD", "CharacterBody2D": "CBD",
    "Area2D": "ARE", "CollisionShape2D": "CSH", "TileMap": "TLM",
    "TileSet": "TLS", "Skeleton2D": "SKL", "Bone2D": "BON",
    "Control": "CTL", "Label": "LBL", "Button": "BTN", "Panel": "PNL",
    "Container": "CNT", "VBoxContainer": "VBX", "HBoxContainer": "HBX",
    "CanvasLayer": "CVL", "AnimationPlayer": "ANP", "AudioStreamPlayer": "AUD",
    "Scene": "SC", "Project": "PRJ", "Resource": "RES",
}
_DEFAULT_PREFIX = "OBJ"
_GEN_LOCK = threading.Lock()
_GEN_COUNTER = 0


class UIDRegistry:
    def __init__(self) -> None:
        self._registry: Dict[str, weakref.ref] = {}
        self._issued: set = set()
        self._unique_names: Dict[str, weakref.ref] = {}

    @staticmethod
    def generate(type_name: str = "Node") -> str:
        global _GEN_COUNTER
        prefix = _PREFIX_MAP.get(type_name, _DEFAULT_PREFIX)
        ts_hex = f"{int(time.time()):08x}"
        with _GEN_LOCK:
            _GEN_COUNTER += 1
            counter_hex = f"{_GEN_COUNTER & 0xFFFFFF:06x}"
        return f"GE-{prefix}-{ts_hex}-{counter_hex}"

    def issue(self, type_name: str = "Node") -> str:
        while True:
            uid = self.generate(type_name)
            if uid not in self._issued:
                self._issued.add(uid)
                return uid

    def register(self, uid: str, obj: object) -> None:
        self._issued.add(uid)
        self._registry[uid] = weakref.ref(obj)

    def lookup(self, uid: str) -> Optional[object]:
        ref = self._registry.get(uid)
        if ref is None:
            return None
        obj = ref()
        if obj is None:
            del self._registry[uid]
        return obj

    def release(self, uid: str) -> None:
        self._registry.pop(uid, None)

    def unregister(self, uid: str) -> None:
        self.release(uid)

    def is_registered(self, uid: str) -> bool:
        return uid in self._registry

    def was_issued(self, uid: str) -> bool:
        return uid in self._issued

    # Godot 4.6 unique-name secondary index
    def register_unique_name(self, alias: str, node: object) -> None:
        if alias in self._unique_names:
            existing = self._unique_names[alias]()
            if existing is not None and existing is not node:
                logger.warning("Unique-name '%s' already registered for %r; overwriting.", alias, existing)
        self._unique_names[alias] = weakref.ref(node)

    def unregister_unique_name(self, alias: str) -> None:
        self._unique_names.pop(alias, None)

    def lookup_unique_name(self, alias: str) -> Optional[object]:
        ref = self._unique_names.get(alias)
        if ref is None:
            return None
        node = ref()
        if node is None:
            del self._unique_names[alias]
        return node

    def list_unique_names(self) -> Dict[str, str]:
        result: Dict[str, str] = {}
        for alias, ref in list(self._unique_names.items()):
            node = ref()
            if node is not None and hasattr(node, "uid"):
                result[alias] = node.uid  # type: ignore[attr-defined]
            else:
                self._unique_names.pop(alias, None)
        return result

    def export_issued(self) -> list:
        return sorted(self._issued)

    def import_issued(self, uids: list) -> None:
        self._issued.update(uids)

    def __len__(self) -> int:
        return len(self._registry)

    def __repr__(self) -> str:
        return (f"<UIDRegistry live={len(self._registry)} "
                f"issued={len(self._issued)} unique_names={len(self._unique_names)}>")

    def get_memory_stats(self) -> dict:
        import sys
        type_counts: dict = {}
        total_size = 0
        for uid, obj_ref in list(self._registry.items()):
            obj = obj_ref()
            if obj is not None:
                class_name = obj.__class__.__name__
                type_counts[class_name] = type_counts.get(class_name, 0) + 1
                try:
                    total_size += sys.getsizeof(obj)
                except Exception:
                    pass
        return {"live_objects": len(self._registry), "issued_uids": len(self._issued),
                "unique_names": len(self._unique_names), "by_type": type_counts, "estimated_bytes": total_size}

    def find_leaked_objects(self, max_referrers: int = 10) -> list:
        import gc
        leaked = []
        for uid, obj_ref in list(self._registry.items()):
            obj = obj_ref()
            if obj is not None:
                referrers = len(gc.get_referrers(obj))
                if referrers > max_referrers:
                    leaked.append((uid, obj.__class__.__name__, referrers))
        return sorted(leaked, key=lambda x: x[2], reverse=True)


_global_registry: Optional[UIDRegistry] = None

def get_registry() -> UIDRegistry:
    global _global_registry
    if _global_registry is None:
        _global_registry = UIDRegistry()
    return _global_registry

def generate_uid(type_name: str = "Node") -> str:
    return get_registry().issue(type_name)
