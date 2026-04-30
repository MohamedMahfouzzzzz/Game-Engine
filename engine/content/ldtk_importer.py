# /**************************************************************************/
# /*  ldtk_importer.py                                                      */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

import json
from typing import Dict, Any

import logging


logger = logging.getLogger(__name__)



class LDtkImporter:
    def import_file(self, path: str) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)
        return {
            "type": "ldtk",
            "levels": data.get("levels", []),
            "tilesets": data.get("defs", {}).get("tilesets", []),
            "entities": data.get("defs", {}).get("entities", []),
        }
