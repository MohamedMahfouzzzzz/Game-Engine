"""Context-aware editor action registry."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional


@dataclass(slots=True)
class RegisteredAction:
    name: str
    shortcut: str
    callback: Callable[[], None]
    context: str = "global"


class ActionRegistry:
    """Dispatch shortcuts by active editor context.

    Context-specific actions win over global actions, so the same shortcut can
    save a sprite in the pixel editor and save a scene/project in the main UI.
    """

    def __init__(self) -> None:
        self._actions: Dict[str, List[RegisteredAction]] = {}
        self._context_stack: List[str] = ["global"]

    @property
    def active_context(self) -> str:
        return self._context_stack[-1] if self._context_stack else "global"

    def push_context(self, context: str) -> None:
        if not context:
            return
        if context in self._context_stack:
            self._context_stack.remove(context)
        self._context_stack.append(context)

    def pop_context(self, context: Optional[str] = None) -> None:
        if len(self._context_stack) <= 1:
            return
        if context is None:
            self._context_stack.pop()
            return
        if context in self._context_stack and context != "global":
            self._context_stack.remove(context)

    def register(self, action: RegisteredAction) -> None:
        bucket = self._actions.setdefault(action.shortcut, [])
        bucket[:] = [
            existing for existing in bucket
            if not (existing.name == action.name and existing.context == action.context)
        ]
        bucket.append(action)

    def trigger(self, shortcut: str) -> bool:
        bucket = self._actions.get(shortcut, [])
        if not bucket:
            return False
        for context in reversed(self._context_stack):
            for action in reversed(bucket):
                if action.context == context:
                    action.callback()
                    return True
        for action in reversed(bucket):
            if action.context == "global":
                action.callback()
                return True
        return False
