# /**************************************************************************/
# /*  editor_log.py                                                          */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Editor logging system - Python port of Godot's editor logging.

Provides logging functionality for editor operations and debugging.
"""

from typing import List, Dict, Any, Optional
from enum import Enum
import logging
from datetime import datetime

from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QComboBox,
    QPushButton, QLabel, QCheckBox, QFrame
)

from .theme import EditorColors, EditorFonts, EditorSpacing
from .components import EditorPrimaryButton, EditorSecondaryButton


class LogLevel(Enum):
    """Log message levels."""
    INFO = "INFO"
    WARNING = "WARNING" 
    ERROR = "ERROR"
    DEBUG = "DEBUG"


class LogMessage:
    """Log message entry."""
    
    def __init__(self, level: LogLevel, message: str, category: str = "General"):
        self.level = level
        self.message = message
        self.category = category
        self.timestamp = datetime.now()
    
    def to_string(self) -> str:
        """Convert log message to string."""
        time_str = self.timestamp.strftime("%H:%M:%S")
        return f"[{time_str}] [{self.level.value}] {self.category}: {self.message}"


class EditorLog(QObject):
    """Editor logging system."""
    
    message_logged = Signal(LogMessage)  # Emitted when new message is logged
    
    def __init__(self):
        super().__init__()
        self.messages: List[LogMessage] = []
        self.max_messages = 1000  # Maximum messages to keep
        self.categories: Dict[str, bool] = {"General": True}  # Category visibility
        
        # Setup Python logging
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Setup Python logging handler."""
        self.logger = logging.getLogger("editor")
        self.logger.setLevel(logging.DEBUG)
        
        # Create handler
        handler = EditorLogHandler(self)
        handler.setLevel(logging.DEBUG)
        
        # Add formatter
        formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        # Add to logger
        self.logger.addHandler(handler)
    
    def log(self, level: LogLevel, message: str, category: str = "General") -> None:
        """Log a message."""
        log_message = LogMessage(level, message, category)
        
        # Add to messages list
        self.messages.append(log_message)
        
        # Limit message count
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
        
        # Emit signal
        self.message_logged.emit(log_message)
        
        # Also use Python logging
        if level == LogLevel.DEBUG:
            self.logger.debug(message)
        elif level == LogLevel.INFO:
            self.logger.info(message)
        elif level == LogLevel.WARNING:
            self.logger.warning(message)
        elif level == LogLevel.ERROR:
            self.logger.error(message)
    
    def info(self, message: str, category: str = "General") -> None:
        """Log info message."""
        self.log(LogLevel.INFO, message, category)
    
    def warning(self, message: str, category: str = "General") -> None:
        """Log warning message."""
        self.log(LogLevel.WARNING, message, category)
    
    def error(self, message: str, category: str = "General") -> None:
        """Log error message."""
        self.log(LogLevel.ERROR, message, category)
    
    def debug(self, message: str, category: str = "General") -> None:
        """Log debug message."""
        self.log(LogLevel.DEBUG, message, category)
    
    def clear(self) -> None:
        """Clear all messages."""
        self.messages.clear()
    
    def get_messages(self, level_filter: Optional[LogLevel] = None, 
                     category_filter: Optional[str] = None) -> List[LogMessage]:
        """Get filtered messages."""
        filtered_messages = self.messages
        
        if level_filter:
            filtered_messages = [m for m in filtered_messages if m.level == level_filter]
        
        if category_filter:
            filtered_messages = [m for m in filtered_messages if m.category == category_filter]
        
        return filtered_messages
    
    def get_categories(self) -> List[str]:
        """Get all log categories."""
        categories = set()
        for message in self.messages:
            categories.add(message.category)
        return sorted(list(categories))
    
    def set_category_visible(self, category: str, visible: bool) -> None:
        """Set category visibility."""
        self.categories[category] = visible
    
    def is_category_visible(self, category: str) -> bool:
        """Check if category is visible."""
        return self.categories.get(category, True)


class EditorLogHandler(logging.Handler):
    """Custom logging handler for editor log."""
    
    def __init__(self, editor_log: EditorLog):
        super().__init__()
        self.editor_log = editor_log
    
    def emit(self, record: logging.LogRecord) -> None:
        """Emit log record."""
        try:
            message = self.format(record)
            
            # Map logging levels to editor log levels
            if record.levelno >= logging.ERROR:
                level = LogLevel.ERROR
            elif record.levelno >= logging.WARNING:
                level = LogLevel.WARNING
            elif record.levelno >= logging.INFO:
                level = LogLevel.INFO
            else:
                level = LogLevel.DEBUG
            
            self.editor_log.log(level, message, "Python")
            
        except Exception:
            self.handleError(record)


