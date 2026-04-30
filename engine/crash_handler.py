# /**************************************************************************/
# /*  crash_handler.py                                                      */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""
Crash handler for Game Engine Studio.

Intercepts all abnormal terminations:
  - Unhandled Python exceptions  (sys.excepthook)
  - SIGTERM / SIGINT              (signal module)
  - Normal exit / atexit          (atexit module)

On any unexpected exit the handler:
  1. Writes a detailed crash log  → logs/crash_<timestamp>.log
  2. Saves an emergency session   → <project_dir>/.recovery/session_<ts>.gep
  3. Stores a flag file so the editor can offer recovery on next launch.
"""

from __future__ import annotations

import atexit
import json
import logging
import os
import platform
import signal
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional

if TYPE_CHECKING:
    from types import TracebackType

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_LOG_DIR = Path("logs")
_RECOVERY_DIR = Path(".Recovery")
_FLAG_FILE = _RECOVERY_DIR / ".crash_flag"
_MAX_LOG_FILES = 20          # rotate after this many crash logs


# ---------------------------------------------------------------------------
# Internal state
# ---------------------------------------------------------------------------
_original_excepthook: Callable = sys.__excepthook__
_session_saver_callback: Optional[Callable[[], Optional[Dict[str, Any]]]] = None
_crash_occurred: bool = False
_clean_shutdown: bool = False


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def install(
    session_saver: Optional[Callable[[], Optional[Dict[str, Any]]]] = None,
) -> None:
    """Install the crash handler.

    Args:
        session_saver: Optional callback that returns a JSON-serialisable dict
                       representing the current editor session. Called just
                       before writing the recovery file.
    """
    global _session_saver_callback
    _session_saver_callback = session_saver

    # Ensure directories exist
    _LOG_DIR.mkdir(parents=True, exist_ok=True)
    _RECOVERY_DIR.mkdir(parents=True, exist_ok=True)

    # Hook into Python's exception system
    sys.excepthook = _excepthook

    # Hook OS signals for graceful handling of external kill signals
    try:
        signal.signal(signal.SIGTERM, _signal_handler)
        signal.signal(signal.SIGINT, _signal_handler)
        if hasattr(signal, "SIGBREAK"):           # Windows Ctrl+Break
            signal.signal(signal.SIGBREAK, _signal_handler)  # type: ignore[attr-defined]
    except (OSError, ValueError):
        # Can't install signal handlers in threads or some environments
        pass

    # atexit runs even on sys.exit(), but NOT on os._exit() or SIGKILL
    atexit.register(_atexit_handler)

    # Setup file logging
    _setup_file_logging()

    logger.info("Crash handler installed.")


def mark_clean_shutdown() -> None:
    """Call this right before a deliberate, clean exit so the handler knows
    not to treat the shutdown as a crash."""
    global _clean_shutdown
    _clean_shutdown = True
    # Remove any stale crash flag from a previous run
    _FLAG_FILE.unlink(missing_ok=True)


def has_pending_recovery() -> bool:
    """Return True if a recovery file exists from a previous crash."""
    return _FLAG_FILE.exists()


def get_recovery_path() -> Optional[Path]:
    """Return the path to the most recent recovery session file, if any."""
    if not _FLAG_FILE.exists():
        return None
    try:
        flag_data = json.loads(_FLAG_FILE.read_text(encoding="utf-8"))
        path = Path(flag_data.get("session_file", ""))
        # Update extension check to .Game
        if path.exists() and path.suffix == ".Game":
            return path
        return None
    except Exception:
        return None


def clear_recovery() -> None:
    """Delete the crash flag and recovery session file."""
    recovery_path = get_recovery_path()
    if recovery_path and recovery_path.exists():
        recovery_path.unlink(missing_ok=True)
    _FLAG_FILE.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _excepthook(
    exc_type: type,
    exc_value: BaseException,
    exc_tb: Optional["TracebackType"],
) -> None:
    global _crash_occurred
    if _crash_occurred:
        return
    _crash_occurred = True

    if issubclass(exc_type, KeyboardInterrupt):
        # Don't treat Ctrl+C as a crash
        _original_excepthook(exc_type, exc_value, exc_tb)
        return

    tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    _handle_crash(reason="unhandled_exception", details=tb_str)
    _original_excepthook(exc_type, exc_value, exc_tb)


def _signal_handler(signum: int, frame: Any) -> None:
    global _crash_occurred
    if _crash_occurred or _clean_shutdown:
        return
    _crash_occurred = True
    sig_name = signal.Signals(signum).name if hasattr(signal, "Signals") else str(signum)
    _handle_crash(reason=f"signal_{sig_name}", details=f"Process terminated by signal {sig_name}.")
    sys.exit(1)


def _atexit_handler() -> None:
    if not _crash_occurred and not _clean_shutdown:
        # Process is exiting unexpectedly without an exception being raised
        # (e.g. os.kill(), Task Manager)
        _handle_crash(reason="unexpected_exit", details="Process exited without clean shutdown.")


def _handle_crash(reason: str, details: str) -> None:
    """Core crash-handling logic: write log, save session, write flag."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    log_path = _LOG_DIR / f"crash_{ts}.log"
    session_path = _RECOVERY_DIR / f"session_{ts}.gep"

    # --- Write crash log ---------------------------------------------------
    system_info = _collect_system_info()
    log_lines = [
        "=" * 72,
        f"  GAME ENGINE STUDIO — CRASH REPORT",
        f"  Timestamp : {datetime.now(timezone.utc).isoformat()}",
        f"  Reason    : {reason}",
        "=" * 72,
        "",
        "[ System Info ]",
        *(f"  {k}: {v}" for k, v in system_info.items()),
        "",
        "[ Details ]",
        details,
        "",
    ]
    try:
        log_path.write_text("\n".join(log_lines), encoding="utf-8")
        logger.info("Crash log written: %s", log_path)
    except Exception as write_err:
        print(f"[CrashHandler] Could not write crash log: {write_err}", file=sys.stderr)

    # --- Save session snapshot ---------------------------------------------
    session_data: Optional[Dict[str, Any]] = None
    if _session_saver_callback is not None:
        try:
            session_data = _session_saver_callback()
        except Exception as cb_err:
            logger.warning("Session saver callback failed: %s", cb_err)

    if session_data is not None:
        try:
            session_path.write_text(
                json.dumps(session_data, indent=2, default=str),
                encoding="utf-8",
            )
        except Exception as sess_err:
            logger.warning("Could not write recovery session: %s", sess_err)
            session_path = None  # type: ignore[assignment]

    # --- Write crash flag --------------------------------------------------
    flag_data = {
        "crash_time": datetime.now(timezone.utc).isoformat(),
        "reason": reason,
        "log_file": str(log_path),
        "session_file": str(session_path) if session_data is not None else None,
    }
    try:
        _FLAG_FILE.write_text(json.dumps(flag_data, indent=2), encoding="utf-8")
    except Exception:
        pass

    # --- Rotate old logs ---------------------------------------------------
    _rotate_logs()


