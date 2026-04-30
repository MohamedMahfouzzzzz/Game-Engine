# /**************************************************************************/
# /*  test_scripting_security.py                                            */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.scripting.abi import ScriptContext
from engine.scripting.host import ScriptHost


class TestScriptingHardening(unittest.TestCase):
    def test_python_runtime_restricts_import(self):
        host = ScriptHost()
        ctx = ScriptContext(node_id="n", scene_id="s", properties={})
        with self.assertRaises(Exception):
            host.execute("python", "import os\nresult=os.getcwd()", ctx)

    def test_custom_lang_ignores_comments(self):
        host = ScriptHost()
        ctx = ScriptContext(node_id="n", scene_id="s", properties={})
        r = host.execute("custom", "# c\nvar hp=10\n//x\n", ctx)
        self.assertEqual(r["hp"], "10")

    def test_python_runtime_blocks_eval(self):
        host = ScriptHost()
        ctx = ScriptContext(node_id="n", scene_id="s", properties={})
        with self.assertRaises(Exception):
            host.execute("python", "result=eval('1+1')", ctx)


if __name__ == "__main__":
    unittest.main(verbosity=2)

