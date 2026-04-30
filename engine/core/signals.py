# /**************************************************************************/
# /*  signals.py                                                            */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""
Lightweight signal / event bus.

Uses *weak references* to callbacks so that deleted nodes never leak memory
through dangling listeners.  Bound methods are supported via
``weakref.WeakMethod``.
"""

from __future__ import annotations

import logging
import weakref
from collections import defaultdict
from typing import Any, Callable, DefaultDict, Dict, Iterator, List, Optional

logger = logging.getLogger(__name__)


class _WeakCallback:
    """Wrapper that holds a weak reference to a callback (plain function
    or bound method) and cleans itself up when the target is GC'd."""

    __slots__ = ("_ref", "_is_method", "_dead")

    def __init__(self, callback: Callable) -> None:
        self._dead = False
        if hasattr(callback, "__self__"):
            # Bound method – use WeakMethod
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

    def matches(self, callback: Callable) -> bool:
        """Return True if this wrapper holds *callback*."""
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
    """Thread-compatible signal bus with automatic memory management.

    Example::

        bus = SignalBus()
        bus.connect("health_changed", self.on_health_changed)
        bus.emit("health_changed", new_health=50)
        bus.disconnect("health_changed", self.on_health_changed)
    """

    def __init__(self) -> None:
        self._listeners: DefaultDict[str, List[_WeakCallback]] = defaultdict(list)

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------

    def connect(self, signal: str, callback: Callable[..., None]) -> None:
        """Subscribe *callback* to *signal*.  Duplicate connections are ignored."""
        listeners = self._listeners[signal]
        # Skip if already connected (and still alive)
        if any(wc.matches(callback) for wc in listeners):
            return
        listeners.append(_WeakCallback(callback))

    def disconnect(self, signal: str, callback: Callable[..., None]) -> None:
        """Unsubscribe *callback* from *signal*."""
        self._listeners[signal] = [
            wc for wc in self._listeners[signal] if not wc.matches(callback)
        ]

    def disconnect_all(self, signal: Optional[str] = None) -> None:
        """Remove all listeners for *signal*, or for every signal if None."""
        if signal is None:
            self._listeners.clear()
        else:
            self._listeners.pop(signal, None)

    # ------------------------------------------------------------------
    # Emission
    # ------------------------------------------------------------------

    def emit(self, signal: str, *args: Any, **kwargs: Any) -> None:
        """Fire *signal* — dead weak-refs are pruned automatically."""
        live: List[_WeakCallback] = []
        for wc in list(self._listeners.get(signal, [])):
            if not wc._dead:
                wc(*args, **kwargs)
                live.append(wc)
        if signal in self._listeners:
            self._listeners[signal] = live

    # ------------------------------------------------------------------
    # Introspection / serialisation
    # ------------------------------------------------------------------

    def has_listeners(self, signal: str) -> bool:
        self._prune(signal)
        return bool(self._listeners.get(signal))

    def list_signals(self) -> List[str]:
        return [s for s in self._listeners if self._listeners[s]]

    def to_dict(self) -> Dict[str, int]:
        """Return ``{signal_name: listener_count}`` for debugging."""
        return {
            name: sum(1 for wc in wcs if not wc._dead)
            for name, wcs in self._listeners.items()
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _prune(self, signal: str) -> None:
        if signal in self._listeners:
            self._listeners[signal] = [
                wc for wc in self._listeners[signal] if not wc._dead
            ]
