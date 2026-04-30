# /**************************************************************************/
# /*  theme/typography.py                                                   */
# /**************************************************************************/

"""Editor typography system - Font sizes, weights, and styles."""

import sys
from PySide6.QtGui import QFont


class EditorFonts:
    """Typography design tokens for consistent text styling.
    
    Uses system fonts for native look on each platform:
    - Windows: Segoe UI
    - macOS: SF Pro
    - Linux: Roboto
    """
    
    # ==================== Font Families ====================
    @staticmethod
    def _get_ui_font_family() -> str:
        """Get appropriate UI font for current platform."""
        if sys.platform == "win32":
            return "Segoe UI"
        elif sys.platform == "darwin":
            return ".SF Pro Text"
        else:
            return "Roboto"
    
    @staticmethod
    def _get_mono_font_family() -> str:
        """Get appropriate monospace font for current platform."""
        if sys.platform == "win32":
            return "Consolas"
        elif sys.platform == "darwin":
            return "SF Mono"
        else:
            return "JetBrains Mono"
    
    @staticmethod
    def _get_heading_font_family() -> str:
        """Get heading font family."""
        if sys.platform == "win32":
            return "Segoe UI"
        elif sys.platform == "darwin":
            return ".SF Pro Display"
        else:
            return "Roboto"
    
    # Font family constants
    UI_FONT = property(lambda self: self._get_ui_font_family())
    MONO_FONT = property(lambda self: self._get_mono_font_family())
    HEADING_FONT = property(lambda self: self._get_heading_font_family())
    
    # ==================== Font Sizes (points) ====================
    # Base unit = 11pt (readable for most users)
    
    SIZE_2XS = 8       # Very small (status indicators, badges)
    SIZE_XS = 9        # Extra small (labels, timestamps)
    SIZE_SM = 10       # Small (compact UI elements)
    SIZE_MD = 11       # Medium - DEFAULT (body text, inputs)
    SIZE_LG = 12       # Large (minor headings)
    SIZE_XL = 13       # Extra large (section headings)
    SIZE_2XL = 14      # 2X large (dock titles)
    SIZE_3XL = 16      # 3X large (dialog titles)
    SIZE_4XL = 18      # 4X large (window titles)
    
    # ==================== Font Weights ====================
    WEIGHT_LIGHT = QFont.Weight.Light       # 25
    WEIGHT_NORMAL = QFont.Weight.Normal     # 400
    WEIGHT_MEDIUM = QFont.Weight.Medium   # 500
    WEIGHT_SEMIBOLD = QFont.Weight.DemiBold # 600
    WEIGHT_BOLD = QFont.Weight.Bold         # 700
    
    # ==================== Preset Font Getters ====================
    @classmethod
    def get_ui_font(cls, size: int = None, weight: QFont.Weight = None) -> QFont:
        """Get UI font with specified size and weight."""
        font = QFont(cls._get_ui_font_family())
        font.setPointSize(size if size is not None else cls.SIZE_MD)
        font.setWeight(weight if weight is not None else cls.WEIGHT_NORMAL)
        return font
    
    @classmethod
    def get_mono_font(cls, size: int = None, weight: QFont.Weight = None) -> QFont:
        """Get monospace font for code/technical text."""
        font = QFont(cls._get_mono_font_family())
        font.setPointSize(size if size is not None else cls.SIZE_MD)
        font.setWeight(weight if weight is not None else cls.WEIGHT_NORMAL)
        return font
    
    @classmethod
    def get_heading_font(cls, size: int = None, weight: QFont.Weight = None) -> QFont:
        """Get heading font for titles and headings."""
        font = QFont(cls._get_heading_font_family())
        font.setPointSize(size if size is not None else cls.SIZE_LG)
        font.setWeight(weight if weight is not None else cls.WEIGHT_SEMIBOLD)
        return font
    
    # ==================== Convenience Methods ====================
    @classmethod
    def dock_title(cls) -> QFont:
        """Font for dock widget titles."""
        return cls.get_heading_font(cls.SIZE_2XL, cls.WEIGHT_SEMIBOLD)
    
    @classmethod
    def section_heading(cls) -> QFont:
        """Font for section headings in inspector/panels."""
        return cls.get_heading_font(cls.SIZE_LG, cls.WEIGHT_MEDIUM)
    
    @classmethod
    def body_text(cls) -> QFont:
        """Font for body text (default)."""
        return cls.get_ui_font(cls.SIZE_MD, cls.WEIGHT_NORMAL)
    
    @classmethod
    def label_small(cls) -> QFont:
        """Font for small labels."""
        return cls.get_ui_font(cls.SIZE_XS, cls.WEIGHT_NORMAL)
    
    @classmethod
    def code_text(cls) -> QFont:
        """Font for code snippets, paths, technical values."""
        return cls.get_mono_font(cls.SIZE_SM, cls.WEIGHT_NORMAL)
    
    @classmethod
    def button_text(cls) -> QFont:
        """Font for button text."""
        return cls.get_ui_font(cls.SIZE_MD, cls.WEIGHT_MEDIUM)
    
    @classmethod
    def input_text(cls) -> QFont:
        """Font for input fields."""
        return cls.get_ui_font(cls.SIZE_MD, cls.WEIGHT_NORMAL)
    
    @classmethod
    def node_tree_item(cls) -> QFont:
        """Font for scene tree items."""
        return cls.get_ui_font(cls.SIZE_MD, cls.WEIGHT_NORMAL)
    
    @classmethod
    def status_text(cls) -> QFont:
        """Font for status bar text."""
        return cls.get_ui_font(cls.SIZE_SM, cls.WEIGHT_NORMAL)
    
    @classmethod
    def tooltip_text(cls) -> QFont:
        """Font for tooltips."""
        return cls.get_ui_font(cls.SIZE_SM, cls.WEIGHT_NORMAL)
    
    @classmethod
    def dialog_title(cls) -> QFont:
        """Font for dialog titles."""
        return cls.get_heading_font(cls.SIZE_3XL, cls.WEIGHT_SEMIBOLD)
    
    @classmethod
    def property_name(cls) -> QFont:
        """Font for property names in inspector."""
        return cls.get_ui_font(cls.SIZE_SM, cls.WEIGHT_NORMAL)
    
    @classmethod
    def property_value(cls) -> QFont:
        """Font for property values in inspector."""
        return cls.get_mono_font(cls.SIZE_SM, cls.WEIGHT_NORMAL)
    
    @classmethod
    def menu_item(cls) -> QFont:
        """Font for menu items."""
        return cls.get_ui_font(cls.SIZE_MD, cls.WEIGHT_NORMAL)
    
    @classmethod
    def menu_shortcut(cls) -> QFont:
        """Font for menu shortcuts."""
        return cls.get_mono_font(cls.SIZE_XS, cls.WEIGHT_NORMAL)

    @classmethod
    def empty_state(cls) -> QFont:
        """Font for empty state messages."""
        return cls.get_ui_font(cls.SIZE_LG, cls.WEIGHT_NORMAL)
