# /**************************************************************************/
# /*  godot_tscn.py                                                         */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple
import re

import logging


logger = logging.getLogger(__name__)



@dataclass
class GodotNodeDecl:
    name: str
    type: str
    parent: str | None = None
    props: Dict[str, Any] = None
    groups: List[str] = None
    signals: List[str] = None


def parse_tscn(text: str) -> Tuple[Dict[str, Any], List[GodotNodeDecl]]:
    """Parse Godot .tscn scene file.

    Supports:
    - [gd_scene ...] header
    - [node name="X" type="Y" parent=".."]
    - [group name="X"] groups
    - signal declarations
    - key = value pairs inside node blocks (parsed into Python values when possible)
    """
    header: Dict[str, Any] = {}
    nodes: List[GodotNodeDecl] = []
    groups: Dict[str, List[str]] = {}  # group name -> list of node paths

    current_node: GodotNodeDecl | None = None
    current_group: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith(";"):
            continue
        if line.startswith("[") and line.endswith("]"):
            if current_node is not None:
                nodes.append(current_node)
                current_node = None
            tag = line[1:-1].strip()
            if tag.startswith("gd_scene"):
                header["gd_scene"] = tag
            elif tag.startswith("node "):
                # naive attribute parsing
                attrs = _parse_attrs(tag[len("node ") :])
                current_node = GodotNodeDecl(
                    name=attrs.get("name", "Node"),
                    type=attrs.get("type", "Node"),
                    parent=attrs.get("parent"),
                    props={},
                    groups=[],
                    signals=[],
                )
            elif tag.startswith("group "):
                # Parse group: [group name="GroupName"]
                attrs = _parse_attrs(tag[len("group ") :])
                current_group = attrs.get("name")
                if current_group:
                    groups[current_group] = []
            continue
        if "=" in line and current_node is not None:
            k, v = line.split("=", 1)
            key = k.strip()
            value = parse_godot_value(v.strip())
            
            # Check for signal declarations
            if key == "signal":
                if isinstance(value, str):
                    current_node.signals.append(value)
                elif isinstance(value, list):
                    current_node.signals.extend(value)
            else:
                current_node.props[key] = value
    if current_node is not None:
        nodes.append(current_node)

    # Assign groups to nodes based on their paths
    for node in nodes:
        node_path = node.name if not node.parent else f"{node.parent}/{node.name}"
        for group_name, group_nodes in groups.items():
            if node_path in group_nodes:
                node.groups.append(group_name)

    header["groups"] = groups
    return header, nodes


def dump_tscn(nodes: List[GodotNodeDecl]) -> str:
    out: List[str] = ['[gd_scene load_steps=2 format=3]']
    out.append("")
    for n in nodes:
        parts = [f'name="{n.name}"', f'type="{n.type}"']
        if n.parent is not None:
            parts.append(f'parent="{n.parent}"')
        out.append("[node " + " ".join(parts) + "]")
        if n.props:
            for k, v in n.props.items():
                out.append(f"{k} = {dump_godot_value(v)}")
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def _parse_attrs(attr_str: str) -> Dict[str, str]:
    # parse key="value" tokens
    attrs: Dict[str, str] = {}
    i = 0
    s = attr_str.strip()
    while i < len(s):
        while i < len(s) and s[i].isspace():
            i += 1
        if i >= len(s):
            break
        # key
        j = i
        while j < len(s) and s[j] not in " =":
            j += 1
        key = s[i:j]
        i = j
        while i < len(s) and s[i].isspace():
            i += 1
        if i < len(s) and s[i] == "=":
            i += 1
        while i < len(s) and s[i].isspace():
            i += 1
        if i < len(s) and s[i] == '"':
            i += 1
            j = i
            while j < len(s) and s[j] != '"':
                j += 1
            attrs[key] = s[i:j]
            i = j + 1
        else:
            # fallback token
            j = i
            while j < len(s) and not s[j].isspace():
                j += 1
            attrs[key] = s[i:j]
            i = j
    return attrs


def parse_godot_value(raw: str) -> Any:
    if raw.startswith('"') and raw.endswith('"'):
        return raw[1:-1]
    if raw in {"true", "false"}:
        return raw == "true"
    # int / float
    try:
        if "." in raw:
            return float(raw)
        return int(raw)
    except ValueError:
        pass
    # Vector2(x, y)
    m = re.match(r"Vector2\(([^,]+),\s*([^)]+)\)", raw)
    if m:
        try:
            return {"__type__": "Vector2", "x": float(m.group(1)), "y": float(m.group(2))}
        except ValueError:
            return raw
    # PackedByteArray("...") - tile data
    m = re.match(r'PackedByteArray\("([^"]*)"\)', raw)
    if m:
        return {"__type__": "PackedByteArray", "data": m.group(1)}
    return raw


def dump_godot_value(value: Any) -> str:
    if isinstance(value, str):
        return f'"{value}"'
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, dict) and value.get("__type__") == "Vector2":
        return f'Vector2({value.get("x", 0)}, {value.get("y", 0)})'
    return str(value)

