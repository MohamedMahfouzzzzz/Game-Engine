# /**************************************************************************/
# /*  canvas.py                                                             */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Canvas with layer support for pixel art."""

from dataclasses import dataclass
from typing import List, Optional, Tuple
from PIL import Image
from PySide6.QtGui import QColor, QImage

from engine.core.undo_manager import UndoManager, Command


@dataclass(slots=True)
class PixelDelta:
    x: int
    y: int
    before: Tuple[int, int, int, int]
    after: Tuple[int, int, int, int]


def merge_rect(a: Optional[Tuple[int, int, int, int]], b: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
    if a is None:
        return b
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    x1 = min(ax, bx)
    y1 = min(ay, by)
    x2 = max(ax + aw, bx + bw)
    y2 = max(ay + ah, by + bh)
    return (x1, y1, x2 - x1, y2 - y1)

class Layer:
    """A single layer in the canvas."""

    def __init__(self, name: str, width: int, height: int, visible: bool = True):
        self.name = name
        self.width = width
        self.height = height
        self.visible = visible
        self.opacity: float = 1.0
        self.locked: bool = False

        self._image: Optional[Image.Image] = None
        self.dirty_rect: Optional[Tuple[int, int, int, int]] = None

    def _ensure_image(self) -> Image.Image:
        if self._image is None:
            self._image = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        return self._image

    def get_pixel(self, x: int, y: int) -> Tuple[int, int, int, int]:
        """Get pixel color at position."""
        if 0 <= x < self.width and 0 <= y < self.height:
            if self._image is None:
                return (0, 0, 0, 0)
            return self._image.getpixel((x, y))
        return (0, 0, 0, 0)

    def set_pixel(self, x: int, y: int, color: Tuple[int, int, int, int]) -> Optional[PixelDelta]:
        """Set pixel color at position."""
        if self.locked or not (0 <= x < self.width and 0 <= y < self.height):
            return None
        image = self._ensure_image()
        before = image.getpixel((x, y))
        after = tuple(color[:4])
        if before == after:
            return None
        image.putpixel((x, y), after)
        self.dirty_rect = merge_rect(self.dirty_rect, (x, y, 1, 1))
        return PixelDelta(x, y, before, after)

    def clear(self) -> None:
        """Clear layer to transparent."""
        self._image = None
        self.dirty_rect = (0, 0, self.width, self.height)

    def resize(self, new_width: int, new_height: int) -> None:
        """Resize layer."""
        if self._image is not None:
            new_image = Image.new("RGBA", (new_width, new_height), (0, 0, 0, 0))
            new_image.paste(self._image, (0, 0))
            self._image = new_image
        self.width = new_width
        self.height = new_height
        self.dirty_rect = (0, 0, new_width, new_height)

    def merge_with(self, other: "Layer") -> None:
        """Merge another layer onto this one."""
        if other._image is None:
            return
        # Composite other layer on top of this one
        base = self._ensure_image()
        top = other._ensure_image()
        self._image = Image.alpha_composite(base, top)
        self.dirty_rect = (0, 0, self.width, self.height)

    def duplicate(self) -> "Layer":
        """Create a copy of this layer."""
        new_layer = Layer(f"{self.name} copy", self.width, self.height, self.visible)
        new_layer._image = self._image.copy() if self._image is not None else None
        new_layer.opacity = self.opacity
        return new_layer

    def get_qimage(self) -> QImage:
        """Get QImage for Qt rendering."""
        data = self._ensure_image().tobytes("raw", "RGBA")
        return QImage(data, self.width, self.height, QImage.Format.Format_RGBA8888)

    def to_image(self) -> Image.Image:
        """Get PIL Image."""
        return self._ensure_image().copy()

    def from_image(self, image: Image.Image) -> None:
        """Set from PIL Image."""
        if image.size != (self.width, self.height):
            image = image.resize((self.width, self.height), Image.Resampling.LANCZOS)
        self._image = image.convert("RGBA")
        self.dirty_rect = (0, 0, self.width, self.height)

    def get_image(self) -> Image.Image:
        """Get PIL Image (for saving)."""
        return self._ensure_image().copy()

    def paste_image(self, image: Image.Image, x: int = 0, y: int = 0) -> None:
        """Paste image at position (supports transparency)."""
        # Handle alpha compositing
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Calculate bounds
        img_w, img_h = image.size
        
        # Only paste if within bounds
        if x >= self.width or y >= self.height or x + img_w <= 0 or y + img_h <= 0:
            return
        
        # Create a temp image of layer size and paste layer
        temp = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        temp.paste(self._ensure_image(), (0, 0))
        
        # Paste the new image with transparency
        temp.paste(image, (x, y), image)
        
        self._image = temp
        self.dirty_rect = merge_rect(self.dirty_rect, (x, y, img_w, img_h))


class CanvasCommand(Command):
    """Undoable canvas command."""

    def __init__(self, layer: Layer, changes: List[PixelDelta]):
        super().__init__("Canvas Edit")
        self.layer = layer
        self.changes = changes

    def execute(self) -> None:
        pass  # Changes already applied

    def undo(self) -> None:
        for change in self.changes:
            self.layer.set_pixel(change.x, change.y, change.before)

    def redo(self) -> None:
        for change in self.changes:
            self.layer.set_pixel(change.x, change.y, change.after)


class Canvas:
    """Multi-layer canvas for pixel art editing."""

    def __init__(self, width: int = 64, height: int = 64):
        self.width = width
        self.height = height
        self.layers: List[Layer] = []
        self._active_layer_index: int = 0
        self._undo_manager = UndoManager()
        self._pending_layer: Optional[Layer] = None
        self._pending_changes: List[PixelDelta] = []

        # Add default layer
        self.add_layer("Background")

        # Grid settings
        self.show_grid: bool = True
        self.grid_size: int = 1
        self.grid_color: Tuple[int, int, int, int] = (128, 128, 128, 64)

        # Selection
        self.selection: Optional[Tuple[int, int, int, int]] = None  # x, y, w, h
        self.dirty_rect: Optional[Tuple[int, int, int, int]] = None

    def add_layer(self, name: str) -> Layer:
        """Add a new layer."""
        layer = Layer(name, self.width, self.height)
        self.layers.append(layer)
        return layer

    def remove_layer(self, index: int) -> None:
        """Remove layer at index."""
        if 0 <= index < len(self.layers) and len(self.layers) > 1:
            del self.layers[index]
            if self._active_layer_index >= len(self.layers):
                self._active_layer_index = len(self.layers) - 1

    def move_layer(self, from_index: int, to_index: int) -> None:
        """Move layer to new position."""
        if 0 <= from_index < len(self.layers) and 0 <= to_index < len(self.layers):
            layer = self.layers.pop(from_index)
            self.layers.insert(to_index, layer)
            self._active_layer_index = to_index if from_index == self._active_layer_index else self._active_layer_index

    def duplicate_layer(self, index: int) -> Optional[Layer]:
        """Duplicate layer at index."""
        if 0 <= index < len(self.layers):
            layer = self.layers[index].duplicate()
            self.layers.insert(index + 1, layer)
            return layer
        return None

    def merge_down(self, index: int) -> bool:
        """Merge layer with one below it."""
        if index > 0 and index < len(self.layers):
            self.layers[index - 1].merge_with(self.layers[index])
            self.remove_layer(index)
            return True
        return False

    def flatten(self) -> Layer:
        """Merge all visible layers into one."""
        result = Layer("Flattened", self.width, self.height)

        for layer in self.layers:
            if layer.visible and layer._image is not None:
                result.merge_with(layer)

        return result

    def get_active_layer(self) -> Optional[Layer]:
        """Get currently active layer."""
        if 0 <= self._active_layer_index < len(self.layers):
            return self.layers[self._active_layer_index]
        return None

    def get_current_layer(self) -> Optional[Layer]:
        """Compatibility alias for the active layer."""
        return self.get_active_layer()

    def set_active_layer(self, index: int) -> None:
        """Set active layer index."""
        if 0 <= index < len(self.layers):
            self._active_layer_index = index

    def set_pixel(self, x: int, y: int, color: Tuple[int, int, int, int]) -> None:
        """Set pixel on active layer."""
        layer = self.get_active_layer()
        if layer:
            change = layer.set_pixel(x, y, color)
            if change:
                if self._pending_layer is not layer:
                    self._pending_changes = []
                    self._pending_layer = layer
                self._pending_changes.append(change)
                self.dirty_rect = merge_rect(self.dirty_rect, (x, y, 1, 1))

    def get_pixel(self, x: int, y: int, include_invisible: bool = False) -> Tuple[int, int, int, int]:
        """Get pixel color (topmost visible)."""
        # Search from top layer down
        for layer in reversed(self.layers):
            if include_invisible or layer.visible:
                color = layer.get_pixel(x, y)
                if color[3] > 0:  # Alpha > 0
                    return color
        return (0, 0, 0, 0)

    def get_merged_image(self) -> Image.Image:
        """Get merged image of all visible layers."""
        return self.flatten().to_image()

    def resize(self, new_width: int, new_height: int) -> None:
        """Resize canvas."""
        for layer in self.layers:
            layer.resize(new_width, new_height)
        self.width = new_width
        self.height = new_height

    def crop(self, x: int, y: int, width: int, height: int) -> None:
        """Crop canvas to region."""
        for layer in self.layers:
            image = layer.to_image().crop((x, y, x + width, y + height))
            layer._image = image
            layer.dirty_rect = (0, 0, width, height)
            layer.width = width
            layer.height = height
        self.width = width
        self.height = height

    def undo(self) -> bool:
        """Undo last action."""
        return self._undo_manager.undo()

    def redo(self) -> bool:
        """Redo last undone action."""
        return self._undo_manager.redo()

    def save_state(self, layer: Optional[Layer] = None, changes: Optional[List[PixelDelta]] = None) -> None:
        """Save state for undo."""
        if layer is None:
            layer = self._pending_layer
        if changes is None:
            changes = self._pending_changes
        if not changes:
            return
        cmd = CanvasCommand(layer, changes)
        self._undo_manager.execute(cmd)
        if changes is self._pending_changes:
            self._pending_changes = []
            self._pending_layer = None

    def load_image(self, path: str) -> bool:
        """Load image into canvas."""
        try:
            image = Image.open(path).convert("RGBA")
            self.width = image.width
            self.height = image.height
            self.layers.clear()
            layer = self.add_layer("Imported")
            layer.from_image(image)
            return True
        except Exception:
            return False

    def save_image(self, path: str) -> bool:
        """Save merged image."""
        try:
            image = self.get_merged_image()
            image.save(path)
            return True
        except Exception:
            return False

    def export(self, path: str) -> bool:
        """Export with all options."""
        path_lower = path.lower()
        
        # Handle Aseprite format
        if path_lower.endswith('.ase') or path_lower.endswith('.aseprite'):
            return self.save_aseprite(path)
        
        return self.save_image(path)

    def load_file(self, path: str) -> bool:
        """Load any supported file format."""
        path_lower = path.lower()
        
        # Handle Aseprite format
        if path_lower.endswith('.ase') or path_lower.endswith('.aseprite'):
            return self.load_aseprite(path)
        
        # Standard image formats
        return self.load_image(path)

    def save_aseprite(self, path: str) -> bool:
        """Save as Aseprite file with layers."""
        try:
            from engine.tools.pixel_art_editor.formats.aseprite_format import AsepriteFormat
            return AsepriteFormat.save_from_canvas(path, self)
        except Exception as e:
            print(f"Error saving Aseprite file: {e}")
            return False

    def load_aseprite(self, path: str) -> bool:
        """Load Aseprite file with layers."""
        try:
            from engine.tools.pixel_art_editor.formats.aseprite_format import AsepriteFormat
            return AsepriteFormat.load_to_canvas(path, self)
        except Exception as e:
            print(f"Error loading Aseprite file: {e}")
            return False

    def clear(self) -> None:
        """Clear all layers."""
        for layer in self.layers:
            layer.clear()
