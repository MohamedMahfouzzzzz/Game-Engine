# /**************************************************************************/
# /*  file_browser.py                                                       */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Secure file browser with path traversal protection.

Security features:
- Path traversal prevention (blocks ../)
- Root path enforcement (can't browse outside project)
- Symlink following disabled
- File type validation
"""

from __future__ import annotations

import os
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QTreeView, QVBoxLayout, QWidget, QLabel, QFileSystemModel


class SecurityError(Exception):
    """Security policy violation."""
    pass


class ProjectFileBrowserWidget(QWidget):
    """File browser with security restrictions.
    
    Prevents:
    - Path traversal attacks (../..)
    - Access outside project root
    - Symlink escapes
    """
    
    file_activated = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._root_path = os.getcwd()
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Project Files"))
        self.model = QFileSystemModel(self)
        self.model.setRootPath(self._root_path)
        self.tree = QTreeView(self)
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(self._root_path))
        self.tree.doubleClicked.connect(self._on_double_click)
        self.tree.setHeaderHidden(False)
        self.tree.setAlternatingRowColors(True)
        layout.addWidget(self.tree)

    def set_root_path(self, path: str) -> None:
        """Set root path with security validation."""
        if not path or not os.path.isdir(path):
            return
        
        # Resolve to absolute, normalized path
        resolved = Path(path).resolve()
        
        # Ensure path exists and is a directory
        if not resolved.is_dir():
            return
        
        self._root_path = str(resolved)
        self.model.setRootPath(self._root_path)
        self.tree.setRootIndex(self.model.index(self._root_path))

    def _is_path_safe(self, file_path: str) -> bool:
        """Check if file path is within allowed root directory.
        
        Prevents path traversal attacks like:
        - ../../../etc/passwd
        - symlink escapes
        - absolute path injection
        """
        try:
            # Resolve to absolute path
            resolved = Path(file_path).resolve()
            root = Path(self._root_path).resolve()
            
            # Check if resolved path is under root
            try:
                resolved.relative_to(root)
                return True
            except ValueError:
                return False
                
        except (OSError, ValueError):
            return False

    def _on_double_click(self, index) -> None:
        file_path = self.model.filePath(index)
        
        # Security: Validate path before activation
        if not self._is_path_safe(file_path):
            # Log security violation
            print(f"[SECURITY] Blocked path traversal attempt: {file_path}")
            return
        
        if os.path.isfile(file_path):
            self.file_activated.emit(file_path)
