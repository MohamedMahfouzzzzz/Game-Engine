# engine/core/signals.py
# Lightweight signal bus — snapshot-before-dispatch bug fixed, once() added
from __future__ import annotations
import logging, weakref
from collections import defaultdict
from typing import Any, Callable, DefaultDict, Dict, List, Optional

logger = logging.getLogger(__name__)


class _WeakCallback:
    __slots__ = ("_ref", "_is_method", "_dead", "_once")

    def __init__(self, callback: Callable, once: bool = False) -> None:
        self._dead = False
        self._once = once
        if hasattr(callback, "__self__"):
            self._ref: Any = weakref.WeakMethod(callback, self._on_dead)  # type: ignore[arg-type]
            self._is_method = True
        else:
            self._ref = weakref.ref(callback, self._on_dead)
            self._is_method = False

    def _on_dead(self, _ref: Any) -> None:
        self._dead = True

    def __call__(self, *args: Any, **kwargs: Any) -> None:
        if self._dead:
            return
        fn = self._ref()
        if fn is not None:
            fn(*args, **kwargs)
        else:
            self._dead = True

    def matches(self, callback: Callable) -> bool:
        if self._dead:
            return False
        fn = self._ref()
        return fn == callback

    def __eq__(self, other: object) -> bool:
        if isinstance(other, _WeakCallback):
            return self._ref == other._ref
        return NotImplemented

    def __hash__(self) -> int:
        return id(self._ref)


class SignalBus:
    def __init__(self) -> None:
        self._listeners: DefaultDict[str, List[_WeakCallback]] = defaultdict(list)

    def connect(self, signal: str, callback: Callable[..., None]) -> None:
        listeners = self._listeners[signal]
        if any(wc.matches(callback) for wc in listeners):
            return
        listeners.append(_WeakCallback(callback, once=False))

    def once(self, signal: str, callback: Callable[..., None]) -> None:
        listeners = self._listeners[signal]
        if any(wc.matches(callback) for wc in listeners):
            return
        listeners.append(_WeakCallback(callback, once=True))

    def disconnect(self, signal: str, callback: Callable[..., None]) -> None:
        self._listeners[signal] = [wc for wc in self._listeners[signal] if not wc.matches(callback)]

    def disconnect_all(self, signal: Optional[str] = None) -> None:
        if signal is None:
            self._listeners.clear()
        else:
            self._listeners.pop(signal, None)

    def emit(self, signal: str, *args: Any, **kwargs: Any) -> None:
        raw = self._listeners.get(signal)
        if not raw:
            return
        snapshot = [wc for wc in raw if not wc._dead]
        for wc in snapshot:
            if not wc._dead:
                wc(*args, **kwargs)
                if wc._once:
                    wc._dead = True
        if signal in self._listeners:
            self._listeners[signal] = [wc for wc in self._listeners[signal] if not wc._dead]

    def has_listeners(self, signal: str) -> bool:
        self._prune(signal)
        return bool(self._listeners.get(signal))

    def list_signals(self) -> List[str]:
        return [s for s in self._listeners if self._listeners[s]]

    def to_dict(self) -> Dict[str, int]:
        return {name: sum(1 for wc in wcs if not wc._dead) for name, wcs in self._listeners.items()}

    def _prune(self, signal: str) -> None:
        if signal in self._listeners:
            self._listeners[signal] = [wc for wc in self._listeners[signal] if not wc._dead]
