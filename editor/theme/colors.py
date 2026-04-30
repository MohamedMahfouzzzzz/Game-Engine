# /**************************************************************************/
# /*  theme/colors.py                                                       */
# /**************************************************************************/

"""Editor color system - Design tokens for consistent coloring."""

from PySide6.QtGui import QColor


class EditorColors:
    """Design token color palette for the editor.
    
    All colors follow a consistent dark theme suitable for long editing sessions.
    """
    
    # ==================== Backgrounds ====================
    BG_PRIMARY = QColor(30, 30, 30)        # Main window background
    BG_SECONDARY = QColor(40, 40, 40)     # Panels, docks
    BG_TERTIARY = QColor(50, 50, 50)      # Inputs, buttons
    BG_HOVER = QColor(60, 60, 60)         # Hover states
    BG_PRESSED = QColor(45, 45, 45)       # Pressed states
    BG_SELECTED = QColor(0, 120, 215)     # Selected items background
    
    # ==================== Viewport ====================
    VIEWPORT_BG = QColor(45, 45, 48)      # 2D viewport background
    VIEWPORT_BG_DARK = QColor(35, 35, 38) # Darker areas
    
    # Grid
    GRID_MAJOR = QColor(60, 60, 60)       # Major grid lines (every 10th)
    GRID_MINOR = QColor(50, 50, 50)       # Minor grid lines
    GRID_AXIS_X = QColor(255, 89, 89)    # X axis (soft red)
    GRID_AXIS_Y = QColor(145, 255, 117)  # Y axis (soft green)
    GRID_AXIS_Z = QColor(117, 145, 255)  # Z axis (soft blue)
    
    # ==================== Selection ====================
    SELECTED_OUTLINE = QColor(0, 150, 255)          # Selected node outline
    SELECTED_FILL = QColor(0, 150, 255, 40)       # Selected node fill (translucent)
    SELECTED_GLOW = QColor(0, 150, 255, 80)       # Selection glow
    
    HOVER_OUTLINE = QColor(255, 255, 255, 120)     # Hover outline
    HOVER_FILL = QColor(255, 255, 255, 20)        # Hover fill
    
    # ==================== Node Type Colors ====================
    # Used for node icons, outlines, and categorization
    NODE_GENERIC = QColor(200, 200, 200)          # Generic nodes (gray)
    NODE_SPRITE = QColor(100, 200, 255)          # Visual/Sprite nodes (blue)
    NODE_ANIMATION = QColor(255, 150, 100)       # Animation nodes (orange)
    NODE_PHYSICS = QColor(255, 200, 100)         # Physics nodes (yellow)
    NODE_COLLISION = QColor(255, 100, 100)       # Collision nodes (red)
    NODE_UI = QColor(200, 100, 255)              # UI nodes (purple)
    NODE_AUDIO = QColor(100, 255, 150)           # Audio nodes (green)
    NODE_CAMERA = QColor(255, 255, 100)          # Camera nodes (yellow)
    NODE_LIGHT = QColor(255, 255, 200)           # Light nodes (light yellow)
    NODE_PARTICLES = QColor(255, 150, 200)       # Particles nodes (pink)
    NODE_PATH = QColor(150, 255, 255)            # Path nodes (cyan)
    NODE_NAVIGATION = QColor(150, 200, 255)      # Navigation nodes (light blue)
    
    # ==================== Text ====================
    TEXT_PRIMARY = QColor(240, 240, 240)          # Main text
    TEXT_SECONDARY = QColor(180, 180, 180)       # Secondary text, labels
    TEXT_DISABLED = QColor(120, 120, 120)        # Disabled text
    TEXT_ACCENT = QColor(0, 150, 255)            # Accent text (links, highlights)
    TEXT_WARNING = QColor(255, 200, 100)         # Warning text
    TEXT_ERROR = QColor(255, 100, 100)           # Error text
    TEXT_SUCCESS = QColor(100, 255, 150)         # Success text
    
    # ==================== Borders ====================
    BORDER_DEFAULT = QColor(60, 60, 60)          # Default borders
    BORDER_FOCUS = QColor(0, 150, 255)           # Focused borders
    BORDER_ERROR = QColor(255, 100, 100)         # Error borders
    
    # ==================== Interactive Elements ====================
    # Buttons
    BUTTON_PRIMARY_BG = QColor(0, 120, 215)
    BUTTON_PRIMARY_HOVER = QColor(0, 140, 245)
    BUTTON_PRIMARY_PRESSED = QColor(0, 100, 185)
    
    BUTTON_SECONDARY_BG = QColor(60, 60, 60)
    BUTTON_SECONDARY_HOVER = QColor(70, 70, 70)
    BUTTON_SECONDARY_PRESSED = QColor(50, 50, 50)
    
    BUTTON_DANGER_BG = QColor(200, 50, 50)
    BUTTON_DANGER_HOVER = QColor(220, 60, 60)
    
    # Inputs
    INPUT_BG = QColor(50, 50, 50)
    INPUT_BORDER = QColor(60, 60, 60)
    INPUT_BORDER_FOCUS = QColor(0, 150, 255)
    INPUT_BORDER_ERROR = QColor(255, 100, 100)
    
    # ==================== Status/Feedback ====================
    ERROR = QColor(255, 100, 100)                # Error states
    ERROR_BG = QColor(60, 30, 30)               # Error backgrounds
    
    WARNING = QColor(255, 200, 100)             # Warning states
    WARNING_BG = QColor(50, 45, 30)             # Warning backgrounds
    
    SUCCESS = QColor(100, 255, 150)             # Success states
    SUCCESS_BG = QColor(30, 50, 35)             # Success backgrounds
    
    INFO = QColor(100, 200, 255)                # Info states
    INFO_BG = QColor(30, 40, 50)                # Info backgrounds
    
    # ==================== Gizmos ====================
    GIZMO_MOVE_X = QColor(255, 89, 89)         # Move X axis
    GIZMO_MOVE_Y = QColor(145, 255, 117)        # Move Y axis
    GIZMO_MOVE_Z = QColor(117, 145, 255)        # Move Z axis
    GIZMO_ROTATE = QColor(255, 200, 100)         # Rotate gizmo
    GIZMO_SCALE = QColor(200, 100, 255)          # Scale gizmo
    
    @classmethod
    def to_stylesheet(cls, color: QColor) -> str:
        """Convert QColor to stylesheet color string."""
        return f"rgb({color.red()}, {color.green()}, {color.blue()})"
    
    @classmethod
    def to_stylesheet_rgba(cls, color: QColor) -> str:
        """Convert QColor to stylesheet rgba string with alpha."""
        return f"rgba({color.red()}, {color.green()}, {color.blue()}, {color.alpha()})"
    
    @classmethod
    def get_node_color(cls, node_type: str) -> QColor:
        """Get color for specific node type."""
        type_colors = {
            "Sprite": cls.NODE_SPRITE,
            "AnimatedSprite": cls.NODE_ANIMATION,
            "RigidBody": cls.NODE_PHYSICS,
            "StaticBody": cls.NODE_PHYSICS,
            "CharacterBody": cls.NODE_PHYSICS,
            "CollisionShape": cls.NODE_COLLISION,
            "Control": cls.NODE_UI,
            "Button": cls.NODE_UI,
            "Label": cls.NODE_UI,
            "Audio": cls.NODE_AUDIO,
            "Camera": cls.NODE_CAMERA,
            "Light": cls.NODE_LIGHT,
            "Particles": cls.NODE_PARTICLES,
            "Path": cls.NODE_PATH,
            "Navigation": cls.NODE_NAVIGATION,
        }
        return type_colors.get(node_type, cls.NODE_GENERIC)
