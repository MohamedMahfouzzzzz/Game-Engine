"""Dialogue localization resources."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict


class TranslationManager:
    """Small resource-backed translation table for dialogue text."""

    def __init__(self) -> None:
        self._tables: Dict[str, Dict[str, str]] = {}
        self.locale = "en"

    def set_locale(self, locale: str) -> None:
        self.locale = locale

    def add(self, key: str, text: str, locale: str | None = None) -> None:
        self._tables.setdefault(locale or self.locale, {})[key] = text

    def translate(self, key: str, fallback: str = "") -> str:
        return self._tables.get(self.locale, {}).get(key, fallback or key)

    def load_json(self, path: str | Path, locale: str | None = None) -> None:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        table = self._tables.setdefault(locale or self.locale, {})
        for key, value in data.items():
            table[str(key)] = str(value)

    def save_json(self, path: str | Path, locale: str | None = None) -> None:
        table = self._tables.get(locale or self.locale, {})
        Path(path).write_text(json.dumps(table, indent=2, ensure_ascii=False), encoding="utf-8")

    def load_csv(self, path: str | Path, locale: str | None = None) -> None:
        table = self._tables.setdefault(locale or self.locale, {})
        with open(path, newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                key = row.get("key") or row.get("id") or row.get("dialogue")
                text = row.get("text") or row.get("translation")
                if key and text is not None:
                    table[str(key)] = str(text)
