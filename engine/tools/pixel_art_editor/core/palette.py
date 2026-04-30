# /**************************************************************************/
# /*  palette.py                                                            */
# /**************************************************************************/

"""Color palette for indexed color mode.

Equivalent to Aseprite's Palette class.
"""

from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from enum import Enum, auto


class ColorProfile(Enum):
    """Color profile for the palette."""
    SRGB = auto()
    ADOBE_RGB = auto()
    DISPLAY_P3 = auto()
    LINEAR = auto()


@dataclass
class PaletteEntry:
    """A single palette entry with color and name."""
    red: int
    green: int
    blue: int
    alpha: int = 255
    name: str = ""
    
    def to_rgba(self) -> Tuple[int, int, int, int]:
        """Convert to RGBA tuple."""
        return (self.red, self.green, self.blue, self.alpha)
    
    @classmethod
    def from_rgba(cls, rgba: Tuple[int, ...], name: str = "") -> 'PaletteEntry':
        """Create from RGBA tuple."""
        return cls(rgba[0], rgba[1], rgba[2], rgba[3] if len(rgba) > 3 else 255, name)


class Palette:
    """Color palette for indexed images.
    
    Supports up to 256 colors (indexed mode limitation).
    """
    
    MAX_COLORS = 256
    
    def __init__(self, name: str = "Palette", color_count: int = 256):
        self.name = name
        self.color_profile = ColorProfile.SRGB
        self._entries: List[PaletteEntry] = []
        
        # Initialize with default grayscale or black
        for i in range(min(color_count, self.MAX_COLORS)):
            if i == 0:
                # Index 0 is usually transparent
                self._entries.append(PaletteEntry(0, 0, 0, 0, "Transparent"))
            else:
                # Default colors
                self._entries.append(PaletteEntry(i, i, i, 255, f"Color {i}"))
    
    def get_entry(self, index: int) -> Optional[PaletteEntry]:
        """Get palette entry at index."""
        if 0 <= index < len(self._entries):
            return self._entries[index]
        return None
    
    def set_entry(self, index: int, entry: PaletteEntry) -> None:
        """Set palette entry at index."""
        if 0 <= index < self.MAX_COLORS:
            if index < len(self._entries):
                self._entries[index] = entry
            else:
                # Extend palette
                while len(self._entries) < index:
                    self._entries.append(PaletteEntry(0, 0, 0, 255))
                self._entries.append(entry)
    
    def add_color(self, rgba: Tuple[int, ...], name: str = "") -> int:
        """Add a color to the palette. Returns index."""
        if len(self._entries) >= self.MAX_COLORS:
            raise ValueError(f"Palette cannot exceed {self.MAX_COLORS} colors")
        
        index = len(self._entries)
        self._entries.append(PaletteEntry.from_rgba(rgba, name))
        return index
    
    def remove_color(self, index: int) -> None:
        """Remove color at index."""
        if 0 <= index < len(self._entries):
            self._entries[index] = PaletteEntry(0, 0, 0, 0, "Deleted")
    
    def find_nearest(self, rgba: Tuple[int, ...]) -> int:
        """Find nearest palette index for RGBA color."""
        if not self._entries:
            return 0
        
        r, g, b = rgba[:3]
        min_distance = float('inf')
        nearest_index = 0
        
        for i, entry in enumerate(self._entries):
            # Skip transparent
            if entry.alpha == 0:
                continue
                
            # Calculate color distance (simplified)
            dr = r - entry.red
            dg = g - entry.green
            db = b - entry.blue
            distance = dr*dr + dg*dg + db*db
            
            if distance < min_distance:
                min_distance = distance
                nearest_index = i
        
        return nearest_index
    
    def resize(self, new_size: int) -> None:
        """Resize palette to new size."""
        new_size = min(new_size, self.MAX_COLORS)
        
        if new_size > len(self._entries):
            # Extend with black
            while len(self._entries) < new_size:
                self._entries.append(PaletteEntry(0, 0, 0, 255))
        else:
            # Truncate
            self._entries = self._entries[:new_size]
    
    def copy(self) -> 'Palette':
        """Create a copy of this palette."""
        new_palette = Palette(self.name)
        new_palette._entries = [PaletteEntry(e.red, e.green, e.blue, e.alpha, e.name) 
                                for e in self._entries]
        new_palette.color_profile = self.color_profile
        return new_palette
    
    @property
    def color_count(self) -> int:
        """Get number of colors in palette."""
        return len(self._entries)
    
    def to_list(self) -> List[Tuple[int, int, int, int]]:
        """Convert to list of RGBA tuples."""
        return [entry.to_rgba() for entry in self._entries]
    
    @classmethod
    def from_list(cls, colors: List[Tuple[int, ...]], name: str = "Palette") -> 'Palette':
        """Create palette from list of RGBA tuples."""
        palette = cls(name, 0)
        palette._entries = [PaletteEntry.from_rgba(c) for c in colors[:cls.MAX_COLORS]]
        return palette
    
    @classmethod
    def default_palette(cls) -> 'Palette':
        """Create Aseprite-compatible default palette (32 colors)."""
        palette = cls("Default", 0)
        
        # Add basic colors (Aseprite default)
        colors = [
            (0, 0, 0, 0),       # Transparent
            (0, 0, 0, 255),     # Black
            (128, 128, 128, 255), # Gray
            (192, 192, 192, 255), # Light Gray
            (255, 255, 255, 255), # White
            (255, 0, 0, 255),   # Red
            (0, 255, 0, 255),   # Green
            (0, 0, 255, 255),   # Blue
            (255, 255, 0, 255), # Yellow
            (255, 0, 255, 255), # Magenta
            (0, 255, 255, 255), # Cyan
            (128, 0, 0, 255),   # Dark Red
            (0, 128, 0, 255),   # Dark Green
            (0, 0, 128, 255),   # Dark Blue
            (128, 128, 0, 255), # Olive
            (128, 0, 128, 255), # Purple
            (0, 128, 128, 255), # Teal
        ]
        
        for rgba in colors:
            palette.add_color(rgba)
        
        return palette
