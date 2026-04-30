# /**************************************************************************/
# /*  main.py                                                               */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Application entry-point for Game Engine Studio."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the project root is always on the path regardless of how the
# executable is invoked (e.g. PyInstaller one-file bundle).
sys.path.insert(0, str(Path(__file__).resolve().parent))

from ui.main_window import main  # noqa: E402

if __name__ == "__main__":
    main()
