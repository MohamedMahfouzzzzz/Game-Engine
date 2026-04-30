# /**************************************************************************/
# /*  external_runtime.py                                                   */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from engine.scripting.abi import ScriptContext

import logging



class ExternalRuntimeError(RuntimeError):
    pass


def _run_process(command: list[str], env: dict[str, str], cwd: Optional[str] = None) -> str:
    result = subprocess.run(command, capture_output=True, text=True, env=env, cwd=cwd)
    if result.returncode != 0:
        raise ExternalRuntimeError(result.stderr.strip() or result.stdout.strip() or "External runtime failed")
    return result.stdout.strip()


logger = logging.getLogger(__name__)

def _context_env(context: ScriptContext) -> dict[str, str]:
    """Create minimal environment for external runtimes, avoiding secrets leak."""
    payload = {
        "node_id": context.node_id,
        "scene_id": context.scene_id,
        "properties": context.properties,
    }
    # Minimal environment - only include what's necessary
    # Do NOT copy os.environ to avoid leaking API keys, tokens, etc.
    env = {
        "GAME_ENGINE_CONTEXT_JSON": json.dumps(payload),
        "PATH": os.environ.get("PATH", ""),  # Required for finding runtimes
        "TEMP": os.environ.get("TEMP", os.environ.get("TMP", "/tmp")),
        "TMP": os.environ.get("TMP", os.environ.get("TEMP", "/tmp")),
        # Explicitly excluded: HOME, USER, USERNAME, API keys, tokens, etc.
    }
    return env


def run_lua(source: str, context: ScriptContext):
    lua_bin = shutil.which("lua")
    if not lua_bin:
        raise ExternalRuntimeError("Lua runtime not found. Install Lua and expose `lua` on PATH.")
    with tempfile.TemporaryDirectory() as d:
        script = Path(d) / "script.lua"
        script.write_text(source, encoding="utf-8")
        out = _run_process([lua_bin, str(script)], env=_context_env(context), cwd=d)
    return {"language": "lua", "output": out}
