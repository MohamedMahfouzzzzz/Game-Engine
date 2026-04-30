# /**************************************************************************/
# /*  __init__.py                                                           */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Configuration management system."""

from engine.config.settings import Settings, get_settings

import logging


logger = logging.getLogger(__name__)


__all__ = ["Settings", "get_settings"]
