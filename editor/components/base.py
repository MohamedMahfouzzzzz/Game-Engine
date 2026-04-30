# /**************************************************************************/
# /*  components/base.py                                                    */
# /**************************************************************************/

"""Editor base components - Styled widgets following design system."""

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QPushButton, QLineEdit, QComboBox, QLabel, QGroupBox,
    QScrollArea, QWidget, QVBoxLayout
)

from ..theme import EditorColors, EditorFonts, EditorSpacing


class EditorButton(QPushButton):
    """Base styled button following editor design system."""
    
    def __init__(self, text: str = "", icon: QIcon = None, parent=None):
        super().__init__(text, parent)
        
        self.setFixedHeight(EditorSpacing.BUTTON_HEIGHT)
        self.setFont(EditorFonts.button_text())
        
        if icon:
            self.setIcon(icon)
            self.setIconSize(QSize(EditorSpacing.ICON_SIZE_SM, EditorSpacing.ICON_SIZE_SM))
        
        self._apply_base_style()
    
    def _apply_base_style(self):
        """Apply base button stylesheet."""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BUTTON_SECONDARY_BG)};
                border: 1px solid {EditorColors.to_stylesheet(EditorColors.BORDER_DEFAULT)};
                color: {EditorColors.to_stylesheet(EditorColors.TEXT_PRIMARY)};
                padding: 4px 16px;
                border-radius: {EditorSpacing.RADIUS_SM}px;
            }}
            QPushButton:hover {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BUTTON_SECONDARY_HOVER)};
                border: 1px solid {EditorColors.to_stylesheet(EditorColors.BORDER_FOCUS)};
            }}
            QPushButton:pressed {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_PRESSED)};
            }}
            QPushButton:disabled {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_SECONDARY)};
                color: {EditorColors.to_stylesheet(EditorColors.TEXT_DISABLED)};
                border: 1px solid {EditorColors.to_stylesheet(EditorColors.BORDER_DEFAULT)};
            }}
        """)


class EditorPrimaryButton(EditorButton):
    """Primary action button (blue accent)."""
    
    def __init__(self, text: str = "", icon: QIcon = None, parent=None):
        super().__init__(text, icon, parent)
        self._apply_primary_style()
    
    def _apply_primary_style(self):
        """Apply primary button stylesheet."""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BUTTON_PRIMARY_BG)};
                border: 1px solid {EditorColors.to_stylesheet(EditorColors.BUTTON_PRIMARY_BG)};
                color: white;
                padding: 4px 16px;
                border-radius: {EditorSpacing.RADIUS_SM}px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BUTTON_PRIMARY_HOVER)};
                border: 1px solid {EditorColors.to_stylesheet(EditorColors.BUTTON_PRIMARY_HOVER)};
            }}
            QPushButton:pressed {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BUTTON_PRIMARY_PRESSED)};
            }}
            QPushButton:disabled {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_SECONDARY)};
                color: {EditorColors.to_stylesheet(EditorColors.TEXT_DISABLED)};
                border: 1px solid {EditorColors.to_stylesheet(EditorColors.BORDER_DEFAULT)};
            }}
        """)


class EditorSecondaryButton(EditorButton):
    """Secondary action button (default style)."""
    pass


class EditorDangerButton(EditorButton):
    """Danger/destructive action button (red)."""
    
    def __init__(self, text: str = "", icon: QIcon = None, parent=None):
        super().__init__(text, icon, parent)
        self._apply_danger_style()
    
    def _apply_danger_style(self):
        """Apply danger button stylesheet."""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BUTTON_DANGER_BG)};
                border: 1px solid {EditorColors.to_stylesheet(EditorColors.BUTTON_DANGER_BG)};
                color: white;
                padding: 4px 16px;
                border-radius: {EditorSpacing.RADIUS_SM}px;
            }}
            QPushButton:hover {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BUTTON_DANGER_HOVER)};
                border: 1px solid {EditorColors.to_stylesheet(EditorColors.BUTTON_DANGER_HOVER)};
            }}
            QPushButton:pressed {{
                background-color: {EditorColors.to_stylesheet(EditorColors.ERROR)};
            }}
        """)


class EditorIconButton(QPushButton):
    """Icon-only button (toolbar style)."""
    
    def __init__(self, icon: QIcon, tooltip: str = "", parent=None):
        super().__init__(parent)
        
        self.setFixedSize(EditorSpacing.BUTTON_HEIGHT, EditorSpacing.BUTTON_HEIGHT)
        self.setIcon(icon)
        self.setIconSize(QSize(EditorSpacing.ICON_SIZE_LG, EditorSpacing.ICON_SIZE_LG))
        self.setToolTip(tooltip)
        self.setFlat(True)
        
        self._apply_icon_style()
    
    def _apply_icon_style(self):
        """Apply icon button stylesheet."""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                padding: 2px;
                border-radius: {EditorSpacing.RADIUS_SM}px;
            }}
            QPushButton:hover {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_HOVER)};
            }}
            QPushButton:pressed {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_PRESSED)};
            }}
            QPushButton:checked {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_SELECTED)};
            }}
        """)


