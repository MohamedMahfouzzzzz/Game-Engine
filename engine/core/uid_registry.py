# /**************************************************************************/
# /*  uid_registry.py                                                       */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""
Global UID registry for all engine objects.

Every Node, Scene, and Project gets a human-readable, collision-resistant UID:

    Format:  GE-<TypePrefix>-<TimestampHex8>-<Random6>
    Example: GE-N2D-1a2b3c4d-f4e5d6

The registry guarantees uniqueness across the lifetime of the process and
persists used UIDs so that reloaded projects never collide.
"""

from __future__ import annotations

import logging
import secrets
import threading
import time
import weakref
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Type-prefix map  (extend as new node types are added)
# ---------------------------------------------------------------------------
_PREFIX_MAP: Dict[str, str] = {
    "Node":              "NO",
    "Node2D":            "N2D",
    "Sprite":            "SPR",
    "Sprite2D":          "SP2",
    "AnimatedSprite":    "ANS",
    "AnimatedSprite2D":  "AS2",
    "Camera2D":          "CAM",
    "Light2D":           "LGT",
    "Particle2D":        "PAR",
    "RigidBody2D":       "RBD",
    "StaticBody2D":      "SBD",
    "KinematicBody2D":   "KBD",
    "CharacterBody2D":   "CBD",
    "Area2D":            "ARE",
    "CollisionShape2D":  "CSH",
    "TileMap":           "TLM",
    "TileSet":           "TLS",
    "Skeleton2D":        "SKL",
    "Bone2D":            "BON",
    "Control":           "CTL",
    "Label":             "LBL",
    "Button":            "BTN",
    "Panel":             "PNL",
    "Container":         "CNT",
    "VBoxContainer":     "VBX",
    "HBoxContainer":     "HBX",
    "CanvasLayer":       "CVL",
    "AnimationPlayer":   "ANP",
    "AudioStreamPlayer": "AUD",
    "Scene":             "SC",
    "Project":           "PRJ",
    "Resource":          "RES",
}

_DEFAULT_PREFIX = "OBJ"
_GEN_LOCK = threading.Lock()
_GEN_COUNTER = 0


class UIDRegistry:
    """Thread-safe, process-global UID registry.

    Objects are stored as *weak references* so that the registry does not
    prevent garbage collection.
    """

    def __init__(self) -> None:
        # uid → weak reference to the object
        self._registry: Dict[str, weakref.ref] = {}
        # set of ALL UIDs ever issued in this session (prevents reuse)
        self._issued: set[str] = set()

    # ------------------------------------------------------------------
    # UID generation
    # ------------------------------------------------------------------

    @staticmethod
    def generate(type_name: str = "Node") -> str:
        """Generate a new unique UID.

        Args:
            type_name: The class name of the object (e.g. ``"Node2D"``).

        Returns:
            A UID string like ``"GE-N2D-1a2b3c4d-f4e5d6"``.
        """
        global _GEN_COUNTER
        prefix = _PREFIX_MAP.get(type_name, _DEFAULT_PREFIX)
        ts_hex = f"{int(time.time()):08x}"
        with _GEN_LOCK:
            _GEN_COUNTER += 1
            counter_hex = f"{_GEN_COUNTER & 0xFFFFFF:06x}"
        return f"GE-{prefix}-{ts_hex}-{counter_hex}"

    def issue(self, type_name: str = "Node") -> str:
        """Generate AND register a UID (collision-safe)."""
        while True:
            uid = self.generate(type_name)
            if uid not in self._issued:
                self._issued.add(uid)
                return uid

    # ------------------------------------------------------------------
    # Registry operations
    # ------------------------------------------------------------------

    def register(self, uid: str, obj: object) -> None:
        """Bind a UID to an object (weak reference)."""
        self._issued.add(uid)
        self._registry[uid] = weakref.ref(obj)

    def lookup(self, uid: str) -> Optional[object]:
        """Return the live object for *uid*, or ``None`` if it was GC'd."""
        ref = self._registry.get(uid)
        if ref is None:
            return None
        obj = ref()
        if obj is None:
            # Object has been garbage-collected — clean up
            del self._registry[uid]
        return obj

    def release(self, uid: str) -> None:
        """Remove a UID from the live registry (object is being destroyed).

        The UID stays in ``_issued`` to prevent reuse within the session.
        """
        self._registry.pop(uid, None)

    def unregister(self, uid: str) -> None:
        """Alias for release() - removes UID from registry."""
        self.release(uid)

    def is_registered(self, uid: str) -> bool:
        return uid in self._registry

    def was_issued(self, uid: str) -> bool:
        """True if the UID was ever generated this session (even if released)."""
        return uid in self._issued

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def export_issued(self) -> list[str]:
        """Return all UIDs issued this session (for persistence)."""
        return sorted(self._issued)

    def import_issued(self, uids: list[str]) -> None:
        """Restore a previously-persisted list of issued UIDs so they are
        never reused after a project reload."""
        self._issued.update(uids)

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self._registry)

    def __repr__(self) -> str:
        return f"<UIDRegistry live={len(self._registry)} issued={len(self._issued)}>"

    def get_memory_stats(self) -> dict:
        """Get memory statistics for tracked objects.
        
        Returns:
            Dict with object counts and estimated memory usage
        """
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
                except:
                    pass
        
        return {
            "live_objects": len(self._registry),
            "issued_uids": len(self._issued),
            "by_type": type_counts,
            "estimated_bytes": total_size,
        }

    def find_leaked_objects(self, max_referrers: int = 10) -> list:
        """Find objects with suspicious reference counts (potential leaks).
        
        Args:
            max_referrers: Threshold for suspicious referrer count
            
        Returns:
            List of (uid, class_name, referrer_count) tuples
        """
        import gc
        
        leaked = []
        for uid, obj_ref in list(self._registry.items()):
            obj = obj_ref()
            if obj is not None:
                referrers = len(gc.get_referrers(obj))
                if referrers > max_referrers:
                    leaked.append((uid, obj.__class__.__name__, referrers))
        
        return sorted(leaked, key=lambda x: x[2], reverse=True)


# ---------------------------------------------------------------------------
# Process-global singleton
# ---------------------------------------------------------------------------
_global_registry: Optional[UIDRegistry] = None


def get_registry() -> UIDRegistry:
    """Return the process-global :class:`UIDRegistry` instance."""
    global _global_registry
    if _global_registry is None:
        _global_registry = UIDRegistry()
    return _global_registry


def generate_uid(type_name: str = "Node") -> str:
    """Convenience: generate and register a UID via the global registry."""
    return get_registry().issue(type_name)
