# /**************************************************************************/
# /*  inspector_dock.py                                                      */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Inspector dock widget - Modern redesign with design system.

Features:
- Grouped properties with collapsible sections
- Color-coded property types
- Real-time value updates
- Modern input controls
"""

from typing import Optional, Dict, Any, List, Callable
import inspect

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QScrollArea, QFormLayout,
    QLabel, QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox,
    QPushButton, QFrame, QGroupBox, QTextEdit, QHBoxLayout,
    QSizePolicy
)

from engine.core.node_base import Node
from ..theme import EditorColors, EditorFonts, EditorSpacing
from ..components import EditorInput, EditorComboBox, EditorGroupBox


class PropertyEditor:
    """Base class for property editors with design system styling."""

    value_changed = Signal(str, object)  # property_name, new_value

    def __init__(self, property_name: str, property_value: Any):
        self.property_name = property_name
        self.property_value = property_value
        self.widget = None
        self._on_change: Optional[Callable] = None

    def create_widget(self) -> QWidget:
        """Create the editor widget."""
        return QLabel("Property Editor")

    def get_value(self) -> Any:
        """Get current value from widget."""
        return self.property_value

    def set_on_change(self, callback: Callable) -> None:
        """Set callback for value changes."""
        self._on_change = callback

    def _emit_change(self, value: Any) -> None:
        """Emit value change."""
        self.value_changed.emit(self.property_name, value)
        if self._on_change:
            self._on_change(self.property_name, value)


class StringPropertyEditor(PropertyEditor):
    """Editor for string properties."""

    def create_widget(self) -> QWidget:
        self.widget = EditorInput()
        self.widget.setText(str(self.property_value))
        self.widget.textChanged.connect(self._on_text_changed)
        return self.widget

    def _on_text_changed(self, text: str) -> None:
        self._emit_change(text)

    def get_value(self) -> str:
        return self.widget.text()


class FloatPropertyEditor(PropertyEditor):
    """Editor for float properties."""

    def create_widget(self) -> QWidget:
        self.widget = QDoubleSpinBox()
        self._style_spinbox(self.widget)
        self.widget.setRange(-999999, 999999)
        self.widget.setDecimals(3)
        self.widget.setValue(float(self.property_value))
        self.widget.valueChanged.connect(self._on_value_changed)
        return self.widget

    def _style_spinbox(self, spinbox: QDoubleSpinBox) -> None:
        """Apply design system styling."""
        spinbox.setStyleSheet(f"""
            QDoubleSpinBox {{
                background-color: {EditorColors.to_stylesheet(EditorColors.INPUT_BG)};
                border: 1px solid {EditorColors.to_stylesheet(EditorColors.INPUT_BORDER)};
                color: {EditorColors.to_stylesheet(EditorColors.TEXT_PRIMARY)};
                padding: 4px 8px;
                border-radius: {EditorSpacing.RADIUS_SM}px;
                min-width: 60px;
            }}
            QDoubleSpinBox:focus {{
                border: 1px solid {EditorColors.to_stylesheet(EditorColors.INPUT_BORDER_FOCUS)};
            }}
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
                width: 16px;
                background: {EditorColors.to_stylesheet(EditorColors.BG_TERTIARY)};
                border: none;
            }}
            QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {{
                background: {EditorColors.to_stylesheet(EditorColors.BG_HOVER)};
            }}
        """)

    def _on_value_changed(self, value: float) -> None:
        self._emit_change(value)

    def get_value(self) -> float:
        return self.widget.value()


class IntPropertyEditor(PropertyEditor):
    """Editor for integer properties."""

    def create_widget(self) -> QWidget:
        self.widget = QSpinBox()
        self._style_spinbox(self.widget)
        self.widget.setRange(-999999, 999999)
        self.widget.setValue(int(self.property_value))
        self.widget.valueChanged.connect(self._on_value_changed)
        return self.widget

    def _style_spinbox(self, spinbox: QSpinBox) -> None:
        """Apply design system styling."""
        spinbox.setStyleSheet(f"""
            QSpinBox {{
                background-color: {EditorColors.to_stylesheet(EditorColors.INPUT_BG)};
                border: 1px solid {EditorColors.to_stylesheet(EditorColors.INPUT_BORDER)};
                color: {EditorColors.to_stylesheet(EditorColors.TEXT_PRIMARY)};
                padding: 4px 8px;
                border-radius: {EditorSpacing.RADIUS_SM}px;
                min-width: 60px;
            }}
            QSpinBox:focus {{
                border: 1px solid {EditorColors.to_stylesheet(EditorColors.INPUT_BORDER_FOCUS)};
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                width: 16px;
                background: {EditorColors.to_stylesheet(EditorColors.BG_TERTIARY)};
                border: none;
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background: {EditorColors.to_stylesheet(EditorColors.BG_HOVER)};
            }}
        """)

    def _on_value_changed(self, value: int) -> None:
        self._emit_change(value)

    def get_value(self) -> int:
        return self.widget.value()


class BoolPropertyEditor(PropertyEditor):
    """Editor for boolean properties."""

    def create_widget(self) -> QWidget:
        self.widget = QCheckBox()
        self._style_checkbox(self.widget)
        self.widget.setChecked(bool(self.property_value))
        self.widget.stateChanged.connect(self._on_state_changed)
        return self.widget

    def _style_checkbox(self, checkbox: QCheckBox) -> None:
        """Apply design system styling."""
        checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {EditorColors.to_stylesheet(EditorColors.TEXT_PRIMARY)};
                spacing: 6px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {EditorColors.to_stylesheet(EditorColors.BORDER_DEFAULT)};
                border-radius: 3px;
                background: {EditorColors.to_stylesheet(EditorColors.INPUT_BG)};
            }}
            QCheckBox::indicator:checked {{
                background: {EditorColors.to_stylesheet(EditorColors.BUTTON_PRIMARY_BG)};
                border-color: {EditorColors.to_stylesheet(EditorColors.BUTTON_PRIMARY_BG)};
            }}
            QCheckBox::indicator:checked::after {{
                content: "✓";
                color: white;
                font-size: 12px;
            }}
        """)

    def _on_state_changed(self, state: int) -> None:
        self._emit_change(bool(state))

    def get_value(self) -> bool:
        return self.widget.isChecked()


