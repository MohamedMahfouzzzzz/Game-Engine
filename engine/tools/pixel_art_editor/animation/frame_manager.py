# /**************************************************************************/
# /*  frame_manager.py                                                      */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Frame management for sprite animation."""

from typing import List, Optional, Dict
from dataclasses import dataclass
from PIL import Image


@dataclass
class Frame:
    """Single animation frame."""
    index: int
    duration: int  # Frames to display (at timeline FPS)
    layers: Dict[str, Image.Image]  # Layer name -> image


class FrameManager:
    """Manages animation frames and layers."""

    def __init__(self):
        self._frames: List[Frame] = []
        self._current_frame: int = 0
        self._layer_names: List[str] = ["Layer 1"]

    def add_frame(self, duration: int = 1) -> Frame:
        """Add new frame."""
        frame = Frame(
            index=len(self._frames),
            duration=duration,
            layers={name: Image.new("RGBA", (64, 64), (0, 0, 0, 0))
                    for name in self._layer_names}
        )
        self._frames.append(frame)
        return frame

    def duplicate_frame(self, index: int) -> Optional[Frame]:
        """Duplicate frame at index."""
        if 0 <= index < len(self._frames):
            source = self._frames[index]
            frame = Frame(
                index=len(self._frames),
                duration=source.duration,
                layers={name: img.copy() for name, img in source.layers.items()}
            )
            self._frames.append(frame)
            return frame
        return None

    def delete_frame(self, index: int) -> bool:
        """Delete frame at index."""
        if 0 <= index < len(self._frames) and len(self._frames) > 1:
            del self._frames[index]
            # Re-index
            for i, frame in enumerate(self._frames):
                frame.index = i
            return True
        return False

    def get_frame(self, index: int) -> Optional[Frame]:
        """Get frame by index."""
        if 0 <= index < len(self._frames):
            return self._frames[index]
        return None

    def add_layer(self, name: str) -> None:
        """Add new layer to all frames."""
        if name not in self._layer_names:
            self._layer_names.append(name)
            for frame in self._frames:
                if name not in frame.layers:
                    frame.layers[name] = Image.new("RGBA", (64, 64), (0, 0, 0, 0))

    def remove_layer(self, name: str) -> None:
        """Remove layer from all frames."""
        if name in self._layer_names and len(self._layer_names) > 1:
            self._layer_names.remove(name)
            for frame in self._frames:
                if name in frame.layers:
                    del frame.layers[name]

    def get_layer_image(self, frame_index: int, layer_name: str) -> Optional[Image.Image]:
        """Get layer image for specific frame."""
        frame = self.get_frame(frame_index)
        if frame:
            return frame.layers.get(layer_name)
        return None

    def set_layer_image(
        self,
        frame_index: int,
        layer_name: str,
        image: Image.Image
    ) -> bool:
        """Set layer image for specific frame."""
        frame = self.get_frame(frame_index)
        if frame and layer_name in frame.layers:
            frame.layers[layer_name] = image
            return True
        return False

    def export_sprite_sheet(
        self,
        output_path: str,
        columns: int = 8
    ) -> bool:
        """Export all frames as sprite sheet."""
        if not self._frames:
            return False

        # Get frame dimensions from first frame
        first_frame = self._frames[0]
        sample_img = list(first_frame.layers.values())[0]
        frame_w, frame_h = sample_img.size

        # Calculate rows
        rows = (len(self._frames) + columns - 1) // columns

        # Create sprite sheet
        sheet = Image.new(
            "RGBA",
            (frame_w * columns, frame_h * rows),
            (0, 0, 0, 0)
        )

        for i, frame in enumerate(self._frames):
            # Merge layers
            merged = Image.new("RGBA", (frame_w, frame_h), (0, 0, 0, 0))
            for layer_name in self._layer_names:
                if layer_name in frame.layers:
                    merged = Image.alpha_composite(merged, frame.layers[layer_name])

            # Paste into sheet
            col = i % columns
            row = i // columns
            sheet.paste(merged, (col * frame_w, row * frame_h))

        sheet.save(output_path)
        return True

    @property
    def frame_count(self) -> int:
        return len(self._frames)

    @property
    def layer_names(self) -> List[str]:
        return self._layer_names.copy()
