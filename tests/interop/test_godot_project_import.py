# /**************************************************************************/
# /*  test_godot_project_import.py                                          */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.interop.godot_importer import GodotImporter
from engine.core.node_base import Node2D


class TestGodotProjectImport(unittest.TestCase):
    def test_import_full_project_godot(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "scenes"), exist_ok=True)
            project_file = os.path.join(d, "project.godot")
            main_tscn = os.path.join(d, "scenes", "main.tscn")
            ui_tscn = os.path.join(d, "scenes", "ui.tscn")

            with open(project_file, "w", encoding="utf-8") as f:
                f.write(
                    '[application]\n'
                    'config/name="Demo2D"\n'
                    'run/main_scene="res://scenes/main.tscn"\n'
                )

            with open(main_tscn, "w", encoding="utf-8") as f:
                f.write(
                    '[gd_scene load_steps=2 format=3]\n\n'
                    '[node name="Main" type="Node2D"]\n'
                    'position = Vector2(10, 20)\n'
                    '[node name="Player" type="Node2D" parent="."]\n'
                    'position = Vector2(50, 60)\n'
                )

            with open(ui_tscn, "w", encoding="utf-8") as f:
                f.write(
                    '[gd_scene load_steps=2 format=3]\n\n'
                    '[node name="UI" type="Node2D"]\n'
                    '[node name="LabelA" type="Label" parent="."]\n'
                )

            p = GodotImporter().import_project(project_file)
            self.assertEqual(p.name, "Demo2D")
            self.assertGreaterEqual(len(p.scenes), 2)
            self.assertIsNotNone(p.active_scene)
            self.assertEqual(p.active_scene.name, "main")
            self.assertIn("godot_import", p.assets)
            player = p.active_scene.root.find_child("Player")
            self.assertIsNotNone(player)
            self.assertIsInstance(player, Node2D)
            self.assertEqual(player.get_position(), (50.0, 60.0))
            self.assertIn("warnings", p.assets["godot_import"])

    def test_missing_parent_fallback_and_report(self):
        with tempfile.TemporaryDirectory() as d:
            tscn = os.path.join(d, "broken_parent.tscn")
            with open(tscn, "w", encoding="utf-8") as f:
                f.write(
                    '[gd_scene load_steps=2 format=3]\n\n'
                    '[node name="Main" type="Node2D"]\n'
                    '[node name="A" type="Node2D" parent="NotExists"]\n'
                    'unknown_property = 123\n'
                )
            p = GodotImporter().import_project(tscn)
            report = p.active_scene.root.get_property("interop_report")
            self.assertIn("NotExists", report["unresolved_parent_paths"])
            self.assertTrue(any("unmapped_property:unknown_property" == w for w in report["property_warnings"]))

    def test_skip_3d_node_types(self):
        with tempfile.TemporaryDirectory() as d:
            tscn = os.path.join(d, "mixed.tscn")
            with open(tscn, "w", encoding="utf-8") as f:
                f.write(
                    '[gd_scene load_steps=2 format=3]\n\n'
                    '[node name="Root" type="Node2D"]\n'
                    '[node name="MeshA" type="MeshInstance3D" parent="."]\n'
                    '[node name="Hud" type="Node2D" parent="."]\n'
                )
            p = GodotImporter().import_project(tscn)
            report = p.active_scene.root.get_property("interop_report")
            self.assertIn("MeshInstance3D", report["skipped_3d_node_types"])
            self.assertIsNotNone(p.active_scene.root.find_child("Hud"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
