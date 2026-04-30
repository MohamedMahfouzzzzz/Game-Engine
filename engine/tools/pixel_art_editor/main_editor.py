# /**************************************************************************/
# /*  main_editor.py                                                        */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Main pixel art editor widget."""

import logging
from typing import Optional, List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QToolBar,
    QSplitter, QFileDialog, QMessageBox, QInputDialog
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction

from engine.tools.pixel_art_editor.canvas import Canvas, Layer
from engine.tools.pixel_art_editor.ui.toolbox import Toolbox
from engine.tools.pixel_art_editor.ui.layer_panel import LayerPanel
from engine.tools.pixel_art_editor.ui.color_palette import ColorPalette
from engine.tools.pixel_art_editor.ui.status_bar import StatusBar
from engine.tools.pixel_art_editor.animation.timeline import Timeline
from engine.tools.pixel_art_editor.tools.tool_base import ToolBase
from engine.tools.pixel_art_editor.scripting import AsepriteAPI

logger = logging.getLogger(__name__)


class PixelArtEditor(QWidget):
    """Main pixel art editor with full toolset."""

    image_saved = Signal(str)

    def __init__(self, parent=None, width: int = 64, height: int = 64):
        super().__init__(parent)
        logger.info("Initializing PixelArtEditor with canvas %dx%d", width, height)
        self._canvas = Canvas(width, height)
        self._current_tool: Optional[ToolBase] = None
        self._zoom: float = 8.0
        self._script_api = AsepriteAPI()
        self._last_script_path = ""

        self._build_ui()
        self._setup_tools()
        self._setup_shortcuts()

    def _build_ui(self) -> None:
        """Build the editor UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Toolbar
        self._toolbar = QToolBar("Tools")
        self._build_toolbar()
        layout.addWidget(self._toolbar)

        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: Toolbox and color palette
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        self._toolbox = Toolbox()
        self._toolbox.tool_selected.connect(self._on_tool_selected)
        left_layout.addWidget(self._toolbox)

        self._color_palette = ColorPalette()
        self._color_palette.color_selected.connect(self._on_color_changed)
        left_layout.addWidget(self._color_palette)

        left_layout.addStretch()
        splitter.addWidget(left_panel)

        # Center: Canvas view
        from engine.tools.pixel_art_editor.ui.canvas_view import CanvasView
        self._canvas_view = CanvasView(self._canvas)
        self._canvas_view.set_zoom(self._zoom)
        splitter.addWidget(self._canvas_view)

        # Right: Layer panel
        self._layer_panel = LayerPanel(self._canvas)
        splitter.addWidget(self._layer_panel)

        splitter.setSizes([150, 600, 200])
        layout.addWidget(splitter, 1)

        # Bottom: Timeline for animation
        self._timeline = Timeline()
        layout.addWidget(self._timeline)

        # Status bar
        self._status_bar = StatusBar()
        layout.addWidget(self._status_bar)

    def _build_toolbar(self) -> None:
        """Build main toolbar actions."""
        actions = [
            ("New", self._new_image, "Ctrl+N"),
            ("Open", self._open_image, "Ctrl+O"),
            ("Save", self._save_image, "Ctrl+S"),
            ("Export", self._export_image, "Ctrl+E"),
            None,  # Separator
            ("Undo", self._undo, "Ctrl+Z"),
            ("Redo", self._redo, "Ctrl+Y"),
            None,
            ("Zoom In", self._zoom_in, "Ctrl++"),
            ("Zoom Out", self._zoom_out, "Ctrl+-"),
            None,
            ("Grid", self._toggle_grid, ""),
            ("Preview", self._toggle_preview, ""),
            None,
            ("Run Script", self._run_lua_script, ""),
        ]

        for item in actions:
            if item is None:
                self._toolbar.addSeparator()
            else:
                name, callback, shortcut = item
                action = QAction(name, self)
                action.triggered.connect(callback)
                if shortcut:
                    action.setShortcut(shortcut)
                self._toolbar.addAction(action)

    def _setup_tools(self) -> None:
        """Initialize drawing tools."""
        from engine.tools.pixel_art_editor.tools import (
            PencilTool, EraserTool, LineTool, RectangleTool,
            CircleTool, FillTool, PickTool, SelectionTool,
            MoveTool, ShapeTool, TextTool, GradientTool,
            BlurTool, SmudgeTool, DodgeTool, BurnTool
        )

        tools = [
            PencilTool(),
            EraserTool(),
            LineTool(),
            RectangleTool(),
            CircleTool(),
            FillTool(),
            PickTool(),
            SelectionTool(),
            MoveTool(),
            ShapeTool(),
            TextTool(),
            GradientTool(),
            BlurTool(),
            SmudgeTool(),
            DodgeTool(),
            BurnTool(),
        ]

        for tool in tools:
            self._toolbox.add_tool(tool)

        # Select pencil by default
        self._toolbox.select_tool(0)

    def _setup_shortcuts(self) -> None:
        """Setup keyboard shortcuts."""
        from PySide6.QtGui import QKeySequence, QShortcut

        # Tool shortcuts
        shortcuts = [
            ("B", 0),   # Brush/Pencil
            ("E", 1),   # Eraser
            ("L", 2),   # Line
            ("R", 3),   # Rectangle
            ("C", 4),   # Circle
            ("F", 5),   # Fill
            ("I", 6),   # Eyedropper
            ("M", 7),   # Marquee/Selection
            ("V", 8),   # Move
            ("T", 10),  # Text
        ]

        for key, tool_idx in shortcuts:
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.activated.connect(lambda idx=tool_idx: self._toolbox.select_tool(idx))

    def _on_tool_selected(self, tool: ToolBase) -> None:
        """Handle tool selection."""
        self._current_tool = tool
        self._canvas_view.set_tool(tool)
        # Set current color to the new tool
        current_color = self._color_palette.get_primary_color()
        tool.set_color(current_color)
        self._status_bar.set_message(f"Tool: {tool.name}")

    def _on_color_changed(self, color: tuple) -> None:
        """Handle color change from palette."""
        self._canvas_view.set_current_color(color)
        if self._current_tool:
            self._current_tool.set_color(color)
        self._status_bar.set_message(f"Color: {color}")

    def _new_image(self) -> None:
        """Create new image."""
        size, ok = QInputDialog.getText(self, "New Image", "Size (WxH):", text="64x64")
        if ok and "x" in size:
            try:
                w, h = map(int, size.lower().split("x"))
                self._canvas = Canvas(w, h)
                self._canvas_view.set_canvas(self._canvas)
                self._layer_panel.set_canvas(self._canvas)
            except ValueError:
                QMessageBox.warning(self, "Error", "Invalid size format")

    def _open_image(self) -> None:
        """Open existing image."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "",
            "Aseprite Files (*.ase *.aseprite);;Images (*.png *.jpg *.bmp *.gif);;All Files (*)"
        )
        if path:
            if self._canvas.load_file(path):
                self._canvas_view.update()

    def _save_image(self) -> None:
        """Save image."""
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Image", "",
            "Aseprite (*.ase *.aseprite);;Game Engine Pixel (*.pixel);;Sprite (*.sprite);;PNG (*.png);;JPEG (*.jpg);;GIF (*.gif);;All Files (*)"
        )
        if path:
            self._save_with_format(path)
            self.image_saved.emit(path)

    def _save_with_format(self, path: str) -> None:
        """Save with custom format support."""
        import json
        from pathlib import Path

        ext = Path(path).suffix.lower()

        if ext in (".ase", ".aseprite"):
            # Aseprite format with layers
            self._canvas.save_aseprite(path)

        elif ext == ".pixel":
            # Custom pixel format with metadata
            image = self._canvas.get_merged_image()
            data = {
                "version": 1,
                "width": self._canvas.width,
                "height": self._canvas.height,
                "layers": [],
                "palette": []
            }

            # Save layer data
            for i, layer in enumerate(self._canvas.layers):
                layer_data = {
                    "name": layer.name,
                    "visible": layer.visible,
                    "opacity": layer.opacity,
                    "locked": layer.locked,
                    "pixels": []
                }

                # Save pixel data
                for y in range(layer.height):
                    for x in range(layer.width):
                        color = layer.get_pixel(x, y)
                        if color[3] > 0:  # Only save non-transparent pixels
                            layer_data["pixels"].append({"x": x, "y": y, "color": color})

                data["layers"].append(layer_data)

            # Save as JSON
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

        elif ext == ".sprite":
            # Sprite format with animation data
            image = self._canvas.get_merged_image()
            data = {
                "version": 1,
                "width": self._canvas.width,
                "height": self._canvas.height,
                "frames": 1,
                "fps": 12,
                "image_data": image.tobytes("raw", "RGBA").hex()
            }

            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

        else:
            # Standard image formats
            self._canvas.save_image(path)

    def _export_image(self) -> None:
        """Export with options."""
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Image", "",
            "Aseprite (*.ase *.aseprite);;PNG (*.png);;Sprite Sheet (*.png)"
        )
        if path:
            self._canvas.export(path)

    def _undo(self) -> None:
        """Undo last action."""
        self._canvas.undo()
        self._canvas_view.update()

    def _redo(self) -> None:
        """Redo last undone action."""
        self._canvas.redo()
        self._canvas_view.update()

    def _zoom_in(self) -> None:
        """Zoom in."""
        self._zoom = min(32.0, self._zoom * 1.5)
        self._canvas_view.set_zoom(self._zoom)

    def _zoom_out(self) -> None:
        """Zoom out."""
        self._zoom = max(1.0, self._zoom / 1.5)
        self._canvas_view.set_zoom(self._zoom)

    def _toggle_grid(self) -> None:
        """Toggle grid visibility."""
        self._canvas_view.toggle_grid()

    def _toggle_preview(self) -> None:
        """Toggle preview mode."""
        self._canvas_view.toggle_preview()

    def _run_lua_script(self) -> None:
        """Run a Lua script file."""
        from pathlib import Path as PathLib
        path, _ = QFileDialog.getOpenFileName(
            self, "Run Lua Script", self._last_script_path,
            "Lua Scripts (*.lua);;All Files (*)"
        )
        if path:
            self._last_script_path = str(PathLib(path).parent)
            self._execute_lua_script(path)

    def _execute_lua_script(self, path: str) -> None:
        """Execute a Lua script file and show results."""
        from pathlib import Path as PathLib
        script_path = PathLib(path)
        
        if not script_path.exists():
            QMessageBox.critical(self, "Error", f"Script not found: {path}")
            return
        
        # Run the script
        result = self._script_api.run_script_file(script_path)
        
        # Show results
        if result["success"]:
            output = result.get("output", "")
            if output:
                QMessageBox.information(self, "Script Output", f"Script ran successfully!\n\nOutput:\n{output}")
            else:
                QMessageBox.information(self, "Script Output", "Script ran successfully!")
        else:
            error = result.get("error", "Unknown error")
            QMessageBox.critical(self, "Script Error", f"Script failed:\n{error}")
        
        # Update canvas if sprite was modified
        if result["success"]:
            self._canvas_view.update()

    @property
    def canvas(self) -> Canvas:
        return self._canvas
