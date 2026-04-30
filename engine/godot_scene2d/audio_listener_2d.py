# /**************************************************************************/
# /*  audio_listener_2d.py                                                  */
# /**************************************************************************/

"""Godot AudioListener2D port - 2D audio listener."""

from engine.core.nodes2d import Node2D


class AudioListener2D(Node2D):
    """2D audio listener - the 'ears' for 2D sound."""
    
    def __init__(self, name: str = "AudioListener2D"):
        super().__init__(name)
        self._current: bool = False
    
    def make_current(self) -> None:
        """Make this the current active listener."""
        self._current = True
    
    def clear_current(self) -> None:
        """Clear as current listener."""
        self._current = False
    
    def is_current(self) -> bool:
        """Check if this is the current listener."""
        return self._current
    
    def get_listener_transform(self) -> any:
        """Get transform for spatial audio."""
        return self._transform if hasattr(self, '_transform') else None
    
    def __repr__(self) -> str:
        return f"AudioListener2D('{self.name}', current={self._current})"
