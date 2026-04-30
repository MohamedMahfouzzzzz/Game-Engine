# /**************************************************************************/
# /*  test_reimport_cache.py                                                */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

import os
import sys
import unittest
import tempfile
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.content.reimport_cache import ReimportCache
from engine.content.ldtk_importer import LDtkImporter


class TestReimportCache(unittest.TestCase):
    def test_needs_reimport_on_change(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "a.ldtk")
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"levels": []}, f)
            cache = ReimportCache()
            key = "asset:ldtk:a"
            self.assertTrue(cache.needs_reimport(key, path))
            data = LDtkImporter().import_file(path)
            cache.update(key, path, data, "ldtk")
            self.assertFalse(cache.needs_reimport(key, path))
            # touch
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"levels": [{"identifier": "L1"}]}, f)
            self.assertTrue(cache.needs_reimport(key, path))

    def test_persist_cache_metadata(self):
        with tempfile.TemporaryDirectory() as d:
            asset = os.path.join(d, "a.ldtk")
            with open(asset, "w", encoding="utf-8") as f:
                json.dump({"levels": []}, f)
            cache_file = os.path.join(d, "cache.json")
            c1 = ReimportCache()
            c1.update("asset:a", asset, {"ok": 1}, "ldtk")
            c1.save_to_file(cache_file)
            c2 = ReimportCache()
            c2.load_from_file(cache_file)
            self.assertFalse(c2.needs_reimport("asset:a", asset))


if __name__ == "__main__":
    unittest.main(verbosity=2)

