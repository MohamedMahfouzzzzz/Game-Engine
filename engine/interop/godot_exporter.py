# /**************************************************************************/
# /*  godot_exporter.py                                                     */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

from typing import Dict, Any
import json
from pathlib import Path

from engine.core.node_base import Node, Node2D
from engine.core.project_secure import SecureProject as Project
from engine.interop.mapping_registry import MappingRegistry
from engine.interop.godot_tscn import GodotNodeDecl, dump_tscn

import logging


logger = logging.getLogger(__name__)



class GodotExporter:
    def __init__(self, registry: MappingRegistry | None = None) -> None:
        self.registry = registry or MappingRegistry()

    def export_project(self, project: Project, output_path: str) -> str:
        if output_path.lower().endswith(".tscn"):
            scene = project.active_scene
            if not scene:
                raise ValueError("Project has no active scene.")
            decls = self._collect_tscn_decls(scene.root)
            text = dump_tscn(decls)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)
            self._write_report(output_path, project, format_name="tscn", exported_nodes=len(decls))
            return output_path

        payload: Dict[str, Any] = {
            "config": {"name": project.name},
            "compatibility": self.registry.compatibility_report(),
            "project": project.to_dict(),
        }
        with open(output_path, "w", encoding="utf-8") as file_handle:
            json.dump(payload, file_handle, indent=2)
        exported_nodes = len(project.active_scene.root.children) + 1 if project.active_scene else 0
        self._write_report(output_path, project, format_name="json", exported_nodes=exported_nodes)
        return output_path

    def _write_report(self, output_path: str, project: Project, format_name: str, exported_nodes: int) -> None:
        report = {
            "project": project.name,
            "format": format_name,
            "exported_nodes": exported_nodes,
            "compatibility": self.registry.compatibility_report(),
        }
        sidecar = Path(output_path).with_suffix(Path(output_path).suffix + ".report.json")
        sidecar.write_text(json.dumps(report, indent=2), encoding="utf-8")

    def _collect_tscn_decls(self, root: Node) -> list[GodotNodeDecl]:
        decls: list[GodotNodeDecl] = [GodotNodeDecl(name=root.name, type=self._node_type_name(root), parent=None, props=self._node_props(root))]

        def walk(node: Node, parent_path: str) -> None:
            for child in node.children:
                child_path = child.name if parent_path == "." else f"{parent_path}/{child.name}"
                decls.append(
                    GodotNodeDecl(
                        name=child.name,
                        type=self._node_type_name(child),
                        parent=parent_path,
                        props=self._node_props(child),
                    )
                )
                walk(child, child_path)

        walk(root, ".")
        return decls

    def _node_type_name(self, node: Node) -> str:
        return getattr(getattr(node, "node_type", None), "value", "Node")

    def _node_props(self, node: Node) -> Dict[str, Any]:
        props: Dict[str, Any] = {}
        if isinstance(node, Node2D):
            x, y = node.get_position()
            sx, sy = node.get_scale()
            props["position"] = {"__type__": "Vector2", "x": x, "y": y}
            props["rotation"] = node.get_rotation()
            props["scale"] = {"__type__": "Vector2", "x": sx, "y": sy}
            props["z_index"] = node.z_index
            props["visible"] = node.visible
        return props
