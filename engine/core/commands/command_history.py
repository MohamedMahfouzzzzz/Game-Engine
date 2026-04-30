# /**************************************************************************/
# /*  command_history.py                                                    */
# /**************************************************************************/

"""Command history for undo/redo system.

Manages the stack of executed commands and provides
undo/redo functionality.
"""

from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass
from datetime import datetime
import uuid

from .command import Command, CommandResult


@dataclass
class HistoryEntry:
    """A single entry in the command history."""
    command: Command
    timestamp: datetime
    document_state_hash: Optional[str] = None


class CommandHistory:
    """Manages command history for undo/redo.
    
    Implements an unlimited undo/redo stack with:
    - Command grouping (transactions)
    - Command merging (for brush strokes)
    - History navigation
    - State snapshots for debugging
    
    Similar to Aseprite's undo system.
    """
    
    def __init__(self, max_size: int = 0):
        """Initialize command history.
        
        Args:
            max_size: Maximum number of commands to keep (0 = unlimited)
        """
        self._entries: List[HistoryEntry] = []
        self._current_index: int = -1  # -1 means before first command
        self._max_size = max_size
        self._group_depth = 0  # For transaction grouping
        self._pending_group: Optional[List[Command]] = None
        
        # Callbacks
        self._on_change: Optional[Callable] = None
        self._on_undo: Optional[Callable] = None
        self._on_redo: Optional[Callable] = None
    
    @property
    def can_undo(self) -> bool:
        """Check if undo is available."""
        return self._current_index >= 0
    
    @property
    def can_redo(self) -> bool:
        """Check if redo is available."""
        return self._current_index < len(self._entries) - 1
    
    @property
    def undo_count(self) -> int:
        """Get number of commands that can be undone."""
        return self._current_index + 1
    
    @property
    def redo_count(self) -> int:
        """Get number of commands that can be redone."""
        return len(self._entries) - self._current_index - 1
    
    @property
    def is_at_beginning(self) -> bool:
        """Check if at beginning of history."""
        return self._current_index == -1
    
    @property
    def is_at_end(self) -> bool:
        """Check if at end of history."""
        return self._current_index == len(self._entries) - 1
    
    def execute(self, command: Command) -> CommandResult:
        """Execute a command and add to history.
        
        If we're not at the end of history, future commands
        are discarded (like a new branch in git).
        """
        # Check if can execute
        if not command.can_execute():
            return CommandResult.FAILED
        
        # Execute the command
        result = command.execute()
        
        if result != CommandResult.SUCCESS and result != CommandResult.NO_OP:
            return result
        
        # If we're in a transaction group, add to pending group
        if self._group_depth > 0 and self._pending_group is not None:
            self._pending_group.append(command)
            return result
        
        # If we're in the middle of history, truncate future commands
        if not self.is_at_end:
            # Remove all entries after current
            self._entries = self._entries[:self._current_index + 1]
        
        # Try to merge with previous command
        if self._entries and not self.is_at_beginning:
            last_entry = self._entries[self._current_index]
            merged = command.merge_with(last_entry.command)
            if merged:
                # Replace last command with merged command
                merged._mark_executed()
                self._entries[self._current_index] = HistoryEntry(
                    merged, datetime.now()
                )
                self._notify_change()
                return result
        
        # Add new entry
        entry = HistoryEntry(command, datetime.now())
        self._entries.append(entry)
        self._current_index += 1
        
        # Enforce max size
        if self._max_size > 0 and len(self._entries) > self._max_size:
            # Remove oldest entries
            excess = len(self._entries) - self._max_size
            self._entries = self._entries[excess:]
            self._current_index -= excess
            if self._current_index < -1:
                self._current_index = -1
        
        self._notify_change()
        return result
    
    def undo(self) -> bool:
        """Undo the last command.
        
        Returns:
            True if undo was successful, False otherwise.
        """
        if not self.can_undo:
            return False
        
        entry = self._entries[self._current_index]
        result = entry.command.undo()
        
        if result == CommandResult.SUCCESS:
            self._current_index -= 1
            if self._on_undo:
                self._on_undo(entry.command)
            self._notify_change()
            return True
        
        return False
    
    def redo(self) -> bool:
        """Redo the next command.
        
        Returns:
            True if redo was successful, False otherwise.
        """
        if not self.can_redo:
            return False
        
        next_index = self._current_index + 1
        entry = self._entries[next_index]
        result = entry.command.redo()
        
        if result == CommandResult.SUCCESS:
            self._current_index = next_index
            if self._on_redo:
                self._on_redo(entry.command)
            self._notify_change()
            return True
        
        return False
    
    def undo_all(self) -> int:
        """Undo all commands.
        
        Returns:
            Number of commands undone.
        """
        count = 0
        while self.undo():
            count += 1
        return count
    
    def redo_all(self) -> int:
        """Redo all commands.
        
        Returns:
            Number of commands redone.
        """
        count = 0
        while self.redo():
            count += 1
        return count
    
    def clear(self) -> None:
        """Clear all history."""
        self._entries.clear()
        self._current_index = -1
        self._pending_group = None
        self._group_depth = 0
        self._notify_change()
    
    def get_undo_label(self) -> Optional[str]:
        """Get label for next undo command."""
        if self.can_undo:
            return self._entries[self._current_index].command.name
        return None
    
    def get_redo_label(self) -> Optional[str]:
        """Get label for next redo command."""
        if self.can_redo:
            return self._entries[self._current_index + 1].command.name
        return None
    
    def get_undo_stack(self) -> List[str]:
        """Get list of undoable command names."""
        return [e.command.name for e in self._entries[:self._current_index + 1]]
    
    def get_redo_stack(self) -> List[str]:
        """Get list of redoable command names."""
        return [e.command.name for e in self._entries[self._current_index + 1:]]
    
    def begin_transaction(self, name: str) -> None:
        """Begin a transaction (command grouping).
        
        All commands executed until end_transaction() will be
        grouped into a single undoable unit.
        """
        self._group_depth += 1
        if self._group_depth == 1:
            self._pending_group = []
    
    def end_transaction(self) -> None:
        """End a transaction.
        
        The grouped commands are added to history as a single unit.
        """
        if self._group_depth > 0:
            self._group_depth -= 1
            
            if self._group_depth == 0 and self._pending_group:
                # Create compound command
                from .command import CompoundCommand
                compound = CompoundCommand(
                    f"Transaction ({len(self._pending_group)} commands)",
                    self._pending_group.copy()
                )
                self.execute(compound)
                self._pending_group = None
    
    def cancel_transaction(self) -> None:
        """Cancel current transaction without adding to history."""
        if self._group_depth > 0 and self._pending_group:
            # Undo all pending commands
            for cmd in reversed(self._pending_group):
                cmd.undo()
        
        self._group_depth = 0
        self._pending_group = None
    
    def set_callbacks(self, 
                      on_change: Optional[Callable] = None,
                      on_undo: Optional[Callable] = None,
                      on_redo: Optional[Callable] = None) -> None:
        """Set callback functions."""
        self._on_change = on_change
        self._on_undo = on_undo
        self._on_redo = on_redo
    
    def _notify_change(self) -> None:
        """Notify listeners of history change."""
        if self._on_change:
            self._on_change()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get history statistics."""
        return {
            'total_commands': len(self._entries),
            'undo_available': self.undo_count,
            'redo_available': self.redo_count,
            'current_index': self._current_index,
            'is_grouping': self._group_depth > 0,
            'memory_estimate': sum(
                len(str(e.command.serialize())) 
                for e in self._entries
            ),
        }
    
    def __len__(self) -> int:
        return len(self._entries)
    
    def __repr__(self) -> str:
        return f"CommandHistory({len(self._entries)} entries, index={self._current_index})"
