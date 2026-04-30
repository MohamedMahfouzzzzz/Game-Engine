# /**************************************************************************/
# /*  headless/__init__.py                                                  */
# /**************************************************************************/

"""Headless mode for CLI and automated operations.

Provides core engine functionality without UI for:
- Batch processing
- Automated builds
- Server-side operations
- Testing
"""

from .headless_engine import HeadlessEngine, HeadlessMode
from .cli_interface import CLIInterface
from .batch_processor import BatchProcessor

__all__ = [
    "HeadlessEngine",
    "HeadlessMode",
    "CLIInterface",
    "BatchProcessor",
]
