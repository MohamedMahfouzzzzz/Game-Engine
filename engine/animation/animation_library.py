# /**************************************************************************/
# /*  animation_library.py                                                  */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Animation library - collection of named animations."""

from typing import Dict, Optional, List
from engine.animation.animation import Animation


class AnimationLibrary:
    """Library of named animations."""
    
    def __init__(self):
        self._animations: Dict[str, Animation] = {}
    
    def add_animation(self, name: str, animation: Animation) -> bool:
        if name in self._animations:
            return False
        self._animations[name] = animation
        return True
    
    def remove_animation(self, name: str) -> bool:
        if name in self._animations:
            del self._animations[name]
            return True
        return False
    
    def rename_animation(self, name: str, new_name: str) -> bool:
        if name not in self._animations or new_name in self._animations:
            return False
        self._animations[new_name] = self._animations.pop(name)
        return True
    
    def has_animation(self, name: str) -> bool:
        return name in self._animations
    
    def get_animation(self, name: str) -> Optional[Animation]:
        return self._animations.get(name)
    
    def get_animation_list(self) -> List[str]:
        return list(self._animations.keys())
    
    def get_animation_count(self) -> int:
        return len(self._animations)
    
    def clear(self) -> None:
        self._animations.clear()
    
    def __repr__(self) -> str:
        return f"AnimationLibrary(count={len(self._animations)}, anims={list(self._animations.keys())})"
