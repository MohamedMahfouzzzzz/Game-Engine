# /**************************************************************************/
# /*  project_io.py                                                         */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

import json
import os
from pathlib import Path
from typing import Any, Dict

from engine.core.project_secure import SecureProject as Project, PROJECT_FILE_MAGIC
from engine.core.errors import ValidationError

# Project file header
PROJECT_MAGIC = b"GESP"  # Game Engine Project
PROJECT_VERSION = 1
MAX_PROJECT_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
SUPPORTED_EXTENSION = ".Game"
SUPPORTED_VERSION = 1
MAX_SCENES = 500
MAX_NODES_PER_SCENE = 20000


def _safe_realpath(path: str) -> str:
    return os.path.realpath(os.path.abspath(path))


def _validate_path_policy(file_path: str) -> None:
    # Basic path policy: avoid weird device names and ensure a normal file path.
    real = _safe_realpath(file_path)
    if not real.lower().endswith(SUPPORTED_EXTENSION.lower()):
        raise ValueError("Unsupported file extension.")


def _validate_project_schema(data: Dict[str, Any]) -> None:
    if not isinstance(data, dict):
        raise ValueError("Project file must be a JSON object.")
    version = data.get("version", SUPPORTED_VERSION)
    if version != SUPPORTED_VERSION:
        raise ValueError(f"Unsupported project version: {version}")
    for required_key in ["name", "scenes"]:
        if required_key not in data:
            raise ValueError(f"Missing required project key: {required_key}")
    if not isinstance(data["scenes"], dict):
        raise ValueError("scenes must be a dictionary.")
    if len(data["scenes"]) > MAX_SCENES:
        raise ValueError("Too many scenes.")
    # Shallow sanity checks to reduce DoS risk from huge nested objects.
    for _, scene in data["scenes"].items():
        if not isinstance(scene, dict):
            raise ValueError("Scene must be an object.")
        root = scene.get("root")
        if not isinstance(root, dict):
            raise ValueError("Scene root must be an object.")
        # Count nodes iteratively with a cap.
        stack = [root]
        count = 0
        while stack:
            node = stack.pop()
            count += 1
            if count > MAX_NODES_PER_SCENE:
                raise ValueError("Scene has too many nodes.")
            children = node.get("children", [])
            if not isinstance(children, list):
                raise ValueError("Node children must be a list.")
            for child in children:
                if isinstance(child, dict):
                    stack.append(child)


def load_project(file_path: str) -> Project:
    _validate_path_policy(file_path)
    with open(file_path, "rb") as file_handle:
        raw = file_handle.read()
    if len(raw) > MAX_PROJECT_SIZE_BYTES:
        raise ValueError("Project file exceeds size limit.")
    
    # Try new binary header format first
    try:
        from engine.core.project import PROJECT_FILE_MAGIC
        if raw[:4] == PROJECT_FILE_MAGIC:
            return Project.load_from_file_sync(Path(file_path))
    except Exception:
        # Fall back to old JSON-only format
        pass
    
    data = json.loads(raw.decode("utf-8"))
    _validate_project_schema(data)
    return Project.from_dict(data)


def save_project(file_path: str, project: Project) -> None:
    _validate_path_policy(file_path)
    # Use new binary header format
    project.save_to_file_sync(Path(file_path))


def _atomic_write(file_path: str, payload: bytes) -> None:
    directory = os.path.dirname(_safe_realpath(file_path)) or "."
    base = os.path.basename(file_path)
    tmp_path = os.path.join(directory, f".{base}.tmp")
    bak_path = os.path.join(directory, f"{base}.bak")
    # Write tmp
    with open(tmp_path, "wb") as file_handle:
        file_handle.write(payload)
        file_handle.flush()
        os.fsync(file_handle.fileno())
    # Backup old if exists
    if os.path.exists(file_path):
        try:
            if os.path.exists(bak_path):
                os.remove(bak_path)
            os.replace(file_path, bak_path)
        except OSError:
            # If backup fails, still attempt safe replace.
            pass
    os.replace(tmp_path, file_path)
