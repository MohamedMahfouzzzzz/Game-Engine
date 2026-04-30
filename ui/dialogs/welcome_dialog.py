# /**************************************************************************/
# /*  welcome_dialog.py                                                     */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

from __future__ import annotations

from typing import Optional, Dict, List, Callable
from pathlib import Path
from dataclasses import dataclass
import json

from PySide6.QtWidgets import (
    QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget,
    QLineEdit, QTextEdit, QScrollArea, QCheckBox, QFileDialog,
    QGraphicsDropShadowEffect, QFrame
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon, QPixmap, QFont, QColor
import os


@dataclass
class ProjectInfo:
    """Project information for display."""
    name: str
    description: str
    path: str
    last_opened: str = ""


class ProjectCard(QWidget):
    """Project card widget matching the design."""
    
    clicked = Signal(str)  # emits project path
    
    def __init__(self, project: ProjectInfo, parent=None):
        super().__init__(parent)
        self.project = project
        self.setObjectName("projectCard")
        self.setFixedHeight(80)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._selected = False
        self._build_ui()
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(2, 2)
        self.setGraphicsEffect(shadow)
    
    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(15)
        
        # Circular icon
        self.icon_label = QLabel("Pic")
        self.icon_label.setFixedSize(50, 50)
        self.icon_label.setObjectName("projectIcon")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet("""
            QLabel {
                background-color: #e0e0e0;
                border-radius: 25px;
                border: 2px solid #c0c0c0;
                font-size: 14px;
                color: #555555;
            }
        """)
        layout.addWidget(self.icon_label)
        
        # Text content
        text_widget = QWidget()
        text_layout = QVBoxLayout(text_widget)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(5)
        
        self.name_label = QLabel(self.project.name)
        self.name_label.setObjectName("projectName")
        self.name_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 500;
                color: #333333;
                background: transparent;
            }
        """)
        text_layout.addWidget(self.name_label)
        
        self.desc_label = QLabel(self.project.description)
        self.desc_label.setObjectName("projectDesc")
        self.desc_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #666666;
                background: transparent;
            }
        """)
        text_layout.addWidget(self.desc_label)
        
        layout.addWidget(text_widget, 1)
        layout.addStretch()
    
    def mousePressEvent(self, event):
        self.clicked.emit(self.project.path)
    
    def set_selected(self, selected: bool):
        self._selected = selected
        if selected:
            self.setStyleSheet("""
                QWidget#projectCard {
                    background-color: #d0d0d0;
                    border-radius: 40px;
                    border: 2px solid #999999;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget#projectCard {
                    background-color: #e0e0e0;
                    border-radius: 40px;
                    border: 2px solid #c0c0c0;
                }
                QWidget#projectCard:hover {
                    background-color: #d8d8d8;
                    border: 2px solid #a0a0a0;
                }
            """)


