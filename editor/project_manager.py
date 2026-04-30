# /**************************************************************************/
# /*  project_manager.py                                                    */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Project manager - Modern welcome screen with design system.

Features:
- Welcome screen with quick actions
- Clickable recent projects list
- Template previews
- Modern UI using design system
"""

from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime

from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon, QFont, QPixmap, QColor
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QMessageBox, QGroupBox, QFormLayout,
    QComboBox, QFrame, QScrollArea, QWidget, QGridLayout,
    QStackedWidget, QSizePolicy, QSpacerItem, QApplication
)

from engine.core.project_secure import SecureProject as Project
from .editor_data import EditorData
from .theme import EditorColors, EditorFonts, EditorSpacing
from .components import (
    EditorPrimaryButton, EditorSecondaryButton, EditorInput,
    EditorLabel, EditorIconButton, EditorGroupBox, EditorComboBox
)


class ProjectManager(QDialog):
    """Modern project manager with welcome screen."""
    
    project_selected = Signal(str)  # Emitted when project is selected
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Game Engine - Welcome")
        self.setModal(True)
        
        # Set size based on screen
        screen = QApplication.primaryScreen().geometry()
        if screen.width() >= 1920:
            self.resize(900, 650)
        else:
            self.resize(800, 600)
        
        self.project_path: Optional[str] = None
        self.editor_data = EditorData()
        self._recent_projects: List[str] = []
        
        self._setup_ui()
        self._apply_styles()
        self._load_recent_projects()
    
    def _setup_ui(self) -> None:
        """Setup modern welcome screen UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Left sidebar - branding and quick actions
        self.sidebar = self._create_sidebar()
        layout.addWidget(self.sidebar, 1)
        
        # Right content - recent projects and templates
        self.content = self._create_content_area()
        layout.addWidget(self.content, 2)
    
    def _create_sidebar(self) -> QWidget:
        """Create left sidebar with branding and quick actions."""
        sidebar = QWidget()
        sidebar.setMinimumWidth(280)
        sidebar.setMaximumWidth(320)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(EditorSpacing.LG, EditorSpacing.XL, 
                                   EditorSpacing.LG, EditorSpacing.LG)
        layout.setSpacing(EditorSpacing.MD)
        
        # Logo/Branding
        branding = QLabel("🎮 Game Engine")
        branding.setFont(EditorFonts.get_heading_font(EditorFonts.SIZE_3XL, 
                                                       EditorFonts.WEIGHT_BOLD))
        branding.setStyleSheet(f"color: {EditorColors.to_stylesheet(EditorColors.TEXT_PRIMARY)};")
        layout.addWidget(branding)
        
        version = QLabel("v1.0.0")
        version.setFont(EditorFonts.label_small())
        version.setStyleSheet(f"color: {EditorColors.to_stylesheet(EditorColors.TEXT_SECONDARY)};")
        layout.addWidget(version)
        
        layout.addSpacing(EditorSpacing.XL)
        
        # Quick Actions
        actions_label = QLabel("QUICK ACTIONS")
        actions_label.setFont(EditorFonts.label_small())
        actions_label.setStyleSheet(f"color: {EditorColors.to_stylesheet(EditorColors.TEXT_SECONDARY)};")
        layout.addWidget(actions_label)
        
        # New Project button
        self.new_btn = EditorPrimaryButton("  + New Project")
        self.new_btn.setIconSize(QSize(EditorSpacing.ICON_SIZE_MD, EditorSpacing.ICON_SIZE_MD))
        self.new_btn.clicked.connect(self._on_new_project)
        layout.addWidget(self.new_btn)
        
        # Open Project button
        self.open_btn = EditorSecondaryButton("  📂 Open Project")
        self.open_btn.setIconSize(QSize(EditorSpacing.ICON_SIZE_MD, EditorSpacing.ICON_SIZE_MD))
        self.open_btn.clicked.connect(self._on_open_project)
        layout.addWidget(self.open_btn)
        
        layout.addStretch()
        
        # Help links
        help_layout = QVBoxLayout()
        help_layout.setSpacing(EditorSpacing.XS)
        
        docs_link = QLabel("<a href='#' style='color: #4A9EFF; text-decoration: none;'>📖 Documentation</a>")
        docs_link.setFont(EditorFonts.label_small())
        docs_link.setOpenExternalLinks(True)
        help_layout.addWidget(docs_link)
        
        tutorials_link = QLabel("<a href='#' style='color: #4A9EFF; text-decoration: none;'>🎬 Tutorials</a>")
        tutorials_link.setFont(EditorFonts.label_small())
        tutorials_link.setOpenExternalLinks(True)
        help_layout.addWidget(tutorials_link)
        
        layout.addLayout(help_layout)
        
        return sidebar
    
    def _create_content_area(self) -> QWidget:
        """Create right content area with recent projects and templates."""
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(EditorSpacing.XL, EditorSpacing.XL,
                                   EditorSpacing.XL, EditorSpacing.XL)
        layout.setSpacing(EditorSpacing.XL)
        
        # Recent Projects Section
        recent_label = QLabel("Recent Projects")
        recent_label.setFont(EditorFonts.section_heading())
        layout.addWidget(recent_label)
        
        # Recent projects list
        self.recent_list = QWidget()
        self.recent_list_layout = QVBoxLayout(self.recent_list)
        self.recent_list_layout.setContentsMargins(0, 0, 0, 0)
        self.recent_list_layout.setSpacing(EditorSpacing.SM)
        
        # Scroll area for recent projects
        recent_scroll = QScrollArea()
        recent_scroll.setWidgetResizable(True)
        recent_scroll.setWidget(self.recent_list)
        recent_scroll.setMaximumHeight(200)
        recent_scroll.setFrameShape(QFrame.Shape.NoFrame)
        layout.addWidget(recent_scroll)
        
        # Empty state message
        self.empty_recent_label = QLabel("No recent projects. Create a new one or open an existing project.")
        self.empty_recent_label.setFont(EditorFonts.label_small())
        self.empty_recent_label.setStyleSheet(f"color: {EditorColors.to_stylesheet(EditorColors.TEXT_SECONDARY)}; padding: 20px;")
        self.empty_recent_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.empty_recent_label)
        
        layout.addSpacing(EditorSpacing.MD)
        
        # Templates Section
        templates_label = QLabel("Create from Template")
        templates_label.setFont(EditorFonts.section_heading())
        layout.addWidget(templates_label)
        
        # Templates grid
        templates_grid = QGridLayout()
        templates_grid.setSpacing(EditorSpacing.MD)
        
        templates = [
            ("Empty Project", "Start from scratch", "🎯"),
            ("2D Platformer", "Side-scrolling game", "🏃"),
            ("2D Top-Down", "Overhead view game", "🎲"),
            ("UI Project", "User interface focus", "🎨"),
        ]
        
        for i, (name, desc, icon) in enumerate(templates):
            template_card = self._create_template_card(name, desc, icon)
            templates_grid.addWidget(template_card, i // 2, i % 2)
        
        layout.addLayout(templates_grid)
        layout.addStretch()
        
        return content
    
    def _create_template_card(self, name: str, description: str, icon: str) -> QFrame:
        """Create a template selection card."""
        card = QFrame()
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setMinimumHeight(100)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(EditorSpacing.MD, EditorSpacing.MD,
                                   EditorSpacing.MD, EditorSpacing.MD)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setFont(EditorFonts.get_heading_font(EditorFonts.SIZE_3XL))
        layout.addWidget(icon_label)
        
        # Text
        text_layout = QVBoxLayout()
        
        name_label = QLabel(name)
        name_label.setFont(EditorFonts.get_ui_font(EditorFonts.SIZE_LG, 
                                                    EditorFonts.WEIGHT_MEDIUM))
        text_layout.addWidget(name_label)
        
        desc_label = QLabel(description)
        desc_label.setFont(EditorFonts.label_small())
        desc_label.setStyleSheet(f"color: {EditorColors.to_stylesheet(EditorColors.TEXT_SECONDARY)};")
        text_layout.addWidget(desc_label)
        
        layout.addLayout(text_layout, 1)
        layout.addStretch()
        
        # Style
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_SECONDARY)};
                border: 2px solid {EditorColors.to_stylesheet(EditorColors.BORDER_DEFAULT)};
                border-radius: {EditorSpacing.RADIUS_MD}px;
            }}
            QFrame:hover {{
                border: 2px solid {EditorColors.to_stylesheet(EditorColors.BORDER_FOCUS)};
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_HOVER)};
            }}
        """)
        
        # Click handler
        card.mousePressEvent = lambda e: self._on_template_selected(name)
        
        return card
    
    def _create_project_item(self, project_path: str) -> QFrame:
        """Create a clickable recent project item."""
        path_obj = Path(project_path)
        name = path_obj.stem
        
        # Get modification time
        try:
            mtime = path_obj.stat().st_mtime
            date_str = datetime.fromtimestamp(mtime).strftime("%b %d, %Y")
        except:
            date_str = "Unknown date"
        
        item = QFrame()
        item.setFrameShape(QFrame.Shape.NoFrame)
        item.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QHBoxLayout(item)
        layout.setContentsMargins(EditorSpacing.MD, EditorSpacing.SM,
                                   EditorSpacing.MD, EditorSpacing.SM)
        
        # Project icon
        icon_label = QLabel("📁")
        icon_label.setFont(EditorFonts.get_heading_font(EditorFonts.SIZE_LG))
        layout.addWidget(icon_label)
        
        # Project info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(EditorSpacing.XS)
        
        name_label = QLabel(name)
        name_label.setFont(EditorFonts.get_ui_font(EditorFonts.SIZE_LG,
                                                    EditorFonts.WEIGHT_MEDIUM))
        info_layout.addWidget(name_label)
        
        path_label = QLabel(str(path_obj.parent))
        path_label.setFont(EditorFonts.label_small())
        path_label.setStyleSheet(f"color: {EditorColors.to_stylesheet(EditorColors.TEXT_SECONDARY)};")
        path_label.setToolTip(project_path)
        info_layout.addWidget(path_label)
        
        layout.addLayout(info_layout, 1)
        
        # Date
        date_label = QLabel(date_str)
        date_label.setFont(EditorFonts.label_small())
        date_label.setStyleSheet(f"color: {EditorColors.to_stylesheet(EditorColors.TEXT_SECONDARY)};")
        layout.addWidget(date_label)
        
        # Style
        item.setStyleSheet(f"""
            QFrame {{
                background-color: transparent;
                border-radius: {EditorSpacing.RADIUS_SM}px;
            }}
            QFrame:hover {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_HOVER)};
            }}
        """)
        
        # Click handler
        item.mousePressEvent = lambda e: self._on_recent_project_clicked(project_path)
        
        return item
    
    def _apply_styles(self) -> None:
        """Apply dark theme styles to dialog."""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_PRIMARY)};
            }}
            QWidget {{
                background-color: transparent;
            }}
        """)
    
    def _load_recent_projects(self) -> None:
        """Load and display recent projects."""
        self._recent_projects = self.editor_data.get_recent_projects()[:10]
        
        # Clear existing items
        while self.recent_list_layout.count():
            item = self.recent_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if self._recent_projects:
            self.empty_recent_label.hide()
            for project_path in self._recent_projects:
                project_item = self._create_project_item(project_path)
                self.recent_list_layout.addWidget(project_item)
        else:
            self.empty_recent_label.show()
    
    def _on_recent_project_clicked(self, project_path: str) -> None:
        """Handle click on recent project."""
        self._load_project(project_path)
    
    def _on_new_project(self) -> None:
        """Handle new project button."""
        dialog = NewProjectDialog(self)
        if dialog.exec() == QDialog.Accepted:
            project_path = dialog.get_project_path()
            if project_path:
                self._create_and_load_project(project_path)
    
    def _on_open_project(self) -> None:
        """Handle open project button."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Project", "", "Game Engine Project (*.ges)"
        )
        
        if file_path:
            self._load_project(file_path)
    
    def _on_template_selected(self, template_name: str) -> None:
        """Handle template selection."""
        dialog = NewProjectDialog(self, template_name)
        if dialog.exec() == QDialog.Accepted:
            project_path = dialog.get_project_path()
            if project_path:
                self._create_and_load_project(project_path, template_name)
    
    def _create_and_load_project(self, project_path: str, template: str = "Empty") -> None:
        """Create new project and load it."""
        try:
            project = Project.create_new(project_path)
            if project:
                self.project_path = project_path
                self.editor_data.add_recent_project(project_path)
                self.project_selected.emit(project_path)
                self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create project: {e}")
    
    def _load_project(self, project_path: str) -> None:
        """Load existing project."""
        try:
            project = Project.load_from_file_sync(project_path)
            if project:
                self.project_path = project_path
                self.editor_data.add_recent_project(project_path)
                self.project_selected.emit(project_path)
                self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open project: {e}")
    
    def get_project_path(self) -> Optional[str]:
        """Get the selected project path."""
        return self.project_path


class NewProjectDialog(QDialog):
    """Modern new project creation dialog."""
    
    def __init__(self, parent=None, template: str = "Empty"):
        super().__init__(parent)
        self.setWindowTitle("Create New Project")
        self.setModal(True)
        self.resize(550, 400)
        
        self.project_path: Optional[str] = None
        self.selected_template = template
        
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self) -> None:
        """Setup modern new project dialog."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(EditorSpacing.XL, EditorSpacing.XL,
                                   EditorSpacing.XL, EditorSpacing.XL)
        layout.setSpacing(EditorSpacing.LG)
        
        # Header
        header = QLabel("Create New Project")
        header.setFont(EditorFonts.dialog_title())
        layout.addWidget(header)
        
        # Project name
        name_layout = QVBoxLayout()
        name_layout.setSpacing(EditorSpacing.XS)
        
        name_label = QLabel("Project Name")
        name_label.setFont(EditorFonts.get_ui_font(EditorFonts.SIZE_SM,
                                                    EditorFonts.WEIGHT_MEDIUM))
        name_layout.addWidget(name_label)
        
        self.name_edit = EditorInput("My Awesome Game")
        self.name_edit.textChanged.connect(self._update_project_path)
        name_layout.addWidget(self.name_edit)
        
        layout.addLayout(name_layout)
        
        # Project location
        location_layout = QVBoxLayout()
        location_layout.setSpacing(EditorSpacing.XS)
        
        location_label = QLabel("Project Location")
        location_label.setFont(EditorFonts.get_ui_font(EditorFonts.SIZE_SM,
                                                        EditorFonts.WEIGHT_MEDIUM))
        location_layout.addWidget(location_label)
        
        path_layout = QHBoxLayout()
        path_layout.setSpacing(EditorSpacing.SM)
        
        self.path_edit = EditorInput()
        # Set default path
        default_path = Path.home() / "GameEngineProjects"
        default_path.mkdir(parents=True, exist_ok=True)
        self.path_edit.setText(str(default_path))
        
        path_layout.addWidget(self.path_edit)
        
        browse_btn = EditorSecondaryButton("Browse...")
        browse_btn.setFixedWidth(100)
        browse_btn.clicked.connect(self._browse_location)
        path_layout.addWidget(browse_btn)
        
        location_layout.addLayout(path_layout)
        layout.addLayout(location_layout)
        
        # Full path preview
        self.path_preview = QLabel()
        self.path_preview.setFont(EditorFonts.code_text())
        self.path_preview.setStyleSheet(f"color: {EditorColors.to_stylesheet(EditorColors.TEXT_SECONDARY)};")
        self.path_preview.setWordWrap(True)
        layout.addWidget(self.path_preview)
        
        # Template selection
        template_layout = QVBoxLayout()
        template_layout.setSpacing(EditorSpacing.SM)
        
        template_label = QLabel("Template")
        template_label.setFont(EditorFonts.get_ui_font(EditorFonts.SIZE_SM,
                                                        EditorFonts.WEIGHT_MEDIUM))
        template_layout.addWidget(template_label)
        
        self.template_combo = EditorComboBox()
        self.template_combo.addItems([
            "Empty Project",
            "2D Platformer",
            "2D Top-Down",
            "2D Puzzle",
            "UI Project"
        ])
        
        # Set selected template
        index = self.template_combo.findText(self.selected_template)
        if index >= 0:
            self.template_combo.setCurrentIndex(index)
        
        template_layout.addWidget(self.template_combo)
        layout.addLayout(template_layout)
        
        layout.addStretch()
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(EditorSpacing.MD)
        
        self.create_btn = EditorPrimaryButton("Create Project")
        self.create_btn.clicked.connect(self._create_project)
        buttons_layout.addWidget(self.create_btn)
        
        self.cancel_btn = EditorSecondaryButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(buttons_layout)
    
    def _apply_styles(self) -> None:
        """Apply dark theme styles."""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_PRIMARY)};
            }}
        """)
    
    def _update_project_path(self) -> None:
        """Update full path preview."""
        name = self.name_edit.text().strip() or "My Awesome Game"
        base_path = self.path_edit.text().strip()
        full_path = Path(base_path) / f"{name}.ges"
        self.path_preview.setText(str(full_path))
    
    def _browse_location(self) -> None:
        """Browse for project location."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Project Folder", self.path_edit.text()
        )
        if directory:
            self.path_edit.setText(directory)
            self._update_project_path()
            
            # Auto-fill name from directory if empty
            if not self.name_edit.text().strip():
                dir_name = Path(directory).name
                self.name_edit.setText(dir_name)
    
    def _create_project(self) -> None:
        """Create the project."""
        name = self.name_edit.text().strip()
        base_path = self.path_edit.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Required", "Please enter a project name")
            return
        
        if not base_path:
            QMessageBox.warning(self, "Required", "Please select a project location")
            return
        
        # Validate name
        if not name.replace("_", "").replace("-", "").replace(" ", "").isalnum():
            QMessageBox.warning(self, "Invalid Name",
                              "Project name can only contain letters, numbers, spaces, underscores, and hyphens")
            return
        
        # Clean name for filename
        file_name = name.replace(" ", "_")
        project_path = Path(base_path) / f"{file_name}.ges"
        
        # Check if exists
        if project_path.exists():
            reply = QMessageBox.question(
                self, "Project Exists",
                f"A project already exists at:\n{project_path}\n\nDo you want to overwrite it?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
        
        self.project_path = str(project_path)
        self.accept()
    
    def get_project_path(self) -> Optional[str]:
        """Get the created project path."""
        return self.project_path
