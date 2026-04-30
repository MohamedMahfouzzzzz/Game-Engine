# /**************************************************************************/
# /*  node_factory.py                                                       */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Node Factory - Factory Pattern for node creation.

Follows Open/Closed Principle: New node types can be added without
modifying existing code.
"""

from typing import Dict, Type, Optional, Any
from engine.core.node_base import Node

import logging


logger = logging.getLogger(__name__)



class NodeFactory:
    """Factory for creating nodes by type name.
    
    Example:
        >>> from engine.core.nodes import Node2D, Sprite
        >>> NodeFactory.register("Node2D", Node2D)
        >>> NodeFactory.register("Sprite", Sprite)
        >>> 
        >>> node = NodeFactory.create("Node2D", name="Player")
        >>> sprite = NodeFactory.create("Sprite", name="Hero", texture="hero.png")
    """
    
    _registry: Dict[str, Type[Node]] = {}
    _aliases: Dict[str, str] = {}
    
    @classmethod
    def register(cls, node_type: str, node_class: Type[Node], aliases: Optional[list] = None) -> None:
        """Register a node type with the factory.
        
        Args:
            node_type: Primary type name (e.g., "Node2D")
            node_class: The node class to instantiate
            aliases: Optional list of alternative names (e.g., ["node_2d", "Node2d"])
        """
        cls._registry[node_type] = node_class
        
        if aliases:
            for alias in aliases:
                cls._aliases[alias] = node_type
    
    @classmethod
    def create(cls, node_type: str, **kwargs) -> Node:
        """Create a node instance by type.
        
        Args:
            node_type: Type name or alias
            **kwargs: Constructor arguments
            
        Returns:
            Instantiated node
            
        Raises:
            ValueError: If node type is not registered
        """
        # Resolve alias
        if node_type in cls._aliases:
            node_type = cls._aliases[node_type]
        
        if node_type not in cls._registry:
            raise ValueError(
                f"Unknown node type: {node_type}. "
                f"Available: {', '.join(cls.available_types())}"
            )
        
        node_class = cls._registry[node_type]
        return node_class(**kwargs)
    
    @classmethod
    def available_types(cls) -> list[str]:
        """Get list of available node types."""
        return list(cls._registry.keys())
    
    @classmethod
    def is_registered(cls, node_type: str) -> bool:
        """Check if a node type is registered."""
        return node_type in cls._registry or node_type in cls._aliases
    
    @classmethod
    def unregister(cls, node_type: str) -> None:
        """Unregister a node type."""
        if node_type in cls._registry:
            del cls._registry[node_type]
        
        # Clean up aliases
        aliases_to_remove = [k for k, v in cls._aliases.items() if v == node_type]
        for alias in aliases_to_remove:
            del cls._aliases[alias]
    
    @classmethod
    def clear(cls) -> None:
        """Clear all registrations."""
        cls._registry.clear()
        cls._aliases.clear()


class NodeRegistrationError(Exception):
    """Exception raised for node registration errors."""
    pass


# Convenience decorator for auto-registration
def register_node(node_type: str, aliases: Optional[list] = None):
    """Decorator to auto-register a node class.
    
    Example:
        @register_node("Sprite", aliases=["sprite", "SPRITE"])
        class Sprite(Node2D):
            pass
    """
    def decorator(cls: Type[Node]) -> Type[Node]:
        NodeFactory.register(node_type, cls, aliases)
        return cls
    return decorator
