# /**************************************************************************/
# /*  test_soak_memory.py                                                   */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

import os
import sys
import time
import unittest
import tracemalloc

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.core.node import Node2D, Scene


class TestMemorySoak(unittest.TestCase):
    def test_scene_add_remove_no_unbounded_growth(self):
        tracemalloc.start()
        scene = Scene("Soak")

        def snapshot_kb():
            current, peak = tracemalloc.get_traced_memory()
            return int(current / 1024), int(peak / 1024)

        baseline_current, _ = snapshot_kb()

        for i in range(2000):
            parent = Node2D(f"P{i}")
            child = Node2D(f"C{i}")
            parent.add_child(child)
            scene.add_node(parent)
            scene.remove_node(parent)

        after_current, _ = snapshot_kb()
        tracemalloc.stop()

        # Allow some growth for allocator noise; should not be huge for add/remove cycles.
        self.assertLess(after_current - baseline_current, 1024)


if __name__ == "__main__":
    unittest.main(verbosity=2)

