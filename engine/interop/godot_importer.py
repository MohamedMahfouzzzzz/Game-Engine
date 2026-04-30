# /**************************************************************************/
# /*  godot_importer.py                                                     */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

from typing import Any, Dict, List, Tuple
import json
import shutil
from pathlib import Path

from engine.core.errors import InteropError, ValidationError
from engine.core.node_base import Node, Node2D
from engine.core.project_secure import SecureProject as Project
from engine.interop.mapping_registry import MappingRegistry
from engine.interop.godot_tscn import parse_tscn

import logging


logger = logging.getLogger(__name__)



class GodotImporter:
    def __init__(self, registry: MappingRegistry | None = None) -> None:
        self.registry = registry or MappingRegistry()

    def import_project(self, path: str) -> Project:
        path_obj = Path(path)
        if not path_obj.exists():
            raise ValidationError(f"External project path does not exist: {path}")
        if path_obj.name == "project.godot":
            return self._import_godot_project_file(path_obj)
        if path.lower().endswith(".tscn"):
            project = Project(path_obj.stem or "ImportedGodotProject")
            scene, report = self._import_single_tscn(path_obj)
            project.add_scene(scene)
            project.active_scene = scene
            scene.root.set_property("interop_report", report)

            # Copy assets from Godot project to local assets folder
            godot_root = path_obj.parent
            copied = self._copy_assets_to_project(godot_root, Path.cwd())
            if copied:
                scene.root.set_property("copied_assets", copied)
                print(f"Copied {len(copied)} asset files to local project")

            # Update texture paths to point to local assets
            self._update_texture_paths_to_local(scene, Path.cwd())

            # Connect signals to engine signal system
            self._connect_signals(scene)

            # Auto-convert GDScript files in the project
            project_root = path_obj.parent
            converted = self.convert_gdscript_in_project(project_root)
            if converted:
                scene.root.set_property("converted_scripts", converted)
                print(f"Converted {len(converted)} GDScript files to Python")

            return project

        with open(path, "r", encoding="utf-8") as file_handle:
            data: Dict[str, Any] = json.load(file_handle)
        project_name = data.get("config", {}).get("name", "ImportedProject")
        project = Project(project_name)
        scene = project.create_scene("Main")
        scene.root.set_property("external_source", path)
        scene.root.set_property(
            "interop_report",
            {
                "source_format": "json",
                "compatibility": data.get("compatibility", {}),
            },
        )
        return project

    def _import_godot_project_file(self, project_file: Path) -> Project:
        config = self._parse_project_godot(project_file.read_text(encoding="utf-8"))
        project_name = config.get("application/config/name", project_file.parent.name or "ImportedGodotProject")
        project = Project(project_name)

        scene_files = sorted(project_file.parent.rglob("*.tscn"))
        import_reports: List[Dict[str, Any]] = []
        scene_by_relpath: Dict[str, str] = {}
        used_scene_names: Dict[str, int] = {}
        for sf in scene_files:
            scene, report = self._import_single_tscn(sf)
            scene.name = self._unique_scene_name(scene.name, used_scene_names)
            project.add_scene(scene)
            scene_by_relpath[sf.relative_to(project_file.parent).as_posix()] = scene.id
            import_reports.append(report)

        main_scene_ref = config.get("application/run/main_scene", "")
        main_scene_rel = main_scene_ref.replace("res://", "")
        if main_scene_rel in scene_by_relpath:
            project.active_scene = project.scenes[scene_by_relpath[main_scene_rel]]
        elif project.scenes:
            project.active_scene = next(iter(project.scenes.values()))

        import_info = {
            "source_project_file": str(project_file),
            "scene_count": len(scene_files),
            "reports": import_reports,
            "warnings": self._collect_project_warnings(import_reports),
        }
        project.assets["external_import"] = import_info
        project.assets["godot_import"] = import_info
        return project

    def _import_single_tscn(self, path: Path):
        text = path.read_text(encoding="utf-8")
        header, node_decls = parse_tscn(text)
        if not node_decls:
            raise InteropError(f"No nodes found in scene: {path}")

        scene = Project(path.stem).create_scene(path.stem)
        scene.root.name = path.stem
        scene.root.set_property("external_source", str(path))

        # Store groups and signals from header
        if "groups" in header:
            scene.root.set_property("external_groups", header["groups"])

        path_to_node: Dict[str, Node] = {".": scene.root}
        unsupported_nodes: List[str] = []
        skipped_3d_nodes: List[str] = []
        unresolved_parents: List[str] = []
        property_warnings: List[str] = []
        imported_nodes = 0
        supported_types = set(self.registry.node_type_map.keys())
        project_root = path.parent  # Godot project root

        # First pass: create nodes
        for decl in node_decls:
            if decl.parent is None:
                scene.root.name = decl.name or scene.root.name
                continue
            parent = path_to_node.get(decl.parent)
            if parent is None:
                parent = scene.root
                unresolved_parents.append(decl.parent or "<none>")
            if self._is_3d_node_type(decl.type):
                skipped_3d_nodes.append(decl.type)
                continue
            created = self._create_node_from_decl(decl.type, decl.name)
            if decl.type not in supported_types:
                unsupported_nodes.append(decl.type)
            scene.add_node(created, parent=parent)
            node_path = self._child_path(decl.parent, decl.name)
            node_path = self._ensure_unique_path(path_to_node, node_path)
            path_to_node[node_path] = created
            imported_nodes += 1
            prop_warns = self._apply_decl_properties(created, decl.props, project_root)
            property_warnings.extend(prop_warns)

            # Store groups and signals on the node
            if decl.groups:
                created.set_property("groups", decl.groups)
            if decl.signals:
                created.set_property("signals", decl.signals)

        report = {
            "scene_file": str(path),
            "source_format": "tscn",
            "imported_nodes": imported_nodes,
            "unsupported_node_types": sorted(set(unsupported_nodes)),
            "skipped_3d_node_types": sorted(set(skipped_3d_nodes)),
            "unresolved_parent_paths": sorted(set(unresolved_parents)),
            "property_warnings": property_warnings[:1000],
            "groups_count": len(header.get("groups", {})),
            "signals_count": sum(len(decl.signals or []) for decl in node_decls),
        }
        return scene, report

    def _create_node_from_decl(self, node_type: str, name: str) -> Node:
        from engine.core.nodes import Sprite, TileMap, Button, Label, Control, Panel

        # UI Controls
        if node_type == "Button":
            return Button(name)
        if node_type == "Label":
            return Label(name)
        if node_type == "Control":
            return Control(name)
        if node_type == "Panel":
            return Panel(name)
        if node_type in {"LineEdit", "TextEdit", "CheckBox", "ProgressBar", "Slider", "SpinBox", "OptionButton"}:
            # Fallback to Control for unsupported UI nodes
            return Control(name)

        # 2D Nodes
        if node_type == "Sprite2D":
            return Sprite(name)
        if node_type == "AnimatedSprite2D":
            return Sprite(name)  # Fallback to Sprite
        if node_type in {"TileMap", "TileMapLayer"}:
            return TileMap(name)
        if node_type in {"AnimationPlayer", "Tween"}:
            return Node(name)
        if node_type in {"Node2D", "Camera2D", "Light2D", "Area2D", "StaticBody2D", "RigidBody2D", "CharacterBody2D", "CollisionShape2D", "CollisionPolygon2D", "NavigationRegion2D", "Path2D", "PathFollow2D", "RayCast2D", "VisibilityNotifier2D"}:
            return Node2D(name)

        # Fallback to generic Node for unsupported types
        return Node(name)

    def _apply_decl_properties(self, node: Node, props: Dict[str, Any], project_root: Path) -> List[str]:
        warnings: List[str] = []

        # Import node types for specific handling
        from engine.core.nodes import Sprite, TileMap, Button, Label

        for key, value in props.items():
            # Convert res:// paths to absolute paths
            if isinstance(value, str) and value.startswith("res://"):
                value = str(project_root / value.replace("res://", ""))

            # Sprite-specific properties
            if isinstance(node, Sprite):
                if key in ("texture", "texture_path") and value:
                    node.texture_path = str(value)
                    continue
                if key in ("flip_h", "flip_h_horizontal") and isinstance(value, bool):
                    node.flip_h = value
                    continue
                if key in ("flip_v", "flip_v_vertical") and isinstance(value, bool):
                    node.flip_v = value
                    continue
                if key == "centered" and isinstance(value, bool):
                    node.centered = value
                    continue
                if key == "offset" and isinstance(value, dict) and value.get("__type__") == "Vector2":
                    node.offset = (float(value["x"]), float(value["y"]))
                    continue

            # TileMap-specific properties
            if isinstance(node, TileMap):
                if key == "tile_set" and value:
                    node.set_property("tile_set", value)
                    continue
                if key == "format" and isinstance(value, int):
                    node.format = value
                    continue
                if key == "tile_map_data" and value:
                    if isinstance(value, dict) and value.get("__type__") == "PackedByteArray":
                        node.set_property("tile_map_data", value.get("data"))
                    else:
                        node.set_property("tile_map_data", str(value))
                    continue
                # TileMap also needs position
                if key == "position" and isinstance(value, dict) and value.get("__type__") == "Vector2":
                    if isinstance(node, Node2D):
                        node.set_position(float(value["x"]), float(value["y"]))
                    continue

            # Button-specific properties
            if isinstance(node, Button):
                if key == "text" and value:
                    node.text = str(value)
                    continue
                if key == "disabled" and isinstance(value, bool):
                    node.disabled = value
                    continue

            # Label-specific properties
            if isinstance(node, Label):
                if key == "text" and value:
                    node.text = str(value)
                    continue
                if key == "font_size" and isinstance(value, (int, float)):
                    node.font_size = int(value)
                    continue
                if key == "align" and value:
                    node.align = str(value)
                    continue

            if isinstance(node, Node2D):
                if key == "position" and isinstance(value, dict) and value.get("__type__") == "Vector2":
                    node.set_position(float(value["x"]), float(value["y"]))
                    continue
                if key == "rotation" and isinstance(value, (int, float)):
                    node.set_rotation(float(value))
                    continue
                if key == "scale" and isinstance(value, dict) and value.get("__type__") == "Vector2":
                    node.set_scale(float(value["x"]), float(value["y"]))
                    continue
                if key == "z_index" and isinstance(value, (int, float)):
                    node.z_index = int(value)
                    continue
                if key == "visible" and isinstance(value, bool):
                    node.visible = value
                    continue
            if node.node_type.value == "Node" and key in {
                "autoplay", "libraries", "playback_process_mode", "speed_scale",
                "active", "paused", "loops", "duration", "trans", "ease",
            }:
                node.set_property(key, value)
                continue
            node.set_property(f"external:{key}", value)
            if key not in self.registry.property_map:
                warnings.append(f"unmapped_property:{key}")
        return warnings

    def _parse_project_godot(self, text: str) -> Dict[str, str]:
        section = ""
        out: Dict[str, str] = {}
        for raw in text.splitlines():
            line = raw.strip()
            if not line or line.startswith(";"):
                continue
            if line.startswith("[") and line.endswith("]"):
                section = line[1:-1].strip()
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                out[f"{section}/{k.strip()}"] = v.strip().strip('"')
        return out

    def _child_path(self, parent: str, name: str) -> str:
        if parent in {"", "."}:
            return name
        return f"{parent}/{name}"

    def _ensure_unique_path(self, path_to_node: Dict[str, Node], base_path: str) -> str:
        if base_path not in path_to_node:
            return base_path
        i = 1
        while f"{base_path}#{i}" in path_to_node:
            i += 1
        return f"{base_path}#{i}"

    def _is_3d_node_type(self, node_type: str) -> bool:
        return node_type.endswith("3D") or node_type in {"Node3D", "Camera3D", "MeshInstance3D"}

    def _unique_scene_name(self, base_name: str, used: Dict[str, int]) -> str:
        if base_name not in used:
            used[base_name] = 0
            return base_name
        used[base_name] += 1
        return f"{base_name}_{used[base_name]}"

    def _collect_project_warnings(self, reports: List[Dict[str, Any]]) -> List[str]:
        out: List[str] = []
        for r in reports:
            if r.get("skipped_3d_node_types"):
                out.append(f"{r.get('scene_file')}:skipped_3d={','.join(r['skipped_3d_node_types'])}")
            if r.get("unresolved_parent_paths"):
                out.append(f"{r.get('scene_file')}:unresolved_parents={len(r['unresolved_parent_paths'])}")
            if r.get("property_warnings"):
                out.append(f"{r.get('scene_file')}:unmapped_props={len(r['property_warnings'])}")
        return out
    
    def convert_gdscript_in_project(self, project_path: Path) -> Dict[str, str]:
        """Find and convert all .gd files in project to Python."""
        from engine.interop.gdscript_converter import convert_gdscript_in_project
        return convert_gdscript_in_project(project_path)

    def _copy_assets_to_project(self, godot_project_root: Path, target_project_root: Path) -> List[str]:
        """Copy texture and image assets from Godot project to engine project."""
        copied_files = []
        asset_extensions = {".png", ".jpg", ".jpeg", ".svg", ".webp", ".tga", ".bmp"}

        # Find all asset files in Godot project
        for asset_file in godot_project_root.rglob("*"):
            if asset_file.suffix.lower() in asset_extensions:
                # Calculate relative path from Godot project root
                rel_path = asset_file.relative_to(godot_project_root)

                # Create target path in engine project Game Files folder
                target_dir = target_project_root / "Game Files" / rel_path.parent
                target_dir.mkdir(parents=True, exist_ok=True)
                target_file = target_dir / asset_file.name

                # Copy file
                if not target_file.exists():
                    try:
                        shutil.copy2(asset_file, target_file)
                        copied_files.append(str(target_file))
                    except Exception as e:
                        print(f"Failed to copy {asset_file}: {e}")

        return copied_files

    def _update_texture_paths_to_local(self, scene, project_root: Path) -> None:
        """Update all texture paths to point to local Game Files folder."""
        from engine.core.nodes import Sprite

        def update_node(node):
            if isinstance(node, Sprite):
                if hasattr(node, 'texture_path') and node.texture_path:
                    old_path = Path(node.texture_path)
                    filename = old_path.name
                    # Store as relative path from Game Files folder
                    # The viewport will resolve this with project_root
                    node.texture_path = f"Game Files/{filename}"

            # Recursively update children
            for child in node.children:
                update_node(child)

        update_node(scene.root)

    def _connect_signals(self, scene) -> None:
        """Connect signals from imported nodes to engine signal system."""
        from engine.core.signals import SignalBus

        def connect_node_signals(node):
            # Get signals stored as properties
            signals = node.get_property("signals", [])
            if signals:
                for signal_name in signals:
                    # Register signal with SignalBus
                    if hasattr(SignalBus, 'register_signal'):
                        SignalBus.register_signal(node.uid, signal_name)

            # Recursively connect children
            for child in node.children:
                connect_node_signals(child)

        connect_node_signals(scene.root)
