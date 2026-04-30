# /**************************************************************************/
# /*  session_manager.py                                                    */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""
Auto-save and session management for the editor.

Saves the active project state every N seconds to a recovery file so that
work is never lost on a crash or unexpected shutdown.
"""

from __future__ import annotations

import json
import logging
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Optional

# Recovery file header
RECOVERY_MAGIC = b"GREC"  # Game Engine Recovery
RECOVERY_VERSION = 1

logger = logging.getLogger(__name__)

_DEFAULT_INTERVAL_SECONDS = 60
_RECOVERY_SUBDIR = ".Recovery"


class SessionManager:
    """Periodically saves the current project to a recovery file.

    Usage::

        mgr = SessionManager(interval=60)
        mgr.set_project_root(Path("my_project"))
        mgr.set_snapshot_provider(lambda: project.to_dict())
        mgr.start()
        ...
        mgr.stop(clean=True)   # clean=True removes the recovery file
    """

    def __init__(self, interval: int = _DEFAULT_INTERVAL_SECONDS) -> None:
        self._interval = interval
        self._project_root: Optional[Path] = None
        self._snapshot_provider: Optional[Callable[[], Optional[Dict[str, Any]]]] = None
        self._timer: Optional[threading.Timer] = None
        self._lock = threading.Lock()
        self._running = False
        self._last_save_path: Optional[Path] = None

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def set_project_root(self, root: Path) -> None:
        """Point the session manager at the active project folder."""
        self._project_root = root
        self._recovery_dir.mkdir(parents=True, exist_ok=True)

    def set_snapshot_provider(
        self, provider: Callable[[], Optional[Dict[str, Any]]]
    ) -> None:
        """Register a callback that returns a JSON-serialisable project dict."""
        self._snapshot_provider = provider

    @property
    def _recovery_dir(self) -> Path:
        base = self._project_root or Path(".")
        return base / _RECOVERY_SUBDIR

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start the auto-save timer."""
        if self._running:
            return
        self._running = True
        self._schedule()
        logger.info("SessionManager started (interval=%ds).", self._interval)

    def stop(self, clean: bool = False) -> None:
        """Stop the auto-save timer.

        Args:
            clean: If True, delete the recovery file (clean shutdown).
        """
        self._running = False
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None
        if clean and self._last_save_path and self._last_save_path.exists():
            self._last_save_path.unlink(missing_ok=True)
            logger.info("Recovery file removed (clean shutdown).")

    def save_now(self) -> Optional[Path]:
        """Force an immediate save and return the path written."""
        return self._do_save()

    # ------------------------------------------------------------------
    # Recovery helpers (called by crash_handler / welcome dialog)
    # ------------------------------------------------------------------

    def list_recovery_files(self) -> list[Path]:
        """Return all .Game recovery files sorted newest first."""
        if not self._recovery_dir.exists():
            return []
        return sorted(
            self._recovery_dir.glob("autosave_*.Game"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

    def load_recovery(self, path: Path) -> Dict[str, Any]:
        """Load a recovery file and return its dict."""
        with open(path, "rb") as f:
            # Read and validate header
            magic = f.read(4)
            if magic == RECOVERY_MAGIC:
                # New binary header format
                version = int.from_bytes(f.read(1), byteorder="big")
                if version != RECOVERY_VERSION:
                    raise ValueError(f"Unsupported recovery file version: {version}")
                # Skip reserved bytes
                f.read(3)
                # Read JSON data
                json_data = f.read().decode("utf-8")
                return json.loads(json_data)
            else:
                # Old JSON-only format
                f.seek(0)
                return json.loads(f.read().decode("utf-8"))

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _schedule(self) -> None:
        if not self._running:
            return
        self._timer = threading.Timer(self._interval, self._tick)
        self._timer.daemon = True
        self._timer.start()

    def _tick(self) -> None:
        self._do_save()
        self._schedule()  # reschedule

    def _do_save(self) -> Optional[Path]:
        with self._lock:
            if self._snapshot_provider is None:
                return None
            try:
                data = self._snapshot_provider()
                if data is None:
                    return None
            except Exception as exc:
                logger.warning("Snapshot provider raised: %s", exc)
                return None

            ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            out_path = self._recovery_dir / f"autosave_{ts}.Game"
            self._recovery_dir.mkdir(parents=True, exist_ok=True)

            # Write with binary header for EXE packaging
            json_data = json.dumps(data, indent=2, default=str).encode("utf-8")
            with open(out_path, "wb") as f:
                # Magic bytes (4 bytes)
                f.write(RECOVERY_MAGIC)
                # Version (1 byte)
                f.write(bytes([RECOVERY_VERSION]))
                # Reserved bytes (3 bytes)
                f.write(b"\x00\x00\x00")
                # JSON data
                f.write(json_data)

            self._last_save_path = out_path
            logger.debug("Auto-saved session → %s", out_path)

            # Write crash flag
            flag_file = self._recovery_dir / ".crash_flag"
            flag_data = {"session_file": str(out_path), "timestamp": datetime.now(timezone.utc).isoformat()}
            flag_file.write_text(json.dumps(flag_data), encoding="utf-8")

            self._prune_old_saves(keep=5)
            return out_path

    def _prune_old_saves(self, keep: int = 5) -> None:
        """Keep only the N most recent auto-save files."""
        files = self.list_recovery_files()
        for old in files[keep:]:
            old.unlink(missing_ok=True)

    def _cleanup(self) -> None:
        """Delete crash flag and recovery files."""
        flag_file = self._recovery_dir / ".crash_flag"
        flag_file.unlink(missing_ok=True)

    # ------------------------------------------------------------------
    # Context-manager support
    # ------------------------------------------------------------------

    def __enter__(self) -> "SessionManager":
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stop(clean=(exc_type is None))