class Vector2PropertyEditor(PropertyEditor):
    """Editor for Vector2 properties with color-coded axes."""

    def create_widget(self) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(EditorSpacing.SM)

        # X component (Red)
        x_label = QLabel("X")
        x_label.setStyleSheet(f"color: {EditorColors.to_stylesheet(EditorColors.GRID_AXIS_X)}; font-weight: bold;")
        self.x_widget = QDoubleSpinBox()
        self._style_spinbox(self.x_widget, EditorColors.GRID_AXIS_X)
        self.x_widget.setRange(-999999, 999999)
        self.x_widget.setDecimals(3)

        # Y component (Green)
        y_label = QLabel("Y")
        y_label.setStyleSheet(f"color: {EditorColors.to_stylesheet(EditorColors.GRID_AXIS_Y)}; font-weight: bold;")
        self.y_widget = QDoubleSpinBox()
        self._style_spinbox(self.y_widget, EditorColors.GRID_AXIS_Y)
        self.y_widget.setRange(-999999, 999999)
        self.y_widget.setDecimals(3)

        # Set initial values
        if hasattr(self.property_value, 'x'):
            self.x_widget.setValue(float(self.property_value.x))
            self.y_widget.setValue(float(self.property_value.y))

        # Connect signals
        self.x_widget.valueChanged.connect(self._on_value_changed)
        self.y_widget.valueChanged.connect(self._on_value_changed)

        layout.addWidget(x_label)
        layout.addWidget(self.x_widget)
        layout.addWidget(y_label)
        layout.addWidget(self.y_widget)
        layout.addStretch()

        self.widget = widget
        return widget

    def _style_spinbox(self, spinbox: QDoubleSpinBox, accent_color: QColor) -> None:
        """Apply design system styling with accent color."""
        spinbox.setStyleSheet(f"""
            QDoubleSpinBox {{
                background-color: {EditorColors.to_stylesheet(EditorColors.INPUT_BG)};
                border: 1px solid {EditorColors.to_stylesheet(EditorColors.INPUT_BORDER)};
                color: {EditorColors.to_stylesheet(EditorColors.TEXT_PRIMARY)};
                padding: 4px 8px;
                border-radius: {EditorSpacing.RADIUS_SM}px;
                min-width: 50px;
            }}
            QDoubleSpinBox:focus {{
                border: 1px solid {EditorColors.to_stylesheet(accent_color)};
            }}
        """)

    def _on_value_changed(self) -> None:
        value = (self.x_widget.value(), self.y_widget.value())
        self._emit_change(value)

    def get_value(self) -> Any:
        return (self.x_widget.value(), self.y_widget.value())


