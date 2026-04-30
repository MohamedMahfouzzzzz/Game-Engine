# /**************************************************************************/
# /*  abi.py                                                                */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol

import logging


logger = logging.getLogger(__name__)



@dataclass
class ScriptContext:
    node_id: str
    scene_id: str
    properties: Dict[str, Any]
    node: Optional[Any] = None  # Optional reference to actual node object


class ScriptRuntime(Protocol):
    language: str

    def execute(self, source: str, context: ScriptContext) -> Any:
        ...