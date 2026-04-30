# /**************************************************************************/
# /*  host.py                                                               */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

from typing import Any, Dict

from engine.scripting.abi import ScriptContext
from engine.scripting.gdlang import GDLangVMRuntime


class ScriptHost:
    def __init__(self) -> None:
        self.runtimes = {
            "gdlang": GDLangVMRuntime(),  # VM-based runtime (default and only)
        }

    def execute(self, language: str, source: str, context: ScriptContext) -> Any:
        if language not in self.runtimes:
            raise ValueError(f"Unsupported scripting language: {language}")
        return self.runtimes[language].execute(source, context)

    def available_languages(self) -> Dict[str, str]:
        return {k: v.__class__.__name__ for k, v in self.runtimes.items()}

    def get_default_language(self) -> str:
        """Get default scripting language."""
        return "gdlang"

    def is_supported(self, language: str) -> bool:
        """Check if language is supported."""
        return language in self.runtimes
