# /**************************************************************************/
# /*  node_base.py                                                          */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""
Core node hierarchy for the 2-D game engine.

:class:`Node`  — base scene-graph element.
:class:`Node2D` — positional 2-D node with transform, z-index, and modulate.

All nodes receive a collision-resistant UID from the global
:mod:`engine.core.uid_registry` the moment they are constructed.
"""

from __future__ import annotations

import logging
from collections import deque
from typing import Any, Deque, Dict, List, Optional, Tuple

from engine.core.signals import SignalBus

logger = logging.getLogger(__name__)
from engine.core.transform import Transform2D
from engine.core.types import NodeType
from engine.core.uid_registry import generate_uid, get_registry


# ---------------------------------------------------------------------------
# Base Node
# ---------------------------------------------------------------------------

class Node:
    """Base node with properties, children, and a weak-ref signal bus.

    Uses __slots__ for ~40% memory reduction and faster attribute access.
    Prevents arbitrary attribute creation, enforcing clean architecture.

    Attributes:
        uid:        Unique identifier (``GE-NOD-…``).
        name:       Human-readable label shown in the scene tree.
        node_type:  :class:`~engine.core.types.NodeType` enum value.
        parent:     Direct parent node (``None`` for root nodes).
        children:   Ordered list of child nodes.
        properties: Arbitrary key/value bag for runtime data.
        enabled:    When ``False`` the node is skipped during processing.
        visible:    When ``False`` the node is not rendered.
        script:     Path or source of the script attached to this node.
        signals:    :class:`~engine.core.signals.SignalBus` instance.
    """

    # __slots__ reduces memory by eliminating __dict__ and improves cache locality
    # __weakref__ is required for UID registry to create weak references
    __slots__ = [
        "uid", "name", "node_type", "parent", "children",
        "properties", "enabled", "processing", "visible", "script", "signals",
        "_child_by_name", "_tree_version", "_sort_dirty",
        "__weakref__"
    ]

    # Class-level list of signal names declared by this type (GDScript-style)
    _SIGNALS: List[str] = []

    def __init__(
        self,
        name: str = "Node",
        node_type: NodeType = NodeType.NODE,
    ) -> None:
        self.uid: str = generate_uid(node_type.value)
        self.name: str = name
        self.node_type: NodeType = node_type
        self.parent: Optional["Node"] = None
        self.children: List["Node"] = []
        self._child_by_name: Dict[str, List["Node"]] = {}
        self._tree_version: int = 0
        self._sort_dirty: bool = True
        self.properties: Dict[str, Any] = {}
        self.enabled: bool = True
        self.processing: bool = True
        self.visible: bool = True
        self.script: Optional[str] = None
        self.signals: SignalBus = SignalBus()

        # Register with the global UID registry (weak ref — no ownership)
        get_registry().register(self.uid, self)
        logger.debug("Node '%s' created with uid %s", name, self.uid)

    # ------------------------------------------------------------------
    # Tree management
    # ------------------------------------------------------------------

    def add_child(self, child: "Node") -> None:
        """Attach *child* to this node.  Reparents if already attached elsewhere."""
        if child is self:
            raise ValueError("A node cannot be parented to itself")
        ancestor: Optional["Node"] = self
        while ancestor is not None:
            if ancestor is child:
                raise ValueError("Circular parent-child relationship is not allowed")
            ancestor = ancestor.parent
        if child.parent is not None:
            child.parent.remove_child(child)
        child.parent = self
        self.children.append(child)
        self._child_by_name.setdefault(child.name, []).append(child)
        self._tree_version += 1
        self._sort_dirty = True
        logger.debug("Node '%s' added as child to '%s'", child.name, self.name)

    def remove_child(self, child: "Node") -> None:
        """Detach *child* from this node."""
        if child in self.children:
            self.children.remove(child)
            bucket = self._child_by_name.get(child.name)
            if bucket and child in bucket:
                bucket.remove(child)
                if not bucket:
                    self._child_by_name.pop(child.name, None)
            child.parent = None
            child.signals.disconnect_all()
            self._tree_version += 1
            self._sort_dirty = True
            try:
                from engine.signals.signal_manager import get_signal_manager
                get_signal_manager().prune_dead()
            except Exception:
                pass
            logger.debug("Node '%s' removed from parent '%s'", child.name, self.name)

    def get_child(self, name: str, default: Optional["Node"] = None) -> Optional["Node"]:
        """Return the first direct child with *name* in O(1) average time."""
        bucket = self._child_by_name.get(name)
        return bucket[0] if bucket else default

    def find_child(self, name: str, recursive: bool = True) -> Optional["Node"]:
        """Return the first child whose :attr:`name` matches, or ``None``."""
        for child in self.children:
            if child.name == name:
                return child
            if recursive:
                found = child.find_child(name, recursive=True)
                if found is not None:
                    return found
        return None

    def get_path(self) -> str:
        """Return the node's scene-tree path, e.g. ``"Root/Player/Sprite"``."""
        parts: List[str] = [self.name]
        node: Optional["Node"] = self.parent
        while node is not None:
            parts.append(node.name)
            node = node.parent
        return "/".join(reversed(parts))

    def iter_children(self, recursive: bool = False) -> "NodeIterator":
        """Iterate over children (and optionally all descendants)."""
        return NodeIterator(self, recursive=recursive)

    # ------------------------------------------------------------------
    # Property helpers
    # ------------------------------------------------------------------

    def set_property(self, key: str, value: Any) -> None:
        self.properties[key] = value

    def get_property(self, key: str, default: Any = None) -> Any:
        return self.properties.get(key, default)

    def has_property(self, key: str) -> bool:
        return key in self.properties

    # ------------------------------------------------------------------
    # Signal helpers (thin wrappers for ergonomic call-site code)
    # ------------------------------------------------------------------

    def connect(self, signal: str, callback: Any) -> None:
        self.signals.connect(signal, callback)

    def disconnect(self, signal: str, callback: Any) -> None:
        self.signals.disconnect(signal, callback)

    def emit(self, signal: str, *args: Any, **kwargs: Any) -> None:
        self.signals.emit(signal, *args, **kwargs)

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def _to_dict_base(self) -> Dict[str, Any]:
        return {
            "uid":        self.uid,
            "name":       self.name,
            "type":       self.node_type.value,
            "enabled":    self.enabled,
            "visible":    self.visible,
            "script":     self.script,
            "properties": self.properties,
            "children":   [child.to_dict() for child in self.children],
        }

    def to_dict(self) -> Dict[str, Any]:
        return self._to_dict_base()

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Node":
        node_type_val = data.get("type", NodeType.NODE.value)
        try:
            node_type = NodeType(node_type_val)
        except ValueError:
            node_type = NodeType.NODE

        if node_type == NodeType.NODE2D:
            node: Node = Node2D(data.get("name", "Node2D"))
        else:
            node = Node(data.get("name", "Node"), node_type)

        # Restore UID (but don't re-generate)
        saved_uid = data.get("uid")
        if saved_uid:
            node.uid = saved_uid
            get_registry().register(saved_uid, node)

        node.enabled    = data.get("enabled", True)
        node.visible    = data.get("visible", True)
        node.script     = data.get("script")
        node.properties = data.get("properties", {})

        if isinstance(node, Node2D):
            td = data.get("transform", {})
            node.transform.position = tuple(td.get("position", (0.0, 0.0)))  # type: ignore[assignment]
            node.transform.rotation = float(td.get("rotation", 0.0))
            node.transform.scale    = tuple(td.get("scale", (1.0, 1.0)))     # type: ignore[assignment]
            node.z_index   = int(data.get("z_index", 0))
            node.modulate  = tuple(data.get("modulate", (255, 255, 255, 255)))  # type: ignore[assignment]
            node.y_sort_enabled = bool(data.get("y_sort_enabled", False))

        for child_data in data.get("children", []):
            node.add_child(Node.from_dict(child_data))

        return node

    # ------------------------------------------------------------------
    # Object Pooling Support
    # ------------------------------------------------------------------

    def _reset(self) -> None:
        """Reset node state for reuse from object pool.
        
        Called when acquiring from pool. Generates new UID and clears state.
        """
        # Clear children
        self.children.clear()
        self._child_by_name.clear()
        self._tree_version += 1
        self._sort_dirty = True
        
        # Clear properties
        self.properties.clear()
        
        # Reset state
        self.enabled = True
        self.processing = True
        self.visible = True
        self.script = None
        self.parent = None
        
        # Generate new UID
        get_registry().unregister(self.uid)
        self.uid = generate_uid(self.node_type.value)
        get_registry().register(self.uid, self)
        
        # Clear signals
        self.signals.disconnect_all()
    
    def _cleanup(self) -> None:
        """Clean up node before returning to object pool.
        
        Called when releasing to pool. Removes from registry and clears state.
        """
        # Remove all children recursively
        for child in list(self.children):
            if hasattr(child, '_cleanup'):
                child._cleanup()
        self.children.clear()
        self._child_by_name.clear()
        self._tree_version += 1
        self._sort_dirty = True
        
        # Clear references
        self.parent = None
        self.properties.clear()
        self.script = None
        
        # Remove from UID registry
        get_registry().unregister(self.uid)
        
        # Disconnect all signals
        self.signals.disconnect_all()

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def __del__(self) -> None:
        """Release UID registration and disconnect all signals on GC."""
        try:
            get_registry().release(self.uid)
            self.signals.disconnect_all()
        except Exception:
            pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r} uid={self.uid}>"


