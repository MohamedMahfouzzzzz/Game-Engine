# /**************************************************************************/
# /*  display_driver.py                                                     */
# /**************************************************************************/

"""Display/window driver abstraction.

Simplified Python port of Godot display drivers.
Uses pygame/SDL2 as backend.
"""

from enum import IntEnum
from typing import Optional, Tuple, Callable, List, Dict
from dataclasses import dataclass
from engine.godot_scene2d.types import Point2, Size2, Rect2


class DisplayMode(IntEnum):
    """Display window modes."""
    WINDOW_MODE_WINDOWED = 0
    WINDOW_MODE_MINIMIZED = 1
    WINDOW_MODE_MAXIMIZED = 2
    WINDOW_MODE_FULLSCREEN = 3
    WINDOW_MODE_EXCLUSIVE_FULLSCREEN = 4


class VSyncMode(IntEnum):
    """VSync modes."""
    VSYNC_DISABLED = 0
    VSYNC_ENABLED = 1
    VSYNC_ADAPTIVE = 2
    VSYNC_MAILBOX = 3


@dataclass
class DisplayConfig:
    """Display configuration."""
    width: int = 1024
    height: int = 768
    title: str = "Game Engine Studio"
    resizable: bool = True
    borderless: bool = False
    always_on_top: bool = False
    vsync: VSyncMode = VSyncMode.VSYNC_ENABLED
    msaa: int = 0
    fps_limit: int = 60


class DisplayDriver:
    """Abstract display driver."""
    
    def __init__(self, name: str = "DisplayDriver"):
        self._name = name
        self._config = DisplayConfig()
        self._initialized: bool = False
        self._window_id: int = 0
        self._position: Point2 = Point2(100, 100)
        self._size: Size2 = Size2(1024, 768)
        self._mode: DisplayMode = DisplayMode.WINDOW_MODE_WINDOWED
        
        # Event callbacks
        self._resize_callbacks: List[Callable[[int, int], None]] = []
        self._move_callbacks: List[Callable[[int, int], None]] = []
        self._focus_callbacks: List[Callable[[bool], None]] = []
    
    def get_name(self) -> str:
        return self._name
    
    def initialize(self) -> bool:
        """Initialize display."""
        return False
    
    def create_window(self, config: DisplayConfig) -> bool:
        """Create display window."""
        return False
    
    def destroy_window(self) -> None:
        """Destroy window."""
        pass
    
    def swap_buffers(self) -> None:
        """Swap display buffers (present frame)."""
        pass
    
    def set_title(self, title: str) -> None:
        """Set window title."""
        self._config.title = title
    
    def get_title(self) -> str:
        return self._config.title
    
    def set_size(self, width: int, height: int) -> None:
        """Set window size."""
        self._size = Size2(width, height)
    
    def get_size(self) -> Size2:
        return self._size
    
    def set_position(self, x: int, y: int) -> None:
        """Set window position."""
        self._position = Point2(x, y)
    
    def get_position(self) -> Point2:
        return self._position
    
    def set_mode(self, mode: DisplayMode) -> None:
        """Set window mode."""
        self._mode = mode
    
    def get_mode(self) -> DisplayMode:
        return self._mode
    
    def set_vsync(self, vsync: VSyncMode) -> None:
        """Set VSync mode."""
        self._config.vsync = vsync
    
    def get_vsync(self) -> VSyncMode:
        return self._config.vsync
    
    def set_resizable(self, resizable: bool) -> None:
        self._config.resizable = resizable
    
    def is_resizable(self) -> bool:
        return self._config.resizable
    
    def set_borderless(self, borderless: bool) -> None:
        self._config.borderless = borderless
    
    def is_borderless(self) -> bool:
        return self._config.borderless
    
    def set_always_on_top(self, on_top: bool) -> None:
        self._config.always_on_top = on_top
    
    def is_always_on_top(self) -> bool:
        return self._config.always_on_top
    
    def set_fps_limit(self, fps: int) -> None:
        self._config.fps_limit = max(1, fps)
    
    def get_fps_limit(self) -> int:
        return self._config.fps_limit
    
    def show(self) -> None:
        """Show window."""
        pass
    
    def hide(self) -> None:
        """Hide window."""
        pass
    
    def is_visible(self) -> bool:
        return True
    
    def has_focus(self) -> bool:
        return True
    
    def connect_resize(self, callback: Callable[[int, int], None]) -> None:
        self._resize_callbacks.append(callback)
    
    def connect_move(self, callback: Callable[[int, int], None]) -> None:
        self._move_callbacks.append(callback)
    
    def connect_focus(self, callback: Callable[[bool], None]) -> None:
        self._focus_callbacks.append(callback)


class SDL2DisplayDriver(DisplayDriver):
    """SDL2-based display driver."""
    
    def __init__(self):
        super().__init__("SDL2")
        self._screen = None
        self._clock = None
    
    def initialize(self) -> bool:
        try:
            import pygame
            pygame.init()
            pygame.display.set_caption(self._config.title)
            self._clock = pygame.time.Clock()
            self._initialized = True
            return True
        except ImportError:
            return False
    
    def create_window(self, config: DisplayConfig) -> bool:
        if not self._initialized:
            return False
        
        try:
            import pygame
            flags = 0
            if config.resizable:
                flags |= pygame.RESIZABLE
            if config.borderless:
                flags |= pygame.NOFRAME
            
            mode_map = {
                DisplayMode.WINDOW_MODE_FULLSCREEN: pygame.FULLSCREEN,
                DisplayMode.WINDOW_MODE_EXCLUSIVE_FULLSCREEN: pygame.FULLSCREEN | pygame.DOUBLEBUF,
            }
            
            if config.vsync == VSyncMode.VSYNC_ENABLED:
                flags |= pygame.DOUBLEBUF
            
            self._screen = pygame.display.set_mode((config.width, config.height), flags)
            self._config = config
            self._size = Size2(config.width, config.height)
            return True
        except:
            return False
    
    def destroy_window(self) -> None:
        try:
            import pygame
            pygame.quit()
        except:
            pass
    
    def swap_buffers(self) -> None:
        try:
            import pygame
            pygame.display.flip()
            if self._config.fps_limit > 0:
                self._clock.tick(self._config.fps_limit)
        except:
            pass
    
    def set_title(self, title: str) -> None:
        super().set_title(title)
        try:
            import pygame
            pygame.display.set_caption(title)
        except:
            pass
    
    def show(self) -> None:
        pass
    
    def hide(self) -> None:
        try:
            import pygame
            pygame.display.iconify()
        except:
            pass


class DisplayServer:
    """Singleton display server managing the current display."""
    
    _instance: Optional['DisplayServer'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._driver: Optional[DisplayDriver] = None
        return cls._instance
    
    def initialize(self, driver_name: str = "SDL2") -> bool:
        """Initialize display server with driver."""
        if driver_name == "SDL2":
            driver = SDL2DisplayDriver()
            if driver.initialize():
                self._driver = driver
                return True
        return False
    
    def create_window(self, config: Optional[DisplayConfig] = None) -> bool:
        if self._driver:
            return self._driver.create_window(config or DisplayConfig())
        return False
    
    def get_driver(self) -> Optional[DisplayDriver]:
        return self._driver
    
    def shutdown(self) -> None:
        if self._driver:
            self._driver.destroy_window()
            self._driver = None
