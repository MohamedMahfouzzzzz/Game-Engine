# /**************************************************************************/
# /*  reimport_cache.py                                                     */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

import os
import json
from dataclasses import dataclass
from typing import Any, Dict, Optional

from engine.content.dependency_graph import AssetDependencyGraph

import logging


logger = logging.getLogger(__name__)



@dataclass
class ImportRecord:
    source_path: str
    mtime_ns: int
    imported: Any
    kind: str


class ReimportCache:
    def __init__(self) -> None:
        self._records: Dict[str, ImportRecord] = {}
        self.deps = AssetDependencyGraph()

    def needs_reimport(self, key: str, source_path: str) -> bool:
        source_path = os.path.abspath(source_path)
        rec = self._records.get(key)
        try:
            mtime_ns = os.stat(source_path).st_mtime_ns
        except OSError:
            return False
        if rec is None:
            return True
        return rec.mtime_ns != mtime_ns

    def update(self, key: str, source_path: str, imported: Any, kind: str) -> None:
        source_path = os.path.abspath(source_path)
        mtime_ns = os.stat(source_path).st_mtime_ns
        self._records[key] = ImportRecord(source_path=source_path, mtime_ns=mtime_ns, imported=imported, kind=kind)

    def get(self, key: str) -> Optional[Any]:
        rec = self._records.get(key)
        return rec.imported if rec else None

    def save_to_file(self, path: str) -> None:
        serializable = {
            key: {
                "source_path": rec.source_path,
                "mtime_ns": rec.mtime_ns,
                "kind": rec.kind,
            }
            for key, rec in self._records.items()
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(serializable, f, indent=2)

    def load_from_file(self, path: str) -> None:
        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for key, rec in data.items():
            self._records[key] = ImportRecord(
                source_path=rec["source_path"],
                mtime_ns=rec["mtime_ns"],
                imported=None,
                kind=rec.get("kind", "unknown"),
            )