def _collect_system_info() -> Dict[str, str]:
    info: Dict[str, str] = {
        "OS": platform.platform(),
        "Python": sys.version.replace("\n", " "),
        "Executable": sys.executable,
        "CWD": os.getcwd(),
    }
    try:
        import psutil  # optional dependency
        proc = psutil.Process()
        info["Memory (MB)"] = f"{proc.memory_info().rss / 1_048_576:.1f}"
    except ImportError:
        pass
    return info


def _rotate_logs() -> None:
    logs = sorted(_LOG_DIR.glob("crash_*.log"), key=lambda p: p.stat().st_mtime)
    while len(logs) > _MAX_LOG_FILES:
        try:
            logs.pop(0).unlink()
        except Exception:
            break


def _setup_file_logging() -> None:
    _LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = _LOG_DIR / "engine.log"
    handler = logging.FileHandler(log_file, encoding="utf-8")
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.DEBUG)


def setup_crash_handler() -> None:
    """Set up global crash handler for the engine."""
    import sys
    import faulthandler
    import atexit
    
    # Enable faulthandler for segfaults
    faulthandler.enable()
    
    # Set up custom exception hook
    sys.excepthook = handle_exception
    
    # Set up file logging
    _setup_file_logging()
    
    # Register cleanup on exit
    atexit.register(_rotate_logs)
    
    _logger.info("Crash handler initialized")


# Keep backwards compatibility
init_engine_logging = setup_crash_handler
