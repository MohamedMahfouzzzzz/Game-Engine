# /**************************************************************************/
# /*  brush_manager.py                                                      */
# /**************************************************************************/

"""Brush manager for organizing and retrieving brushes."""

from typing import Dict, List, Optional, Callable
from pathlib import Path
import json

from engine.tools.pixel_art_editor.core.brush import Brush, BrushType


class BrushCategory:
    """Category of brushes."""
    
    def __init__(self, name: str, icon: str = ""):
        self.name = name
        self.icon = icon
        self._brushes: Dict[str, Brush] = {}
    
    def add_brush(self, brush: Brush) -> None:
        """Add brush to category."""
        self._brushes[brush.name] = brush
    
    def remove_brush(self, name: str) -> bool:
        """Remove brush by name."""
        if name in self._brushes:
            del self._brushes[name]
            return True
        return False
    
    def get_brush(self, name: str) -> Optional[Brush]:
        """Get brush by name."""
        return self._brushes.get(name)
    
    def get_brushes(self) -> List[Brush]:
        """Get all brushes in category."""
        return list(self._brushes.values())
    
    def __len__(self) -> int:
        return len(self._brushes)


class BrushManager:
    """Manages brush categories and favorites.
    
    Provides organized access to brushes by category:
    - Basic: Circle, square, line brushes
    - Pixels: Single pixel, dither patterns
    - Artistic: Texture brushes, patterns
    - Custom: User-defined brushes
    """
    
    def __init__(self):
        self._categories: Dict[str, BrushCategory] = {}
        self._favorites: List[str] = []  # brush names
        self._recent: List[str] = []  # recently used
        self._max_recent = 10
        
        self._on_change: Optional[Callable] = None
        
        # Initialize default categories
        self._init_default_categories()
    
    def _init_default_categories(self) -> None:
        """Initialize default brush categories."""
        self.add_category("Basic", "brush")
        self.add_category("Pixels", "square")
        self.add_category("Artistic", "paint")
        self.add_category("Custom", "user")
    
    def add_category(self, name: str, icon: str = "") -> BrushCategory:
        """Add a brush category."""
        category = BrushCategory(name, icon)
        self._categories[name] = category
        return category
    
    def remove_category(self, name: str) -> bool:
        """Remove a category."""
        if name in self._categories and name not in ("Basic", "Pixels"):
            del self._categories[name]
            return True
        return False
    
    def get_category(self, name: str) -> Optional[BrushCategory]:
        """Get category by name."""
        return self._categories.get(name)
    
    def get_categories(self) -> List[str]:
        """Get list of category names."""
        return list(self._categories.keys())
    
    def add_brush(self, category_name: str, brush: Brush) -> bool:
        """Add brush to category."""
        category = self._categories.get(category_name)
        if category is not None:
            category.add_brush(brush)
            self._notify_change()
            return True
        return False
    
    def get_brush(self, name: str, category: str = None) -> Optional[Brush]:
        """Get brush by name, optionally restricted to category."""
        if category:
            cat = self._categories.get(category)
            if cat:
                return cat.get_brush(name)
            return None
        
        # Search all categories
        for cat in self._categories.values():
            brush = cat.get_brush(name)
            if brush:
                return brush
        return None
    
    def use_brush(self, name: str) -> None:
        """Mark brush as used (adds to recent)."""
        # Add to recent
        if name in self._recent:
            self._recent.remove(name)
        self._recent.insert(0, name)
        
        # Trim
        if len(self._recent) > self._max_recent:
            self._recent = self._recent[:self._max_recent]
        
        self._notify_change()
    
    def add_favorite(self, name: str) -> bool:
        """Add brush to favorites."""
        if name not in self._favorites:
            self._favorites.append(name)
            self._notify_change()
            return True
        return False
    
    def remove_favorite(self, name: str) -> bool:
        """Remove brush from favorites."""
        if name in self._favorites:
            self._favorites.remove(name)
            self._notify_change()
            return True
        return False
    
    def is_favorite(self, name: str) -> bool:
        """Check if brush is a favorite."""
        return name in self._favorites
    
    def get_favorites(self) -> List[Brush]:
        """Get favorite brushes."""
        result = []
        for name in self._favorites:
            brush = self.get_brush(name)
            if brush:
                result.append(brush)
        return result
    
    def get_recent(self) -> List[Brush]:
        """Get recently used brushes."""
        result = []
        for name in self._recent:
            brush = self.get_brush(name)
            if brush:
                result.append(brush)
        return result
    
    def get_all_brushes(self) -> Dict[str, List[Brush]]:
        """Get all brushes organized by category."""
        return {
            name: cat.get_brushes()
            for name, cat in self._categories.items()
        }
    
    def set_on_change(self, callback: Callable) -> None:
        """Set callback for changes."""
        self._on_change = callback
    
    def _notify_change(self) -> None:
        """Notify listeners of change."""
        if self._on_change:
            self._on_change()
    
    def save_presets(self, filepath: str) -> bool:
        """Save brush presets to file."""
        try:
            data = {
                'favorites': self._favorites,
                'recent': self._recent,
                'custom_brushes': []
            }
            
            # Save custom brushes from Custom category
            custom = self._categories.get('Custom')
            if custom:
                for brush in custom.get_brushes():
                    data['custom_brushes'].append({
                        'name': brush.name,
                        'type': brush.type.name,
                        'size': brush.size,
                        'opacity': brush.opacity,
                    })
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving brush presets: {e}")
            return False
    
    def load_presets(self, filepath: str) -> bool:
        """Load brush presets from file."""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self._favorites = data.get('favorites', [])
            self._recent = data.get('recent', [])
            
            # Load custom brushes
            custom_brushes = data.get('custom_brushes', [])
            custom = self._categories.get('Custom')
            if custom and custom_brushes:
                for brush_data in custom_brushes:
                    brush = Brush(
                        brush_data['name'],
                        BrushType[brush_data['type']],
                        brush_data['size']
                    )
                    brush.opacity = brush_data.get('opacity', 1.0)
                    custom.add_brush(brush)
            
            self._notify_change()
            return True
        except Exception as e:
            print(f"Error loading brush presets: {e}")
            return False
