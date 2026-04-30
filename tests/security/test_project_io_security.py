# /**************************************************************************/
# /*  test_security_project_io.py                                           */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

import os
import sys
import unittest
import json
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.core.project import Project
from ui.actions.project_io import load_project, save_project


class TestProjectIOSecurity(unittest.TestCase):
    def test_reject_wrong_extension(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "x.txt")
            with open(p, "w", encoding="utf-8") as f:
                f.write("{}")
            with self.assertRaises(ValueError):
                load_project(p)

    def test_atomic_save_and_load(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "proj.Game")
            proj = Project("SecProj")
            proj.create_scene("S1")
            save_project(path, proj)
            loaded = load_project(path)
            self.assertEqual(loaded.name, "SecProj")

    def test_reject_huge_scene_nodes(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "bad.Game")
            root = {"id": "r", "name": "Root", "type": "Node", "enabled": True, "visible": True, "properties": {}, "children": []}
            # build wide tree beyond cap to avoid recursion limits when encoding JSON
            for i in range(21000):
                child = {"id": f"c{i}", "name": f"C{i}", "type": "Node", "enabled": True, "visible": True, "properties": {}, "children": []}
                root["children"].append(child)
            data = {"version": 1, "name": "Bad", "scenes": {"s1": {"id": "s1", "name": "S1", "root": root}}}
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f)
            with self.assertRaises(ValueError):
                load_project(path)


if __name__ == "__main__":
    unittest.main(verbosity=2)

