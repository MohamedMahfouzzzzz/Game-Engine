# /**************************************************************************/
# /*  __init__.py                                                           */
# /**************************************************************************/

"""Driver abstraction layer - Simplified Python port of Godot drivers.

This module provides platform abstraction for:
- Audio output (cross-platform)
- Image codecs (PNG)
- Display/window management
- Input handling
"""

from engine.drivers.audio_driver import AudioDriver, AudioDriverManager
from engine.drivers.display_driver import DisplayDriver, DisplayServer
from engine.drivers.image_loader import ImageLoader, PNGLoader
from engine.drivers.input_driver import InputDriver, InputManager

__all__ = [
    # Audio
    "AudioDriver", "AudioDriverManager",
    # Display
    "DisplayDriver", "DisplayServer", 
    # Images
    "ImageLoader", "PNGLoader",
    # Input
    "InputDriver", "InputManager",
]
