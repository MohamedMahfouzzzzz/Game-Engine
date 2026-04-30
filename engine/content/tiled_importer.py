# /**************************************************************************/
# /*  tiled_importer.py                                                     */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

import json
from typing import Any, Dict

import logging


logger = logging.getLogger(__name__)



class TiledImporter:
    def import_file(self, path: str) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)
        return {
            "type": "tiled",
            "layers": data.get("layers", []),
            "tilesets": data.get("tilesets", []),
            "objects": [layer for layer in data.get("layers", []) if layer.get("type") == "objectgroup"],
            "properties": data.get("properties", []),
        }
