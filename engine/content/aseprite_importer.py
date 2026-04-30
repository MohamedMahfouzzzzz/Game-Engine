# /**************************************************************************/
# /*  aseprite_importer.py                                                  */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

from typing import Dict, Any

import logging


logger = logging.getLogger(__name__)



class AsepriteImporter:
    """Reads exported Aseprite JSON metadata."""

    def import_file(self, path: str) -> Dict[str, Any]:
        import json

        with open(path, "r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)
        meta = data.get("meta", {})
        return {
            "type": "aseprite",
            "layers": meta.get("layers", []),
            "tags": meta.get("frameTags", []),
            "slices": meta.get("slices", []),
            "frames": data.get("frames", {}),
        }
