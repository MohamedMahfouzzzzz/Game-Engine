# /**************************************************************************/
# /*  playthrow_format.py                                                   */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Playthrow format specification and utilities."""

import json
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Dict, List, Optional, Any
import zlib

import logging

logger = logging.getLogger(__name__)


@dataclass
class PlaythrowHeader:
    """Binary file header for .playthrow format."""
    magic: bytes = b"PLYTHRW"  # 7 bytes
    version: int = 1
    compression: int = 1  # 0=none, 1=zlib
    session_id: str = ""
    project_id: str = ""
    player_id: str = ""
    start_time: float = 0.0
    action_count: int = 0
    metadata_size: int = 0


class PlaythrowFormat:
    """Handles the .playthrow binary format."""

    HEADER_SIZE = 128  # Fixed header size

    @classmethod
    def write_playthrow(
        cls,
        file_path: Path,
        session_data: Dict[str, Any],
        compress: bool = True
    ) -> None:
        """Write session data to .playthrow binary file."""
        actions = session_data.get("actions", [])

        # Prepare header
        header = PlaythrowHeader(
            session_id=session_data.get("session_id", ""),
            project_id=session_data.get("project_id", ""),
            player_id=session_data.get("player_id", ""),
            start_time=session_data.get("start_time", 0.0),
            action_count=len(actions),
            compression=1 if compress else 0,
            metadata_size=0
        )

        # Serialize actions
        actions_json = json.dumps(actions).encode("utf-8")
        if compress:
            actions_data = zlib.compress(actions_json)
        else:
            actions_data = actions_json

        # Write file
        with open(file_path, "wb") as f:
            cls._write_header(f, header)
            f.write(actions_data)

    @classmethod
    def read_playthrow(cls, file_path: Path) -> Dict[str, Any]:
        """Read session data from .playthrow binary file."""
        with open(file_path, "rb") as f:
            header = cls._read_header(f)
            data = f.read()

        # Decompress if needed
        if header.compression == 1:
            data = zlib.decompress(data)

        actions = json.loads(data.decode("utf-8"))

        return {
            "session_id": header.session_id,
            "project_id": header.project_id,
            "player_id": header.player_id,
            "start_time": header.start_time,
            "action_count": header.action_count,
            "actions": actions
        }

    @classmethod
    def _write_header(cls, f: BinaryIO, header: PlaythrowHeader) -> None:
        """Write binary header."""
        f.write(header.magic)
        f.write(struct.pack("<B", header.version))
        f.write(struct.pack("<B", header.compression))
        f.write(struct.pack("<I", header.action_count))
        f.write(struct.pack("<I", header.metadata_size))
        f.write(struct.pack("<d", header.start_time))

        # Write strings with length prefix
        cls._write_string(f, header.session_id)
        cls._write_string(f, header.project_id)
        cls._write_string(f, header.player_id)

        # Pad to fixed size
        current = f.tell()
        if current < cls.HEADER_SIZE:
            f.write(b"\x00" * (cls.HEADER_SIZE - current))

    @classmethod
    def _read_header(cls, f: BinaryIO) -> PlaythrowHeader:
        """Read binary header."""
        header = PlaythrowHeader()

        header.magic = f.read(7)
        header.version = struct.unpack("<B", f.read(1))[0]
        header.compression = struct.unpack("<B", f.read(1))[0]
        header.action_count = struct.unpack("<I", f.read(4))[0]
        header.metadata_size = struct.unpack("<I", f.read(4))[0]
        header.start_time = struct.unpack("<d", f.read(8))[0]

        header.session_id = cls._read_string(f)
        header.project_id = cls._read_string(f)
        header.player_id = cls._read_string(f)

        # Skip padding
        f.seek(cls.HEADER_SIZE)

        return header

    @staticmethod
    def _write_string(f: BinaryIO, s: str) -> None:
        """Write length-prefixed string."""
        encoded = s.encode("utf-8")
        f.write(struct.pack("<H", len(encoded)))
        f.write(encoded)

    @staticmethod
    def _read_string(f: BinaryIO) -> str:
        """Read length-prefixed string."""
        length = struct.unpack("<H", f.read(2))[0]
        return f.read(length).decode("utf-8")

    @classmethod
    def validate_file(cls, file_path: Path) -> bool:
        """Validate if file is a valid .playthrow file."""
        try:
            with open(file_path, "rb") as f:
                magic = f.read(7)
                return magic == b"PLYTHRW"
        except (FileNotFoundError, IOError):
            return False
