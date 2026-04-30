#!/usr/bin/env python3
# /**************************************************************************/
# /*  editor_main.py                                                        */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Game Engine Editor - Main entry point.

Python port of Godot's editor with PySide6 UI framework.
"""

import sys
import os
from pathlib import Path

# Add engine to path
engine_path = Path(__file__).parent / "engine"
if str(engine_path) not in sys.path:
    sys.path.insert(0, str(engine_path))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from editor.editor_node import EditorNode
from editor.project_manager import ProjectManager
from engine import crash_handler


def main():
    """Main editor entry point."""
    # Setup crash handler
    # crash_handler.initialize()  # TODO: Implement initialize function

    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("Game Engine Editor")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Game Engine")

    # Set high DPI scaling (fixed for newer PySide6)
    # app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    # app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    # Show project manager FIRST (before showing any editor window)
    project_manager = ProjectManager(None)  # No parent - main window

    if project_manager.exec() != ProjectManager.Accepted:
        # User cancelled, exit
        return 0

    # Create main editor window AFTER project is selected
    editor = EditorNode()

    # Load the selected project
    if project_manager.project_path:
        editor._load_project(project_manager.project_path)

    # Show the editor
    editor.show()

    # Run the application
    return app.exec()


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
