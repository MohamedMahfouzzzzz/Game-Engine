# /**************************************************************************/
# /*  command.py                                                            */
# /**************************************************************************/

"""Base Command class for Undo/Redo system.

Implements the Command Pattern for professional undo/redo functionality.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from enum import Enum, auto
from dataclasses import dataclass
from datetime import datetime
import uuid


class CommandResult(Enum):
    """Result of command execution."""
    SUCCESS = auto()
    FAILED = auto()
    CANCELLED = auto()
    NO_OP = auto()


@dataclass
class CommandContext:
    """Context passed to commands during execution."""
    document_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class Command(ABC):
    """Base class for all undoable commands.
    
    The Command Pattern encapsulates operations as objects,
    allowing them to be undone, redone, and logged.
    
    Example:
        class DrawPixelCommand(Command):
            def __init__(self, layer, x, y, old_color, new_color):
                super().__init__("Draw Pixel")
                self.layer = layer
                self.x = x
                self.y = y
                self.old_color = old_color
                self.new_color = new_color
            
            def execute(self) -> CommandResult:
                self.layer.set_pixel(self.x, self.y, self.new_color)
                return CommandResult.SUCCESS
            
            def undo(self) -> CommandResult:
                self.layer.set_pixel(self.x, self.y, self.old_color)
                return CommandResult.SUCCESS
    """
    
    def __init__(self, name: str, description: str = ""):
        self._id = uuid.uuid4()
        self.name = name
        self.description = description or name
        self._context: Optional[CommandContext] = None
        self._executed = False
        self._metadata: Dict[str, Any] = {}
        self._timestamp: Optional[datetime] = None
    
    @property
    def id(self) -> uuid.UUID:
        """Get unique command ID."""
        return self._id
    
    @property
    def is_executed(self) -> bool:
        """Check if command has been executed."""
        return self._executed
    
    def set_context(self, context: CommandContext) -> None:
        """Set execution context."""
        self._context = context
    
    @abstractmethod
    def execute(self) -> CommandResult:
        """Execute the command.
        
        Returns:
            CommandResult indicating success or failure.
        """
        pass
    
    @abstractmethod
    def undo(self) -> CommandResult:
        """Undo the command.
        
        Returns:
            CommandResult indicating success or failure.
        """
        pass
    
    def redo(self) -> CommandResult:
        """Redo the command (default is just execute)."""
        return self.execute()
    
    def can_execute(self) -> bool:
        """Check if command can be executed (pre-conditions)."""
        return True
    
    def can_undo(self) -> bool:
        """Check if command can be undone."""
        return self._executed
    
    def merge_with(self, other: 'Command') -> Optional['Command']:
        """Try to merge with another command.
        
        If commands can be merged (e.g., consecutive brush strokes),
        return a new merged command. Otherwise return None.
        
        This helps reduce history size for many small operations.
        """
        return None
    
    def get_affected_objects(self) -> list:
        """Get list of objects that will be modified.
        
        Used for UI updates and dependency tracking.
        """
        return []
    
    def serialize(self) -> Dict[str, Any]:
        """Serialize command to dictionary.
        
        For saving command history or remote execution.
        """
        return {
            'id': str(self._id),
            'name': self.name,
            'description': self.description,
            'type': self.__class__.__name__,
            'timestamp': self._timestamp.isoformat() if self._timestamp else None,
            'metadata': self._metadata,
        }
    
    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'Command':
        """Deserialize command from dictionary."""
        raise NotImplementedError("Subclasses must implement deserialize")
    
    def _mark_executed(self) -> None:
        """Mark command as executed."""
        self._executed = True
        self._timestamp = datetime.now()
    
    def _mark_undone(self) -> None:
        """Mark command as undone."""
        self._executed = False
    
    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata key-value pair."""
        self._metadata[key] = value
    
    def get_metadata(self, key: str) -> Optional[Any]:
        """Get metadata value."""
        return self._metadata.get(key)
    
    def __repr__(self) -> str:
        status = "executed" if self._executed else "pending"
        return f"{self.__class__.__name__}({self.name}, {status})"


class NoOpCommand(Command):
    """A command that does nothing (for testing)."""
    
    def __init__(self, name: str = "No Operation"):
        super().__init__(name)
    
    def execute(self) -> CommandResult:
        self._mark_executed()
        return CommandResult.NO_OP
    
    def undo(self) -> CommandResult:
        self._mark_undone()
        return CommandResult.NO_OP


class CompoundCommand(Command):
    """A command composed of multiple sub-commands.
    
    Executes/undoes all sub-commands atomically.
    """
    
    def __init__(self, name: str, commands: list = None):
        super().__init__(name)
        self._commands: list = commands or []
    
    def add_command(self, command: Command) -> None:
        """Add a sub-command."""
        self._commands.append(command)
    
    def execute(self) -> CommandResult:
        """Execute all sub-commands."""
        for i, cmd in enumerate(self._commands):
            result = cmd.execute()
            if result == CommandResult.FAILED:
                # Rollback already executed commands
                for j in range(i - 1, -1, -1):
                    self._commands[j].undo()
                return CommandResult.FAILED
        
        self._mark_executed()
        return CommandResult.SUCCESS
    
    def undo(self) -> CommandResult:
        """Undo all sub-commands in reverse order."""
        for cmd in reversed(self._commands):
            result = cmd.undo()
            if result == CommandResult.FAILED:
                return CommandResult.FAILED
        
        self._mark_undone()
        return CommandResult.SUCCESS
    
    def __len__(self) -> int:
        return len(self._commands)