# ---------------------------------------------------------------------------
# Node2D
# ---------------------------------------------------------------------------

class Node2D(Node):
    """A :class:`Node` extended with a 2-D transform, z-ordering, and tint.

    Attributes:
        transform: :class:`~engine.core.transform.Transform2D`.
        z_index:   Draw order within the same CanvasLayer (higher = on top).
        modulate:  RGBA tint applied to this node and its children.
    """

    # Additional slots for 2D properties
    __slots__ = ["transform", "z_index", "modulate", "y_sort_enabled"]

    def __init__(self, name: str = "Node2D") -> None:
        super().__init__(name, NodeType.NODE2D)
        self.transform: Transform2D = Transform2D()
        self.z_index: int = 0
        self.modulate: Tuple[int, int, int, int] = (255, 255, 255, 255)
        self.y_sort_enabled: bool = False

    # ------------------------------------------------------------------
    # Transform shortcuts
    # ------------------------------------------------------------------

    def set_position(self, x: float, y: float) -> None:
        self.transform.position = (x, y)  # type: ignore[assignment]
        if self.parent is not None:
            self.parent._sort_dirty = True

    def get_position(self) -> Tuple[float, float]:
        return self.transform.position  # type: ignore[return-value]

    @property
    def x(self) -> float:
        return self.transform.position[0]

    @x.setter
    def x(self, value: float) -> None:
        self.set_position(float(value), self.y)

    @property
    def y(self) -> float:
        return self.transform.position[1]

    @y.setter
    def y(self, value: float) -> None:
        self.set_position(self.x, float(value))

    def set_rotation(self, radians: float) -> None:
        self.transform.rotation = radians

    def get_rotation(self) -> float:
        return self.transform.rotation

    @property
    def rotation(self) -> float:
        return self.transform.rotation

    @rotation.setter
    def rotation(self, value: float) -> None:
        self.set_rotation(float(value))

    def set_scale(self, x: float, y: float) -> None:
        self.transform.scale = (x, y)  # type: ignore[assignment]

    def get_scale(self) -> Tuple[float, float]:
        return self.transform.scale  # type: ignore[return-value]

    @property
    def scale_x(self) -> float:
        return self.transform.scale[0]

    @scale_x.setter
    def scale_x(self, value: float) -> None:
        self.set_scale(float(value), self.scale_y)

    @property
    def scale_y(self) -> float:
        return self.transform.scale[1]

    @scale_y.setter
    def scale_y(self, value: float) -> None:
        self.set_scale(self.scale_x, float(value))

    @property
    def position(self) -> Tuple[float, float]:
        return self.get_position()

    @position.setter
    def position(self, value: Tuple[float, float]) -> None:
        self.set_position(float(value[0]), float(value[1]))

    @property
    def scale(self) -> Tuple[float, float]:
        return self.get_scale()

    @scale.setter
    def scale(self, value: Tuple[float, float]) -> None:
        self.set_scale(float(value[0]), float(value[1]))

    @property
    def position(self) -> Tuple[float, float]:
        """Proxy property for transform.position for ergonomic access."""
        return self.transform.position  # type: ignore[return-value]

    @position.setter
    def position(self, value: Tuple[float, float]) -> None:
        """Proxy property setter for transform.position."""
        self.transform.position = value  # type: ignore[assignment]

    def translate(self, dx: float, dy: float) -> None:
        x, y = self.get_position()
        self.set_position(x + dx, y + dy)

    def rotate(self, delta_radians: float) -> None:
        self.set_rotation(self.get_rotation() + delta_radians)

    # ------------------------------------------------------------------
    # Object Pooling Override
    # ------------------------------------------------------------------

    def _reset(self) -> None:
        """Reset including 2D properties."""
        super()._reset()
        
        # Reset transform
        self.transform.position = (0.0, 0.0)
        self.transform.rotation = 0.0
        self.transform.scale = (1.0, 1.0)
        
        # Reset other properties
        self.z_index = 0
        self.modulate = (255, 255, 255, 255)
        self.y_sort_enabled = False
    
    def _cleanup(self) -> None:
        """Cleanup including 2D properties."""
        super()._cleanup()
        # Transform will be reset on next acquire

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        data = self._to_dict_base()
        data["transform"] = {
            "position": list(self.transform.position),
            "rotation": self.transform.rotation,
            "scale":    list(self.transform.scale),
        }
        data["z_index"]  = self.z_index
        data["modulate"] = list(self.modulate)
        data["y_sort_enabled"] = self.y_sort_enabled
        return data


# ---------------------------------------------------------------------------
# Iterator helper
# ---------------------------------------------------------------------------

class NodeIterator:
    """Depth-first iterator over a node's subtree."""

    def __init__(self, root: Node, recursive: bool = False) -> None:
        self._stack: Deque[Node] = deque(root.children)
        self._recursive = recursive

    def __iter__(self) -> "NodeIterator":
        return self

    def __next__(self) -> Node:
        if not self._stack:
            raise StopIteration
        node = self._stack.popleft()
        if self._recursive:
            self._stack.extendleft(reversed(node.children))
        return node
