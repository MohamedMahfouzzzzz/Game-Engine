# /**************************************************************************/
# /*  signals/__init__.py                                                   */
# /**************************************************************************/

"""Signals/Slots system for node communication.

Godot-like signal system for decoupled communication between
engine components. Supports typed signals, automatic connection
management, and queued emission.
"""

from .signal import Signal, SignalConnection, SignalEmitOptions
from .slot import Slot, CallableSlot, MethodSlot
from .signal_manager import SignalManager

__all__ = [
    "Signal",
    "SignalConnection",
    "SignalEmitOptions",
    "Slot",
    "CallableSlot", 
    "MethodSlot",
    "SignalManager",
]
