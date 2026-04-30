# /**************************************************************************/
# /*  __init__.py                                                           */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

from engine.extensions.manager_secure import SecureExtensionManager as ExtensionManager

import logging


logger = logging.getLogger(__name__)


__all__ = ["ExtensionManager"]
