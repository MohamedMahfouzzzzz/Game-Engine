# /**************************************************************************/
# /*  import_godot_project.py                                               */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

import argparse
import json
from pathlib import Path
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine.interop.godot_importer import GodotImporter

import logging


logger = logging.getLogger(__name__)



def main() -> None:
    parser = argparse.ArgumentParser(description="Import a Godot 2D project into this engine format.")
    parser.add_argument("source", help="Path to Godot project.godot or .tscn file")
    parser.add_argument("--out", default="imported_project.gep.json", help="Output JSON file")
    parser.add_argument("--report", default="", help="Optional path for a compact import report JSON")
    args = parser.parse_args()

    importer = GodotImporter()
    project = importer.import_project(args.source)
    out_path = Path(args.out)
    out_path.write_text(json.dumps(project.to_dict(), indent=2), encoding="utf-8")
    print(f"Imported project '{project.name}' with {len(project.scenes)} scene(s) -> {out_path}")
    report = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": args.source,
        "project": project.name,
        "scene_count": len(project.scenes),
        "active_scene": project.active_scene.name if project.active_scene else None,
        "godot_import": project.assets.get("godot_import", {}),
    }
    report_path = Path(args.report) if args.report else out_path.with_suffix(out_path.suffix + ".report.json")
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Import report -> {report_path}")


if __name__ == "__main__":
    main()
