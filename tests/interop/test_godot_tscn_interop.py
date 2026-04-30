# /**************************************************************************/
# /*  test_godot_tscn_interop.py                                            */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

import os
import sys
import unittest
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.core.project import Project
from engine.core.node import Node2D
from engine.interop.godot_exporter import GodotExporter
from engine.interop.godot_importer import GodotImporter


class TestGodotTscnInterop(unittest.TestCase):
    def test_export_import_tscn(self):
        p = Project("G")
        s = p.create_scene("Main")
        player = Node2D("Player")
        player.set_position(10, 20)
        weapon = Node2D("Weapon")
        weapon.set_position(2, 3)
        player.add_child(weapon)
        s.add_node(player)
        exporter = GodotExporter()
        importer = GodotImporter()
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "main.tscn")
            exporter.export_project(p, path)
            self.assertTrue(os.path.exists(path + ".report.json"))
            p2 = importer.import_project(path)
            self.assertIsNotNone(p2.active_scene)
            p2_player = p2.active_scene.root.find_child("Player")
            p2_weapon = p2.active_scene.root.find_child("Weapon")
            self.assertIsNotNone(p2_player)
            self.assertIsNotNone(p2_weapon)
            self.assertEqual(p2_player.get_position(), (10.0, 20.0))
            self.assertEqual(p2_weapon.get_position(), (2.0, 3.0))


if __name__ == "__main__":
    unittest.main(verbosity=2)

