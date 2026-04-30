# /**************************************************************************/
# /*  image_loader.py                                                       */
# /**************************************************************************/

"""Image loading drivers - PNG and other formats.

Simplified Python port of Godot image loader drivers.
"""

from typing import Optional, Tuple, List, BinaryIO, Union
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path


class ImageFormat(IntEnum):
    """Supported image formats."""
    FORMAT_L8 = 0          # Grayscale
    FORMAT_LA8 = 1         # Grayscale + Alpha
    FORMAT_R8 = 2          # Red only
    FORMAT_RG8 = 3         # RG
    FORMAT_RGB8 = 4        # RGB
    FORMAT_RGBA8 = 5       # RGBA
    FORMAT_RGBA4444 = 6    # RGBA 4-bit per channel
    FORMAT_RGB565 = 7      # RGB 565
    FORMAT_RF = 8          # Red float
    FORMAT_RGF = 9         # RG float
    FORMAT_RGBF = 10       # RGB float
    FORMAT_RGBAF = 11      # RGBA float
    FORMAT_RH = 12         # Red half-float
    FORMAT_RGH = 13        # RG half-float
    FORMAT_RGBH = 14       # RGB half-float
    FORMAT_RGBAH = 15      # RGBA half-float
    FORMAT_MAX = 16


@dataclass
class ImageData:
    """Loaded image data."""
    width: int = 0
    height: int = 0
    format: ImageFormat = ImageFormat.FORMAT_RGBA8
    data: bytes = b''
    mipmaps: bool = False


class ImageLoader:
    """Base image loader."""
    
    def __init__(self, name: str, extensions: List[str]):
        self._name = name
        self._extensions = [ext.lower() for ext in extensions]
    
    def get_name(self) -> str:
        return self._name
    
    def get_extensions(self) -> List[str]:
        return self._extensions.copy()
    
    def can_load(self, path: str) -> bool:
        """Check if this loader can handle the file."""
        ext = Path(path).suffix.lower().lstrip('.')
        return ext in self._extensions
    
    def load(self, path_or_data: Union[str, bytes, BinaryIO]) -> Optional[ImageData]:
        """Load image from file path or data."""
        return None
    
    def save(self, path: str, image: ImageData) -> bool:
        """Save image to file."""
        return False


class PNGLoader(ImageLoader):
    """PNG image loader using PIL/Pillow."""
    
    def __init__(self):
        super().__init__("PNG", ["png"])
        self._pil_available = self._check_pil()
    
    def _check_pil(self) -> bool:
        try:
            from PIL import Image
            return True
        except ImportError:
            return False
    
    def load(self, path_or_data: Union[str, bytes, BinaryIO]) -> Optional[ImageData]:
        if not self._pil_available:
            return self._load_fallback(path_or_data)
        
        try:
            from PIL import Image
            
            if isinstance(path_or_data, str):
                img = Image.open(path_or_data)
            elif isinstance(path_or_data, bytes):
                from io import BytesIO
                img = Image.open(BytesIO(path_or_data))
            else:
                img = Image.open(path_or_data)
            
            # Convert to RGBA
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            width, height = img.size
            data = img.tobytes()
            
            return ImageData(
                width=width,
                height=height,
                format=ImageFormat.FORMAT_RGBA8,
                data=data
            )
        except Exception:
            return None
    
    def save(self, path: str, image: ImageData) -> bool:
        if not self._pil_available:
            return False
        
        try:
            from PIL import Image
            from io import BytesIO
            
            mode_map = {
                ImageFormat.FORMAT_RGBA8: 'RGBA',
                ImageFormat.FORMAT_RGB8: 'RGB',
                ImageFormat.FORMAT_L8: 'L',
                ImageFormat.FORMAT_LA8: 'LA',
            }
            
            mode = mode_map.get(image.format, 'RGBA')
            img = Image.frombytes(mode, (image.width, image.height), image.data)
            img.save(path, 'PNG')
            return True
        except Exception:
            return False
    
    def _load_fallback(self, path_or_data: Union[str, bytes, BinaryIO]) -> Optional[ImageData]:
        """Simple PNG loader fallback using pygame if PIL not available."""
        try:
            import pygame
            if isinstance(path_or_data, str):
                surface = pygame.image.load(path_or_data)
                width, height = surface.get_size()
                data = pygame.image.tostring(surface, 'RGBA')
                return ImageData(width, height, ImageFormat.FORMAT_RGBA8, data)
        except:
            pass
        return None


class BMPLoader(ImageLoader):
    """BMP image loader."""
    
    def __init__(self):
        super().__init__("BMP", ["bmp"])
    
    def load(self, path_or_data: Union[str, bytes, BinaryIO]) -> Optional[ImageData]:
        try:
            import pygame
            if isinstance(path_or_data, str):
                surface = pygame.image.load(path_or_data)
                width, height = surface.get_size()
                data = pygame.image.tostring(surface, 'RGBA')
                return ImageData(width, height, ImageFormat.FORMAT_RGBA8, data)
        except:
            pass
        return None


class JPEGLoader(ImageLoader):
    """JPEG image loader."""
    
    def __init__(self):
        super().__init__("JPEG", ["jpg", "jpeg"])
    
    def load(self, path_or_data: Union[str, bytes, BinaryIO]) -> Optional[ImageData]:
        try:
            import pygame
            if isinstance(path_or_data, str):
                surface = pygame.image.load(path_or_data)
                width, height = surface.get_size()
                data = pygame.image.tostring(surface, 'RGBA')
                return ImageData(width, height, ImageFormat.FORMAT_RGBA8, data)
        except:
            pass
        return None


class ImageLoaderManager:
    """Manages all image loaders."""
    
    def __init__(self):
        self._loaders: List[ImageLoader] = []
        self._register_builtin_loaders()
    
    def _register_builtin_loaders(self) -> None:
        """Register built-in image loaders."""
        self._loaders.append(PNGLoader())
        self._loaders.append(BMPLoader())
        self._loaders.append(JPEGLoader())
    
    def register_loader(self, loader: ImageLoader) -> None:
        """Register a custom loader."""
        self._loaders.append(loader)
    
    def get_loader_for_file(self, path: str) -> Optional[ImageLoader]:
        """Get appropriate loader for file."""
        for loader in self._loaders:
            if loader.can_load(path):
                return loader
        return None
    
    def load(self, path: str) -> Optional[ImageData]:
        """Load image using appropriate loader."""
        loader = self.get_loader_for_file(path)
        if loader:
            return loader.load(path)
        return None
    
    def save(self, path: str, image: ImageData) -> bool:
        """Save image using appropriate loader."""
        loader = self.get_loader_for_file(path)
        if loader:
            return loader.save(path, image)
        return False


# Global singleton
_image_loader_manager: Optional[ImageLoaderManager] = None


def get_image_loader() -> ImageLoaderManager:
    """Get global image loader manager."""
    global _image_loader_manager
    if _image_loader_manager is None:
        _image_loader_manager = ImageLoaderManager()
    return _image_loader_manager
