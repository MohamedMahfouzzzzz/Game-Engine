# /**************************************************************************/
# /*  audio_listener.py                                                     */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""2D audio listener position."""

from engine.core.nodes2d import Node2D


class AudioListener2D(Node2D):
    """Defines the position where 2D audio is heard from.
    
    AudioStreamPlayer2D nodes calculate their volume/panning
    based on their distance and angle to the active listener.
    """
    
    def __init__(self, name: str = "AudioListener2D"):
        super().__init__(name)
        self._active: bool = True
        self._current: bool = False
    
    def set_active(self, active: bool) -> None:
        """Enable/disable this listener."""
        self._active = active
    
    def is_active(self) -> bool:
        return self._active
    
    def make_current(self) -> None:
        """Make this the active listener for audio."""
        self._current = True
    
    def clear_current(self) -> None:
        """Clear as current listener."""
        self._current = False
    
    def is_current(self) -> bool:
        """Returns true if this is the current audio listener."""
        return self._current
    
    def get_rid(self) -> int:
        """Get audio server RID."""
        return id(self)
    
    def __repr__(self) -> str:
        return f"AudioListener2D('{self.name}', current={self._current})"
