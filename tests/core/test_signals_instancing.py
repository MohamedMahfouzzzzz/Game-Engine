# /**************************************************************************/
# /*  test_signals_instancing_resources.py                                  */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.core.instancing import instance_scene
from engine.core.node import Node, Project, Scene


class TestPhase4Features(unittest.TestCase):
    def test_signals(self):
        n = Node("N")
        called = {"x": 0}

        def cb(v):
            called["x"] += v

        n.connect("hit", cb)
        n.emit("hit", 2)
        self.assertEqual(called["x"], 2)

    def test_instancing_metadata(self):
        p = Project("P")
        a = p.create_scene("A")
        b = p.create_scene("B")
        inst = instance_scene(a, b, "I")
        self.assertEqual(inst.get_property("instance_of_scene_name"), "B")

    def test_resource_manager_source(self):
        p = Project("P")
        p.resource_manager.register_with_source("tex:hero", {"w": 1}, "hero.png")
        self.assertEqual(p.resource_manager.get_source("tex:hero"), "hero.png")


if __name__ == "__main__":
    unittest.main(verbosity=2)