class EditorInput(QLineEdit):
    """Styled text input following design system."""
    
    def __init__(self, placeholder: str = "", parent=None):
        super().__init__(parent)
        
        self.setFixedHeight(EditorSpacing.INPUT_HEIGHT)
        self.setFont(EditorFonts.input_text())
        self.setPlaceholderText(placeholder)
        
        self._apply_style()
    
    def _apply_style(self):
        """Apply input stylesheet."""
        self.setStyleSheet(f"""
            QLineEdit {{
                background-color: {EditorColors.to_stylesheet(EditorColors.INPUT_BG)};
                border: 1px solid {EditorColors.to_stylesheet(EditorColors.INPUT_BORDER)};
                color: {EditorColors.to_stylesheet(EditorColors.TEXT_PRIMARY)};
                padding: 4px 8px;
                border-radius: {EditorSpacing.RADIUS_SM}px;
            }}
            QLineEdit:focus {{
                border: 1px solid {EditorColors.to_stylesheet(EditorColors.INPUT_BORDER_FOCUS)};
            }}
            QLineEdit:disabled {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_SECONDARY)};
                color: {EditorColors.to_stylesheet(EditorColors.TEXT_DISABLED)};
            }}
            QLineEdit::placeholder {{
                color: {EditorColors.to_stylesheet(EditorColors.TEXT_DISABLED)};
            }}
        """)


class EditorComboBox(QComboBox):
    """Styled dropdown following design system."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setFixedHeight(EditorSpacing.INPUT_HEIGHT)
        self.setFont(EditorFonts.input_text())
        
        self._apply_style()
    
    def _apply_style(self):
        """Apply combobox stylesheet."""
        self.setStyleSheet(f"""
            QComboBox {{
                background-color: {EditorColors.to_stylesheet(EditorColors.INPUT_BG)};
                border: 1px solid {EditorColors.to_stylesheet(EditorColors.INPUT_BORDER)};
                color: {EditorColors.to_stylesheet(EditorColors.TEXT_PRIMARY)};
                padding: 4px 8px;
                border-radius: {EditorSpacing.RADIUS_SM}px;
                min-width: 80px;
            }}
            QComboBox:hover {{
                border: 1px solid {EditorColors.to_stylesheet(EditorColors.BORDER_FOCUS)};
            }}
            QComboBox:focus {{
                border: 1px solid {EditorColors.to_stylesheet(EditorColors.INPUT_BORDER_FOCUS)};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {EditorColors.to_stylesheet(EditorColors.TEXT_SECONDARY)};
                margin-top: 2px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_SECONDARY)};
                border: 1px solid {EditorColors.to_stylesheet(EditorColors.BORDER_DEFAULT)};
                color: {EditorColors.to_stylesheet(EditorColors.TEXT_PRIMARY)};
                selection-background-color: {EditorColors.to_stylesheet(EditorColors.BG_SELECTED)};
            }}
        """)


class EditorLabel(QLabel):
    """Styled label following design system."""
    
    def __init__(self, text: str = "", is_secondary: bool = False, parent=None):
        super().__init__(text, parent)
        
        self.setFont(EditorFonts.label_small())
        
        if is_secondary:
            self.setStyleSheet(f"color: {EditorColors.to_stylesheet(EditorColors.TEXT_SECONDARY)};")
        else:
            self.setStyleSheet(f"color: {EditorColors.to_stylesheet(EditorColors.TEXT_PRIMARY)};")


class EditorGroupBox(QGroupBox):
    """Styled group box following design system."""
    
    def __init__(self, title: str = "", parent=None):
        super().__init__(title, parent)
        
        self.setFont(EditorFonts.section_heading())
        
        self._apply_style()
    
    def _apply_style(self):
        """Apply group box stylesheet."""
        self.setStyleSheet(f"""
            QGroupBox {{
                background-color: transparent;
                border: 1px solid {EditorColors.to_stylesheet(EditorColors.BORDER_DEFAULT)};
                border-radius: {EditorSpacing.RADIUS_MD}px;
                margin-top: 12px;
                padding-top: 8px;
                font-weight: 600;
                color: {EditorColors.to_stylesheet(EditorColors.TEXT_PRIMARY)};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px;
                color: {EditorColors.to_stylesheet(EditorColors.TEXT_SECONDARY)};
            }}
        """)


class EditorScrollArea(QScrollArea):
    """Styled scroll area following design system."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self._apply_style()
    
    def _apply_style(self):
        """Apply scroll area stylesheet."""
        self.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                background: {EditorColors.to_stylesheet(EditorColors.BG_SECONDARY)};
                width: {EditorSpacing.SCROLLBAR_WIDTH}px;
                border-radius: {EditorSpacing.RADIUS_SM}px;
            }}
            QScrollBar::handle:vertical {{
                background: {EditorColors.to_stylesheet(EditorColors.BG_TERTIARY)};
                min-height: 30px;
                border-radius: {EditorSpacing.RADIUS_SM}px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {EditorColors.to_stylesheet(EditorColors.BG_HOVER)};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)
