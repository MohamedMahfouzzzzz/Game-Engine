# /**************************************************************************/
# /*  __init__.py                                                           */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Game Engine Studio - Core Engine Package."""

from engine.crash_handler import (
    install,
    mark_clean_shutdown,
    has_pending_recovery,
    get_recovery_path,
    clear_recovery,
)
from engine.session_manager import SessionManager

import logging


logger = logging.getLogger(__name__)


__all__ = [
    "install",
    "mark_clean_shutdown",
    "has_pending_recovery",
    "get_recovery_path",
    "clear_recovery",
    "SessionManager",
]