class ColorPropertyEditor(PropertyEditor):
    """Editor for Color properties with preview."""

    def create_widget(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(EditorSpacing.XS)

        # Color preview bar
        self.preview_frame = QFrame()
        self.preview_frame.setFixedHeight(24)
        self.preview_frame.setFrameShape(QFrame.Shape.StyledPanel)
        layout.addWidget(self.preview_frame)

        # RGBA controls
        rgba_layout = QHBoxLayout()
        rgba_layout.setSpacing(EditorSpacing.SM)

        # R component
        self.r_widget = self._create_color_spinbox("R", EditorColors.GRID_AXIS_X)
        rgba_layout.addWidget(self.r_widget)

        # G component
        self.g_widget = self._create_color_spinbox("G", EditorColors.GRID_AXIS_Y)
        rgba_layout.addWidget(self.g_widget)

        # B component
        self.b_widget = self._create_color_spinbox("B", EditorColors.GRID_AXIS_Z)
        rgba_layout.addWidget(self.b_widget)

        # A component
        self.a_widget = self._create_color_spinbox("A", EditorColors.NODE_GENERIC)
        rgba_layout.addWidget(self.a_widget)

        layout.addLayout(rgba_layout)

        # Set initial values
        if hasattr(self.property_value, 'r'):
            self.r_widget.setValue(float(self.property_value.r))
            self.g_widget.setValue(float(self.property_value.g))
            self.b_widget.setValue(float(self.property_value.b))
            self.a_widget.setValue(float(self.property_value.a))

        self._update_preview()

        # Connect signals
        self.r_widget.valueChanged.connect(self._on_value_changed)
        self.g_widget.valueChanged.connect(self._on_value_changed)
        self.b_widget.valueChanged.connect(self._on_value_changed)
        self.a_widget.valueChanged.connect(self._on_value_changed)

        self.widget = widget
        return widget

    def _create_color_spinbox(self, label: str, accent_color: QColor) -> QDoubleSpinBox:
        """Create a color channel spinbox."""
        spinbox = QDoubleSpinBox()
        spinbox.setRange(0, 1)
        spinbox.setDecimals(3)
        spinbox.setSingleStep(0.1)
        spinbox.setPrefix(f"{label}: ")
        spinbox.setStyleSheet(f"""
            QDoubleSpinBox {{
                background-color: {EditorColors.to_stylesheet(EditorColors.INPUT_BG)};
                border: 1px solid {EditorColors.to_stylesheet(EditorColors.INPUT_BORDER)};
                color: {EditorColors.to_stylesheet(EditorColors.TEXT_PRIMARY)};
                padding: 4px 4px;
                border-radius: {EditorSpacing.RADIUS_SM}px;
                min-width: 55px;
                font-size: {EditorFonts.SIZE_SM}pt;
            }}
            QDoubleSpinBox:focus {{
                border: 1px solid {EditorColors.to_stylesheet(accent_color)};
            }}
        """)
        return spinbox

    def _on_value_changed(self) -> None:
        self._update_preview()
        value = (self.r_widget.value(), self.g_widget.value(),
                self.b_widget.value(), self.a_widget.value())
        self._emit_change(value)

    def _update_preview(self) -> None:
        """Update color preview."""
        r = int(self.r_widget.value() * 255)
        g = int(self.g_widget.value() * 255)
        b = int(self.b_widget.value() * 255)
        self.preview_frame.setStyleSheet(f"""
            background-color: rgb({r}, {g}, {b});
            border: 1px solid {EditorColors.to_stylesheet(EditorColors.BORDER_DEFAULT)};
            border-radius: {EditorSpacing.RADIUS_SM}px;
        """)

    def get_value(self) -> Any:
        return (self.r_widget.value(), self.g_widget.value(),
                self.b_widget.value(), self.a_widget.value())


class InspectorWidget(QWidget):
    """Modern inspector widget with grouped properties."""

    property_changed = Signal(str, object)  # property_name, new_value
    node_name_changed = Signal(str)  # new_name

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_node: Optional[Node] = None
        self.property_editors: Dict[str, PropertyEditor] = {}

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup modern inspector UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(EditorSpacing.SM, EditorSpacing.SM, EditorSpacing.SM, EditorSpacing.SM)
        layout.setSpacing(EditorSpacing.MD)

        # Scroll area for properties
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        # Style scroll area
        self.scroll_area.setStyleSheet(f"""
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
        """)

        self.properties_widget = QWidget()
        self.properties_layout = QVBoxLayout(self.properties_widget)
        self.properties_layout.setContentsMargins(0, 0, 0, 0)
        self.properties_layout.setSpacing(EditorSpacing.MD)

        self.scroll_area.setWidget(self.properties_widget)
        layout.addWidget(self.scroll_area)
    
    def set_node(self, node: Optional[Node]) -> None:
        """Set the node to inspect."""
        self.current_node = node
        self._refresh_properties()
    
    def _refresh_properties(self) -> None:
        """Refresh property editors for current node."""
        # Clear existing editors
        for i in reversed(range(self.properties_layout.count())):
            child = self.properties_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
                child.deleteLater()

        self.property_editors.clear()

        if not self.current_node:
            # Empty state
            empty_label = QLabel("Select a node to edit properties")
            empty_label.setFont(EditorFonts.label_small())
            empty_label.setStyleSheet(f"color: {EditorColors.to_stylesheet(EditorColors.TEXT_SECONDARY)};")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.properties_layout.addWidget(empty_label)
            return

        # Node info header
        self._add_node_header()

        # Add properties based on node type
        self._add_node_properties()

        # Add stretch at bottom
        self.properties_layout.addStretch()

    def _add_node_header(self) -> None:
        """Add node header with icon and type."""
        header_frame = QFrame()
        header_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {EditorColors.to_stylesheet(EditorColors.BG_TERTIARY)};
                border-radius: {EditorSpacing.RADIUS_MD}px;
                padding: {EditorSpacing.SM}px;
            }}
        """)

        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(EditorSpacing.MD, EditorSpacing.MD, EditorSpacing.MD, EditorSpacing.MD)
        header_layout.setSpacing(EditorSpacing.XS)

        # Node type and icon
        node_type_name = self.current_node.__class__.__name__
        from ..docks.scene_tree_dock import NODE_ICONS
        icon = NODE_ICONS.get(node_type_name, "🔵")

        type_label = QLabel(f"{icon} {node_type_name}")
        type_label.setFont(EditorFonts.get_ui_font(EditorFonts.SIZE_SM, EditorFonts.WEIGHT_MEDIUM))
        type_label.setStyleSheet(f"color: {EditorColors.to_stylesheet(EditorColors.TEXT_SECONDARY)};")
        header_layout.addWidget(type_label)

        # Name editor
        name_label = QLabel("Name")
        name_label.setFont(EditorFonts.label_small())
        header_layout.addWidget(name_label)

        self.name_editor = EditorInput()
        self.name_editor.setText(self.current_node.name)
        self.name_editor.textChanged.connect(self._on_node_name_changed)
        header_layout.addWidget(self.name_editor)

        self.properties_layout.addWidget(header_frame)
    
    def _add_node_properties(self) -> None:
        """Add property editors grouped by category."""
        if not self.current_node:
            return

        # Group properties by category
        property_groups = {
            'Transform': {},
            'Appearance': {},
            'Physics': {},
            'Other': {}
        }

        # Transform properties
        if hasattr(self.current_node, 'position'):
            property_groups['Transform']['position'] = (object, self.current_node.position)
        if hasattr(self.current_node, 'rotation'):
            property_groups['Transform']['rotation'] = (float, self.current_node.rotation)
        if hasattr(self.current_node, 'scale'):
            property_groups['Transform']['scale'] = (object, self.current_node.scale)

        # Appearance properties
        if hasattr(self.current_node, 'visible'):
            property_groups['Appearance']['visible'] = (bool, self.current_node.visible)
        if hasattr(self.current_node, 'modulate'):
            property_groups['Appearance']['modulate'] = (object, self.current_node.modulate)
        if hasattr(self.current_node, 'z_index'):
            property_groups['Appearance']['z_index'] = (int, self.current_node.z_index)

        # Sprite2D specific
        if self.current_node.__class__.__name__ == 'Sprite2D':
            if hasattr(self.current_node, 'flip_h'):
                property_groups['Appearance']['flip_h'] = (bool, self.current_node.flip_h)
            if hasattr(self.current_node, 'flip_v'):
                property_groups['Appearance']['flip_v'] = (bool, self.current_node.flip_v)

        # Camera2D specific
        if self.current_node.__class__.__name__ == 'Camera2D':
            if hasattr(self.current_node, 'zoom'):
                property_groups['Transform']['zoom'] = (object, self.current_node.zoom)
            if hasattr(self.current_node, 'offset'):
                property_groups['Transform']['offset'] = (object, self.current_node.offset)

        # Physics properties
        physics_classes = ['RigidBody2D', 'StaticBody2D', 'CharacterBody2D', 'CollisionShape2D']
        if self.current_node.__class__.__name__ in physics_classes:
            if hasattr(self.current_node, 'collision_layer'):
                property_groups['Physics']['collision_layer'] = (int, self.current_node.collision_layer)
            if hasattr(self.current_node, 'collision_mask'):
                property_groups['Physics']['collision_mask'] = (int, self.current_node.collision_mask)

        # Create property groups
        for group_name, props in property_groups.items():
            if not props:
                continue

            group = self._create_property_group(group_name, props)
            if group:
                self.properties_layout.addWidget(group)

    def _create_property_group(self, group_name: str, props: Dict[str, tuple]) -> Optional[QWidget]:
        """Create a collapsible property group."""
        if not props:
            return None

        # Use EditorGroupBox for consistent styling
        group = EditorGroupBox(group_name)
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(EditorSpacing.SM)

        for prop_name, (prop_type, prop_value) in props.items():
            if prop_value is None:
                continue

            editor = self._create_property_editor(prop_name, prop_type, prop_value)
            if editor:
                self.property_editors[prop_name] = editor
                editor.set_on_change(self._on_property_changed)

                # Create property row
                prop_widget = self._create_property_row(prop_name, editor)
                group_layout.addWidget(prop_widget)

        return group

    def _create_property_row(self, prop_name: str, editor: PropertyEditor) -> QWidget:
        """Create a property row with label and editor."""
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(EditorSpacing.SM)

        # Property name label
        name_label = QLabel(prop_name.replace('_', ' ').title())
        name_label.setFont(EditorFonts.property_name())
        name_label.setStyleSheet(f"color: {EditorColors.to_stylesheet(EditorColors.TEXT_SECONDARY)};")
        name_label.setFixedWidth(80)
        row_layout.addWidget(name_label)

        # Editor widget
        editor_widget = editor.create_widget()
        editor_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        row_layout.addWidget(editor_widget)

        return row

    def _on_property_changed(self, prop_name: str, value: Any) -> None:
        """Handle property value change."""
        if self.current_node and hasattr(self.current_node, prop_name):
            setattr(self.current_node, prop_name, value)
            self.property_changed.emit(prop_name, value)
    
    def _create_property_editor(self, prop_name: str, prop_type: type, prop_value: Any) -> Optional[PropertyEditor]:
        """Create appropriate property editor."""
        if prop_type == str:
            return StringPropertyEditor(prop_name, prop_value)
        elif prop_type == float:
            return FloatPropertyEditor(prop_name, prop_value)
        elif prop_type == int:
            return IntPropertyEditor(prop_name, prop_value)
        elif prop_type == bool:
            return BoolPropertyEditor(prop_name, prop_value)
        elif prop_type == object:
            # Try to infer type from value
            if hasattr(prop_value, 'x') and hasattr(prop_value, 'y'):
                return Vector2PropertyEditor(prop_name, prop_value)
            elif hasattr(prop_value, 'r') and hasattr(prop_value, 'g'):
                return ColorPropertyEditor(prop_name, prop_value)
        
        return None
    
    def _on_node_name_changed(self, name: str) -> None:
        """Handle node name change."""
        if self.current_node:
            self.current_node.name = name
            self.node_name_changed.emit(name)

    def apply_changes(self) -> None:
        """Apply all property changes to the current node."""
        if not self.current_node:
            return

        for prop_name, editor in self.property_editors.items():
            new_value = editor.get_value()
            if hasattr(self.current_node, prop_name):
                setattr(self.current_node, prop_name, new_value)
                self.property_changed.emit(prop_name, new_value)


class InspectorDock(QDockWidget):
    """Modern inspector dock widget."""

    property_changed = Signal(str, object)  # property_name, new_value
    node_name_changed = Signal(str)  # new_name

    def __init__(self, parent=None):
        super().__init__("Inspector", parent)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        # Create widget
        self.inspector = InspectorWidget()
        self.setWidget(self.inspector)

        # Connect signals
        self.inspector.property_changed.connect(self._on_property_changed)
        self.inspector.node_name_changed.connect(self._on_node_name_changed)

    def set_node(self, node: Optional[Node]) -> None:
        """Set the node to inspect."""
        self.inspector.set_node(node)

    def _on_property_changed(self, property_name: str, new_value: Any) -> None:
        """Handle property change."""
        self.property_changed.emit(property_name, new_value)

    def _on_node_name_changed(self, new_name: str) -> None:
        """Handle node name change."""
        self.node_name_changed.emit(new_name)

    def refresh(self) -> None:
        """Refresh the inspector."""
        self.inspector._refresh_properties()
