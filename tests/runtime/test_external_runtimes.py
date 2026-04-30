# /**************************************************************************/
# /*  test_external_runtimes.py                                             */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.scripting.abi import ScriptContext
from engine.scripting.external_runtime import ExternalRuntimeError
from engine.scripting.lua_runtime import LuaRuntime


class TestExternalRuntimes(unittest.TestCase):
    def test_lua_runtime_contract(self):
        ctx = ScriptContext(node_id="n", scene_id="s", properties={})
        runtime = LuaRuntime()
        try:
            result = runtime.execute("print('ok')", ctx)
            self.assertIn("language", result)
        except ExternalRuntimeError as e:
            self.assertIn("runtime", str(e).lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
