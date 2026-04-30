# /**************************************************************************/
# /*  test_runtime_loop.py                                                  */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.core.node import Node2D, Project
from engine.runtime.game_loop import GameRuntime, RuntimeConfig


class CounterScript:
    def __init__(self):
        self.inited = False
        self.updates = 0
        self.torn = False

    def on_init(self):
        self.inited = True

    def on_update(self, dt: float):
        self.updates += 1

    def on_teardown(self):
        self.torn = True


class TestRuntimeLoop(unittest.TestCase):
    def test_lifecycle_calls(self):
        p = Project("R")
        s = p.create_scene("S")
        n = Node2D("N")
        script = CounterScript()
        n.script = script
        s.add_node(n)
        rt = GameRuntime(p, RuntimeConfig(fixed_dt=0.0, max_steps=5))
        rt.run()
        self.assertTrue(script.inited)
        self.assertEqual(script.updates, 5)
        self.assertTrue(script.torn)


if __name__ == "__main__":
    unittest.main(verbosity=2)

