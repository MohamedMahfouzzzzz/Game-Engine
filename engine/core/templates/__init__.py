# /**************************************************************************/
# /*  __init__.py                                                           */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Ready-made scene templates for games."""

from .remapping_scene import RemappingScene

import logging


logger = logging.getLogger(__name__)


__all__ = ['RemappingScene']
