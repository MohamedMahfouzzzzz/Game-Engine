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

Godot 4.6 parity additions
---------------------------
* ``unique_name``  — optional pin that lets you address this node via
  ``%UniqueName`` syntax in scene paths, stable across renames/reparents.
* ``get_node(path)`` — scene-path resolver supporting ``%UniqueName`` shortcut,
  absolute paths (leading ``/``), and relative dot-notation (``../Sibling``).
* ``find_node_by_uid(uid)`` — O(1) lookup delegated to the global registry.
* ``_SIGNALS`` list accepted by SignalBus for forward-declared signals.
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


class Node:
    __slots__ = [
        "uid", "name", "unique_name", "node_type", "parent", "children",
        "properties", "enabled", "processing", "visible", "script", "signals",
        "_child_by_name", "_tree_version", "_sort_dirty", "_scene_root",
        "__weakref__"
    ]

    _SIGNALS: List[str] = []

    def __init__(self, name: str = "Node", node_type: NodeType = NodeType.NODE) -> None:
        self.uid: str = generate_uid(node_type.value)
        self.name: str = name
        self.unique_name: Optional[str] = None
        self.node_type: NodeType = node_type
        self.parent: Optional["Node"] = None
        self.children: List["Node"] = []
        self._child_by_name: Dict[str, List["Node"]] = {}
        self._tree_version: int = 0
        self._sort_dirty: bool = True
        self._scene_root: Optional["Node"] = None
        self.properties: Dict[str, Any] = {}
        self.enabled: bool = True
        self.processing: bool = True
        self.visible: bool = True
        self.script: Optional[str] = None
        self.signals: SignalBus = SignalBus()
        get_registry().register(self.uid, self)
        logger.debug("Node '%s' created with uid %s", name, self.uid)

    def set_unique_name(self, unique_name: Optional[str]) -> None:
        old = self.unique_name
        self.unique_name = unique_name
        reg = get_registry()
        if old:
            reg.unregister_unique_name(old)
        if unique_name:
            reg.register_unique_name(unique_name, self)

    def get_node(self, path: str) -> Optional["Node"]:
        if not path:
            return self
        if path.startswith("%"):
            rest_parts = path[1:].split("/", 1)
            alias = rest_parts[0]
            node = get_registry().lookup_unique_name(alias)
            if node is None:
                return None
            if len(rest_parts) == 2:
                return node.get_node(rest_parts[1])
            return node
        if path.startswith("/"):
            root = self._get_tree_root()
            return root.get_node(path.lstrip("/")) if root else None
        parts = path.split("/")
        current: Optional["Node"] = self
        for part in parts:
            if current is None:
                return None
            if part == ".":
                continue
            elif part == "..":
                current = current.parent
            else:
                current = current.get_child(part)
        return current

    def _get_tree_root(self) -> Optional["Node"]:
        node: Optional["Node"] = self
        while node is not None and node.parent is not None:
            node = node.parent
        return node

    @staticmethod
    def find_node_by_uid(uid: str) -> Optional["Node"]:
        obj = get_registry().lookup(uid)
        return obj if isinstance(obj, Node) else None

    def add_child(self, child: "Node") -> None:
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
        child._scene_root = self._scene_root or (self if self.parent is None else None)
        self.children.append(child)
        self._child_by_name.setdefault(child.name, []).append(child)
        self._tree_version += 1
        self._sort_dirty = True
        logger.debug("Node '%s' added as child to '%s'", child.name, self.name)

    def remove_child(self, child: "Node") -> None:
        if child in self.children:
            self.children.remove(child)
            bucket = self._child_by_name.get(child.name)
            if bucket and child in bucket:
                bucket.remove(child)
                if not bucket:
                    self._child_by_name.pop(child.name, None)
            child.parent = None
            child._scene_root = None
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
        bucket = self._child_by_name.get(name)
        return bucket[0] if bucket else default

    def find_child(self, name: str, recursive: bool = True) -> Optional["Node"]:
        for child in self.children:
            if child.name == name:
                return child
            if recursive:
                found = child.find_child(name, recursive=True)
                if found is not None:
                    return found
        return None

    def get_path(self) -> str:
        parts: List[str] = [self.name]
        node: Optional["Node"] = self.parent
        while node is not None:
            parts.append(node.name)
            node = node.parent
        return "/".join(reversed(parts))

    def iter_children(self, recursive: bool = False) -> "NodeIterator":
        return NodeIterator(self, recursive=recursive)

    def set_property(self, key: str, value: Any) -> None:
        self.properties[key] = value

    def get_property(self, key: str, default: Any = None) -> Any:
        return self.properties.get(key, default)

    def has_property(self, key: str) -> bool:
        return key in self.properties

    def connect(self, signal: str, callback: Any) -> None:
        self.signals.connect(signal, callback)

    def disconnect(self, signal: str, callback: Any) -> None:
        self.signals.disconnect(signal, callback)

    def emit(self, signal: str, *args: Any, **kwargs: Any) -> None:
        self.signals.emit(signal, *args, **kwargs)

    def _to_dict_base(self) -> Dict[str, Any]:
        return {
            "uid":         self.uid,
            "name":        self.name,
            "unique_name": self.unique_name,
            "type":        self.node_type.value,
            "enabled":     self.enabled,
            "visible":     self.visible,
            "script":      self.script,
            "properties":  self.properties,
            "children":    [child.to_dict() for child in self.children],
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
        saved_uid = data.get("uid")
        if saved_uid:
            node.uid = saved_uid
            get_registry().register(saved_uid, node)
        node.enabled    = data.get("enabled", True)
        node.visible    = data.get("visible", True)
        node.script     = data.get("script")
        node.properties = data.get("properties", {})
        saved_unique = data.get("unique_name")
        if saved_unique:
            node.set_unique_name(saved_unique)
        if isinstance(node, Node2D):
            td = data.get("transform", {})
            node.transform.position = tuple(td.get("position", (0.0, 0.0)))  # type: ignore[assignment]
            node.transform.rotation = float(td.get("rotation", 0.0))
            node.transform.scale    = tuple(td.get("scale", (1.0, 1.0)))     # type: ignore[assignment]
            node.z_index            = int(data.get("z_index", 0))
            node.modulate           = tuple(data.get("modulate", (255, 255, 255, 255)))  # type: ignore[assignment]
            node.y_sort_enabled     = bool(data.get("y_sort_enabled", False))
        for child_data in data.get("children", []):
            node.add_child(Node.from_dict(child_data))
        return node

    def _reset(self) -> None:
        if self.unique_name:
            get_registry().unregister_unique_name(self.unique_name)
            self.unique_name = None
        self.children.clear()
        self._child_by_name.clear()
        self._tree_version += 1
        self._sort_dirty = True
        self.properties.clear()
        self.enabled = True
        self.processing = True
        self.visible = True
        self.script = None
        self.parent = None
        self._scene_root = None
        get_registry().unregister(self.uid)
        self.uid = generate_uid(self.node_type.value)
        get_registry().register(self.uid, self)
        self.signals.disconnect_all()

    def _cleanup(self) -> None:
        for child in list(self.children):
            if hasattr(child, '_cleanup'):
                child._cleanup()
        self.children.clear()
        self._child_by_name.clear()
        self._tree_version += 1
        self._sort_dirty = True
        self.parent = None
        self._scene_root = None
        self.properties.clear()
        self.script = None
        if self.unique_name:
            get_registry().unregister_unique_name(self.unique_name)
            self.unique_name = None
        get_registry().unregister(self.uid)
        self.signals.disconnect_all()

    def __del__(self) -> None:
        try:
            if self.unique_name:
                get_registry().unregister_unique_name(self.unique_name)
            get_registry().release(self.uid)
            self.signals.disconnect_all()
        except Exception:
            pass

    def __repr__(self) -> str:
        pin = f" %{self.unique_name}" if self.unique_name else ""
        return f"<{self.__class__.__name__} name={self.name!r} uid={self.uid}{pin}>"


class Node2D(Node):
    __slots__ = ["transform", "z_index", "modulate", "y_sort_enabled"]

    def __init__(self, name: str = "Node2D") -> None:
        super().__init__(name, NodeType.NODE2D)
        self.transform: Transform2D = Transform2D()
        self.z_index: int = 0
        self.modulate: Tuple[int, int, int, int] = (255, 255, 255, 255)
        self.y_sort_enabled: bool = False

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
        return self.transform.position  # type: ignore[return-value]

    @position.setter
    def position(self, value: Tuple[float, float]) -> None:
        self.transform.position = value  # type: ignore[assignment]

    @property
    def scale(self) -> Tuple[float, float]:
        return self.get_scale()

    @scale.setter
    def scale(self, value: Tuple[float, float]) -> None:
        self.set_scale(float(value[0]), float(value[1]))

    def translate(self, dx: float, dy: float) -> None:
        x, y = self.get_position()
        self.set_position(x + dx, y + dy)

    def rotate(self, delta_radians: float) -> None:
        self.set_rotation(self.get_rotation() + delta_radians)

    def _reset(self) -> None:
        super()._reset()
        self.transform.position = (0.0, 0.0)
        self.transform.rotation = 0.0
        self.transform.scale = (1.0, 1.0)
        self.z_index = 0
        self.modulate = (255, 255, 255, 255)
        self.y_sort_enabled = False

    def _cleanup(self) -> None:
        super()._cleanup()

    def to_dict(self) -> Dict[str, Any]:
        data = self._to_dict_base()
        data["transform"] = {
            "position": list(self.transform.position),
            "rotation": self.transform.rotation,
            "scale":    list(self.transform.scale),
        }
        data["z_index"]         = self.z_index
        data["modulate"]        = list(self.modulate)
        data["y_sort_enabled"]  = self.y_sort_enabled
        return data


class NodeIterator:
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
