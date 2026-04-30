# /**************************************************************************/
# /*  __init__.py                                                           */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Runtime module for game execution."""

import logging

from engine.runtime.game_loop import (
    FPSCounter,
    GameLoop,
    GameRuntime,
    LoopState,
    RuntimeConfig,
)

logger = logging.getLogger(__name__)

__all__ = [
    "GameLoop",
    "GameRuntime",
    "FPSCounter",
    "LoopState",
    "RuntimeConfig",
]
