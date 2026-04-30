
import logging


logger = logging.getLogger(__name__)

# /**************************************************************************/
# /*  errors.py                                                             */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

class EngineError(Exception):
    """Base engine exception."""


class ValidationError(EngineError):
    """Input/schema validation failure."""


class InteropError(EngineError):
    """Import/export interoperability failure."""


class ScriptingSecurityError(EngineError):
    """Raised when script violates runtime safety policy."""


class SecurityError(EngineError):
    """Raised when a security policy violation is detected."""