class WelcomeDialog(QDialog):
    """Welcome dialog matching the design screenshot exactly."""
    
    def __init__(self, recent_paths: list[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Game Engine")
        self.setObjectName("welcomeDialog")
        self.resize(1000, 600)
        self.selected_action: str = "none"
        self.selected_path: Optional[str] = None
        self._recent_paths = recent_paths
        self._project_cards: List[ProjectCard] = []
        self._selected_project: Optional[str] = None
        self._has_recovery = self._check_recovery()
        self._build_ui()
        self._load_projects()
        self._apply_styles()
    
    def _build_ui(self) -> None:
        # Main layout - grey background
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)
        
        # Left side - Projects list container (the big rounded rectangle)
        left_container = QWidget()
        left_container.setObjectName("projectsContainer")
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(30, 30, 30, 30)
        left_layout.setSpacing(20)
        
        # Title "Game Engine"
        title = QLabel("Game Engine")
        title.setObjectName("gameEngineTitle")
        title.setStyleSheet("""
            QLabel {
                font-size: 36px;
                font-weight: bold;
                color: #000000;
                font-family: 'Courier New', monospace;
                letter-spacing: 2px;
                background: transparent;
            }
        """)
        left_layout.addWidget(title)
        
        # Scroll area for projects
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #d0d0d0;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #888888;
                border-radius: 4px;
                min-height: 30px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Projects widget inside scroll
        self.projects_widget = QWidget()
        self.projects_layout = QVBoxLayout(self.projects_widget)
        self.projects_layout.setContentsMargins(10, 10, 10, 10)
        self.projects_layout.setSpacing(15)
        self.projects_layout.addStretch()
        
        scroll.setWidget(self.projects_widget)
        left_layout.addWidget(scroll, 1)
        
        main_layout.addWidget(left_container, 3)
        
        # Right side - Buttons
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 80, 0, 0)
        right_layout.setSpacing(15)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Buttons as in the image
        self.new_project_btn = QPushButton("New Project")
        self.import_project_btn = QPushButton("Import Project")
        self.delete_project_btn = QPushButton("Delete Project")
        self.remove_project_btn = QPushButton("Remove Project")
        
        buttons = [
            self.new_project_btn,
            self.import_project_btn,
            self.delete_project_btn,
            self.remove_project_btn
        ]
        
        for btn in buttons:
            btn.setFixedSize(160, 45)
            btn.setObjectName("actionButton")
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #e8e8e8;
                    border: 2px solid #999999;
                    border-radius: 20px;
                    font-size: 14px;
                    color: #333333;
                }
                QPushButton:hover {
                    background-color: #d0d0d0;
                    border: 2px solid #666666;
                }
                QPushButton:pressed {
                    background-color: #c0c0c0;
                }
            """)
            right_layout.addWidget(btn)
        
        right_layout.addStretch()
        main_layout.addWidget(right_widget)
        
        # Connect buttons
        self.new_project_btn.clicked.connect(self._on_new_project)
        self.import_project_btn.clicked.connect(self._on_import_project)
        self.delete_project_btn.clicked.connect(self._on_delete_project)
        self.remove_project_btn.clicked.connect(self._on_remove_project)
    
    def _apply_styles(self):
        """Apply main styles."""
        self.setStyleSheet("""
            QDialog#welcomeDialog {
                background-color: #dddddd;
            }
            QWidget#projectsContainer {
                background-color: #e0e0e0;
                border: 2px solid #999999;
                border-radius: 60px;
            }
        """)
    
    def _load_projects(self):
        """Load recent projects into the list."""
        # Clear existing cards
        for card in self._project_cards:
            card.deleteLater()
        self._project_cards.clear()
        
        # Get real recent projects
        projects = self._get_recent_projects()
        
        if not projects:
            # Show placeholder if no projects
            placeholder = QLabel("No recent projects\nCreate a new project to get started")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    color: #888888;
                    background: transparent;
                    padding: 40px;
                }
            """)
            self.projects_layout.insertWidget(0, placeholder)
            return
        
        # Add project cards
        for project in projects:
            card = ProjectCard(project)
            card.clicked.connect(self._on_project_selected)
            card.set_selected(False)
            self.projects_layout.insertWidget(self.projects_layout.count() - 1, card)
            self._project_cards.append(card)
    
    def _get_recent_projects(self) -> List[ProjectInfo]:
        """Get list of recent projects with their info."""
        projects = []
        
        # Load from recent paths
        for path in self._recent_paths[:10]:  # Limit to 10 recent
            if os.path.exists(path):
                name = os.path.basename(path)
                if name.endswith('.Game'):
                    name = name[:-5]
                
                # Try to load project info
                description = "Game Engine Project"
                try:
                    # Check for project metadata
                    meta_path = os.path.join(os.path.dirname(path), '.project_meta.json')
                    if os.path.exists(meta_path):
                        with open(meta_path, 'r') as f:
                            meta = json.load(f)
                            description = meta.get('description', description)
                except:
                    pass
                
                # Get last modified time
                try:
                    mtime = os.path.getmtime(path)
                    from datetime import datetime
                    last_opened = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
                    description += f" (Last opened: {last_opened})"
                except:
                    pass
                
                projects.append(ProjectInfo(
                    name=name,
                    description=description,
                    path=path,
                    last_opened=""
                ))
        
        return projects
    
    def _on_project_selected(self, path: str):
        """Handle project card click."""
        self._selected_project = path
        # Update selection visual
        for card in self._project_cards:
            card.set_selected(card.project.path == path)
    
    def _on_new_project(self):
        """Create new project."""
        self.selected_action = "new"
        # Show simple new project dialog
        self._show_new_project_dialog()
    
    def _show_new_project_dialog(self):
        """Show inline new project dialog."""
        from PySide6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "New Project", "Project Name:")
        if ok and name:
            docs = os.path.join(os.path.expanduser("~"), "Documents", "GameProjects")
            os.makedirs(docs, exist_ok=True)
            self.selected_path = os.path.join(docs, name)
            self.accept()
    
    def _on_import_project(self):
        """Import existing project."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Project", "", "Project Files (*.Game)"
        )
        if path:
            self.selected_action = "open"
            self.selected_path = path
            self.accept()
    
    def _on_delete_project(self):
        """Delete selected project."""
        if not self._selected_project:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Select Project", "Please select a project first")
            return
        
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, "Delete Project",
            f"Are you sure you want to delete this project?\n{self._selected_project}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                import shutil
                project_dir = os.path.dirname(self._selected_project)
                if os.path.exists(project_dir):
                    shutil.rmtree(project_dir)
                # Remove from recent
                if self._selected_project in self._recent_paths:
                    self._recent_paths.remove(self._selected_project)
                self._load_projects()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete: {e}")
    
    def _on_remove_project(self):
        """Remove selected project from list (not delete files)."""
        if not self._selected_project:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Select Project", "Please select a project first")
            return
        
        if self._selected_project in self._recent_paths:
            self._recent_paths.remove(self._selected_project)
        self._load_projects()
    
    def _check_recovery(self) -> bool:
        """Check if there are any recovery files from a crash."""
        recovery_dir = Path(".Recovery")
        if not recovery_dir.exists():
            return False
        flag_file = recovery_dir / ".crash_flag"
        return flag_file.exists()

    def _recover_session(self) -> None:
        """Handle recover session action."""
        self.selected_action = "recover_session"
        self.accept()
