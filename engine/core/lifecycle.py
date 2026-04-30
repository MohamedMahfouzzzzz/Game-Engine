# /**************************************************************************/
# /*  lifecycle.py                                                          */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

from typing import Protocol

import logging


logger = logging.getLogger(__name__)



class LifecycleScript(Protocol):
    def on_init(self) -> None:
        ...

    def on_update(self, delta_time: float) -> None:
        ...

    def on_teardown(self) -> None:
        ...
