# /**************************************************************************/
# /*  transaction.py                                                        */
# /**************************************************************************/

"""Transaction support for command grouping.

Allows multiple commands to be grouped into a single undoable unit.
"""

from typing import Optional, List
from contextlib import contextmanager

from .command import Command, CommandResult
from .command_history import CommandHistory


class Transaction:
    """A transaction groups multiple commands into one undoable unit.
    
    Usage:
        with Transaction(history, "Brush Stroke"):
            history.execute(cmd1)
            history.execute(cmd2)
            history.execute(cmd3)
        # All 3 commands are grouped as "Brush Stroke"
    
    Or manual mode:
        transaction = Transaction(history, "Move Layers")
        transaction.begin()
        history.execute(cmd1)
        history.execute(cmd2)
        transaction.end()
    """
    
    def __init__(self, 
                 history: CommandHistory, 
                 name: str = "Transaction",
                 auto_commit: bool = True):
        self._history = history
        self._name = name
        self._auto_commit = auto_commit
        self._is_active = False
    
    def begin(self) -> 'Transaction':
        """Begin the transaction."""
        self._history.begin_transaction(self._name)
        self._is_active = True
        return self
    
    def end(self) -> None:
        """End and commit the transaction."""
        if self._is_active:
            self._history.end_transaction()
            self._is_active = False
    
    def cancel(self) -> None:
        """Cancel the transaction (undo all pending commands)."""
        if self._is_active:
            self._history.cancel_transaction()
            self._is_active = False
    
    def __enter__(self) -> 'Transaction':
        """Context manager entry."""
        return self.begin()
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Context manager exit.
        
        If an exception occurred, cancel the transaction.
        Otherwise, commit it.
        """
        if exc_type is not None:
            # An exception occurred, cancel the transaction
            self.cancel()
            return False  # Re-raise the exception
        else:
            # Success, commit the transaction
            self.end()
            return True
    
    def is_active(self) -> bool:
        """Check if transaction is active."""
        return self._is_active


@contextmanager
def transaction(history: CommandHistory, name: str = "Transaction"):
    """Context manager for transactions.
    
    Usage:
        with transaction(history, "Brush Stroke"):
            for pixel in brush_stroke:
                history.execute(DrawPixelCommand(...))
    """
    t = Transaction(history, name)
    t.begin()
    try:
        yield t
    except Exception:
        t.cancel()
        raise
    else:
        t.end()
