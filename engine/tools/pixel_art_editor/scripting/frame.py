# /**************************************************************************/
# /*  frame.py                                                              */
# /**************************************************************************/

"""Frame class for Aseprite API."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

import logging

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .aseprite_api import Sprite


@dataclass
class Frame:
    """Aseprite Frame class."""
    frameNumber: int
    sprite: "Sprite"
    duration: int = 100  # Duration in milliseconds
