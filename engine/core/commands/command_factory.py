# /**************************************************************************/
# /*  command_factory.py                                                  */
# /**************************************************************************/

"""Factory for creating commands by type.

Allows commands to be created dynamically and serialized/deserialized.
"""

from typing import Dict, Type, Optional, Any
from .command import Command


class CommandFactory:
    """Factory for creating command instances.
    
    Registers command types and creates them by name.
    Useful for:
    - Deserializing command history
    - Scripting/macro recording
    - Remote command execution
    """
    
    _instance: Optional['CommandFactory'] = None
    _command_types: Dict[str, Type[Command]] = {}
    
    @classmethod
    def instance(cls) -> 'CommandFactory':
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def register(self, name: str, command_class: Type[Command]) -> None:
        """Register a command type.
        
        Args:
            name: Unique name for the command type
            command_class: The Command subclass
        """
        self._command_types[name] = command_class
    
    def unregister(self, name: str) -> None:
        """Unregister a command type."""
        if name in self._command_types:
            del self._command_types[name]
    
    def create(self, name: str, **kwargs) -> Optional[Command]:
        """Create a command instance by type name.
        
        Args:
            name: Registered command type name
            **kwargs: Arguments to pass to command constructor
        
        Returns:
            Command instance or None if type not found
        """
        command_class = self._command_types.get(name)
        if command_class is None:
            return None
        
        try:
            return command_class(**kwargs)
        except Exception as e:
            # Log error and return None
            print(f"Failed to create command '{name}': {e}")
            return None
    
    def can_create(self, name: str) -> bool:
        """Check if a command type is registered."""
        return name in self._command_types
    
    def get_registered_types(self) -> list:
        """Get list of registered command type names."""
        return list(self._command_types.keys())
    
    def deserialize_command(self, data: Dict[str, Any]) -> Optional[Command]:
        """Deserialize a command from dictionary.
        
        Args:
            data: Dictionary containing command data
        
        Returns:
            Command instance or None
        """
        command_type = data.get('type')
        if not command_type:
            return None
        
        command_class = self._command_types.get(command_type)
        if command_class is None:
            return None
        
        try:
            return command_class.deserialize(data)
        except (NotImplementedError, Exception):
            # If deserialize not implemented, try to reconstruct
            # from metadata if possible
            return None
    
    def clear(self) -> None:
        """Clear all registered command types."""
        self._command_types.clear()


# Convenience functions
def register_command(name: str, command_class: Type[Command]) -> None:
    """Register a command type with the global factory."""
    CommandFactory.instance().register(name, command_class)


def create_command(name: str, **kwargs) -> Optional[Command]:
    """Create a command using the global factory."""
    return CommandFactory.instance().create(name, **kwargs)
