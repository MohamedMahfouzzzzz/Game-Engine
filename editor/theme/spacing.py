# /**************************************************************************/
# /*  theme/spacing.py                                                      */
# /**************************************************************************/

"""Editor spacing system - Consistent spacing and sizing."""


class EditorSpacing:
    """Spacing design tokens for consistent layout.
    
    Based on 8px grid system for harmonious proportions.
    """
    
    # ==================== Base Unit ====================
    UNIT = 8  # Base unit in pixels
    
    # ==================== Spacing Scale ====================
    # Use these for margins, padding, gaps
    
    XS = UNIT // 2              # 4px  - Tight spacing
    SM = UNIT                   # 8px  - Default element spacing
    MD = UNIT * 2               # 16px - Section spacing
    LG = UNIT * 3               # 24px - Large gaps
    XL = UNIT * 4               # 32px - Major sections
    XXL = UNIT * 6              # 48px - Dialog spacing
    
    # ==================== Component Heights ====================
    # Standard heights for consistent sizing
    
    BUTTON_HEIGHT = 28          # Standard button
    BUTTON_HEIGHT_SMALL = 24      # Compact button
    BUTTON_HEIGHT_LARGE = 32    # Prominent button
    
    INPUT_HEIGHT = 28           # Standard input
    INPUT_HEIGHT_SMALL = 24     # Compact input
    INPUT_HEIGHT_LARGE = 32     # Large input (textarea-like)
    
    ROW_HEIGHT = 28             # List/tree row height
    ROW_HEIGHT_SMALL = 24       # Compact list row
    ROW_HEIGHT_LARGE = 32       # Large list row
    
    TOOLBAR_HEIGHT = 40         # Main toolbar
    TOOLBAR_HEIGHT_SMALL = 32   # Compact toolbar
    
    DOCK_TITLE_HEIGHT = 32      # Dock widget title bar
    STATUS_BAR_HEIGHT = 24      # Status bar
    MENU_BAR_HEIGHT = 28        # Menu bar
    
    # ==================== Icon Sizes ====================
    ICON_SIZE_XS = 12           # Tree decorations
    ICON_SIZE_SM = 16           # Default icon (buttons, lists)
    ICON_SIZE_MD = 20           # Medium icons
    ICON_SIZE_LG = 24           # Toolbar icons
    ICON_SIZE_XL = 32           # Large icons (welcome screen)
    
    # ==================== Panel Dimensions ====================
    # Minimum/maximum sizes for panels
    
    DOCK_MIN_WIDTH = 240
    DOCK_MAX_WIDTH = 400
    DOCK_DEFAULT_WIDTH = 280
    
    DOCK_MIN_HEIGHT = 200
    DOCK_MAX_HEIGHT = 800
    
    INSPECTOR_MIN_WIDTH = 240
    INSPECTOR_MAX_WIDTH = 360
    INSPECTOR_DEFAULT_WIDTH = 280
    
    SCENE_TREE_MIN_WIDTH = 200
    SCENE_TREE_MAX_WIDTH = 400
    SCENE_TREE_DEFAULT_WIDTH = 240
    
    FILE_BROWSER_MIN_WIDTH = 240
    FILE_BROWSER_MAX_WIDTH = 400
    
    # ==================== Layout Margins ====================
    # Standard margins for different contexts
    
    DIALOG_MARGIN = 24          # Dialog content margin
    PANEL_MARGIN = 16           # Panel content margin
    SECTION_MARGIN = 16         # Between sections
    ITEM_MARGIN = 8             # Between items in a list
    
    # ==================== Border Radius ====================
    # For rounded corners (if enabled)
    
    RADIUS_NONE = 0
    RADIUS_SM = 2               # Inputs, small buttons
    RADIUS_MD = 4               # Buttons, cards
    RADIUS_LG = 6               # Dialogs, large panels
    
    # ==================== Splitter Sizes ====================
    SPLITTER_WIDTH = 4          # QSplitter handle width
    
    # ==================== Scrollbar Sizes ====================
    SCROLLBAR_WIDTH = 14        # Scrollbar thickness
    
    # ==================== Helper Methods ====================
    @classmethod
    def scale(cls, multiplier: float) -> int:
        """Get scaled spacing value."""
        return int(cls.UNIT * multiplier)
    
    @classmethod
    def margin_css(cls, top: int = None, right: int = None, 
                   bottom: int = None, left: int = None) -> str:
        """Generate CSS margin string."""
        t = top if top is not None else cls.SM
        r = right if right is not None else cls.SM
        b = bottom if bottom is not None else cls.SM
        l = left if left is not None else cls.SM
        return f"{t}px {r}px {b}px {l}px"
    
    @classmethod
    def padding_css(cls, top: int = None, right: int = None,
                    bottom: int = None, left: int = None) -> str:
        """Generate CSS padding string."""
        t = top if top is not None else cls.SM
        r = right if right is not None else cls.SM
        b = bottom if bottom is not None else cls.SM
        l = left if left is not None else cls.SM
        return f"{t}px {r}px {b}px {l}px"