class LogWidget(QWidget):
    """Widget for displaying log messages."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.editor_log = EditorLog()
        self.current_level_filter: Optional[LogLevel] = None
        self.current_category_filter: Optional[str] = None
        
        self._setup_ui()
        
        # Connect to log signals
        self.editor_log.message_logged.connect(self.on_message_logged)
    
    def _setup_ui(self) -> None:
        """Setup the log widget UI with design system styling."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(EditorSpacing.PANEL_MARGIN, EditorSpacing.PANEL_MARGIN,
                                 EditorSpacing.PANEL_MARGIN, EditorSpacing.PANEL_MARGIN)
        layout.setSpacing(EditorSpacing.MD)

        # Controls bar with modern styling
        controls_frame = QFrame()
        controls_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_SECONDARY)};
                border: 1px solid {EditorColors.to_stylesheet(EditorColors.BORDER_DEFAULT)};
                border-radius: {EditorSpacing.RADIUS_MD}px;
            }}
        """)
        controls_layout = QHBoxLayout(controls_frame)
        controls_layout.setContentsMargins(EditorSpacing.MD, EditorSpacing.SM,
                                          EditorSpacing.MD, EditorSpacing.SM)

        # Level filter
        level_label = QLabel("Level:")
        level_label.setFont(EditorFonts.label_small())
        level_label.setStyleSheet(f"color: {EditorColors.to_stylesheet(EditorColors.TEXT_SECONDARY)};")
        controls_layout.addWidget(level_label)

        self.level_combo = QComboBox()
        self.level_combo.addItems(["All", "INFO", "WARNING", "ERROR", "DEBUG"])
        self.level_combo.currentTextChanged.connect(self.on_level_filter_changed)
        self._style_combo(self.level_combo)
        controls_layout.addWidget(self.level_combo)

        controls_layout.addSpacing(EditorSpacing.MD)

        # Category filter
        category_label = QLabel("Category:")
        category_label.setFont(EditorFonts.label_small())
        category_label.setStyleSheet(f"color: {EditorColors.to_stylesheet(EditorColors.TEXT_SECONDARY)};")
        controls_layout.addWidget(category_label)

        self.category_combo = QComboBox()
        self.category_combo.addItems(["All"])
        self.category_combo.currentTextChanged.connect(self.on_category_filter_changed)
        self._style_combo(self.category_combo)
        controls_layout.addWidget(self.category_combo)

        controls_layout.addStretch()

        # Clear button
        self.clear_button = EditorSecondaryButton("🗑️ Clear")
        self.clear_button.clicked.connect(self.clear_log)
        controls_layout.addWidget(self.clear_button)

        layout.addWidget(controls_frame)

        # Log display with modern styling
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setMaximumBlockCount(1000)
        self._style_log_display()
        layout.addWidget(self.log_display)

    def _style_combo(self, combo: QComboBox) -> None:
        """Apply design system styling to combo box."""
        combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_TERTIARY)};
                border: 1px solid {EditorColors.to_stylesheet(EditorColors.BORDER_DEFAULT)};
                border-radius: {EditorSpacing.RADIUS_SM}px;
                padding: 4px 8px;
                color: {EditorColors.to_stylesheet(EditorColors.TEXT_PRIMARY)};
                min-width: 100px;
            }}
            QComboBox:hover {{
                border-color: {EditorColors.to_stylesheet(EditorColors.BORDER_FOCUS)};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_SECONDARY)};
                border: 1px solid {EditorColors.to_stylesheet(EditorColors.BORDER_DEFAULT)};
                selection-background-color: {EditorColors.to_stylesheet(EditorColors.BG_SELECTED)};
            }}
        """)
        combo.setFont(EditorFonts.body_text())

    def _style_log_display(self) -> None:
        """Apply design system styling to log display."""
        self.log_display.setStyleSheet(f"""
            QTextEdit {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_SECONDARY)};
                border: 1px solid {EditorColors.to_stylesheet(EditorColors.BORDER_DEFAULT)};
                border-radius: {EditorSpacing.RADIUS_MD}px;
                color: {EditorColors.to_stylesheet(EditorColors.TEXT_PRIMARY)};
                font-family: "{EditorFonts._get_mono_font_family()}";
                font-size: {EditorFonts.SIZE_SM}pt;
                padding: 8px;
            }}
        """)
        self.log_display.setFont(EditorFonts.code_text())
    
    def on_message_logged(self, message: LogMessage) -> None:
        """Handle new log message."""
        if self._should_show_message(message):
            self.log_display.append(message.to_string())
    
    def _should_show_message(self, message: LogMessage) -> bool:
        """Check if message should be displayed."""
        # Check level filter
        if self.current_level_filter and message.level != self.current_level_filter:
            return False
        
        # Check category filter
        if self.current_category_filter and message.category != self.current_category_filter:
            return False
        
        # Check category visibility
        if not self.editor_log.is_category_visible(message.category):
            return False
        
        return True
    
    def on_level_filter_changed(self, text: str) -> None:
        """Handle level filter change."""
        if text == "All":
            self.current_level_filter = None
        else:
            self.current_level_filter = LogLevel(text)
        
        self.refresh_display()
    
    def on_category_filter_changed(self, text: str) -> None:
        """Handle category filter change."""
        if text == "All":
            self.current_category_filter = None
        else:
            self.current_category_filter = text
        
        self.refresh_display()
    
    def refresh_display(self) -> None:
        """Refresh the log display."""
        self.log_display.clear()
        
        for message in self.editor_log.get_messages(
            self.current_level_filter, 
            self.current_category_filter
        ):
            if self._should_show_message(message):
                self.log_display.append(message.to_string())
        
        # Update category combo
        self._update_category_combo()
    
    def _update_category_combo(self) -> None:
        """Update category combo box."""
        categories = self.editor_log.get_categories()
        current_text = self.category_combo.currentText()
        
        self.category_combo.clear()
        self.category_combo.addItems(["All"] + categories)
        
        # Restore selection
        index = self.category_combo.findText(current_text)
        if index >= 0:
            self.category_combo.setCurrentIndex(index)
    
    def clear_log(self) -> None:
        """Clear the log."""
        self.editor_log.clear()
        self.log_display.clear()
    
    def log_message(self, level: LogLevel, message: str, category: str = "General") -> None:
        """Log a message."""
        self.editor_log.log(level, message, category)
