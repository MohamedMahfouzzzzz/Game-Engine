# /**************************************************************************/
# /*  test_import_cli.py                                                    */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

import json
import os
import subprocess
import sys
import tempfile
import unittest


class TestImportCLI(unittest.TestCase):
    def test_cli_generates_output_and_report(self):
        with tempfile.TemporaryDirectory() as d:
            project_file = os.path.join(d, "project.godot")
            scene_file = os.path.join(d, "main.tscn")
            out_file = os.path.join(d, "out.gep.json")
            report_file = os.path.join(d, "import_report.json")
            with open(project_file, "w", encoding="utf-8") as f:
                f.write('[application]\nconfig/name="CliDemo"\nrun/main_scene="res://main.tscn"\n')
            with open(scene_file, "w", encoding="utf-8") as f:
                f.write('[gd_scene load_steps=2 format=3]\n\n[node name="Main" type="Node2D"]\n')

            cmd = [
                sys.executable,
                "tools/import_godot_project.py",
                project_file,
                "--out",
                out_file,
                "--report",
                report_file,
            ]
            result = subprocess.run(cmd, cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))), capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertTrue(os.path.exists(out_file))
            self.assertTrue(os.path.exists(report_file))
            with open(report_file, "r", encoding="utf-8") as f:
                report = json.loads(f.read())
            self.assertEqual(report["project"], "CliDemo")


if __name__ == "__main__":
    unittest.main(verbosity=2)

