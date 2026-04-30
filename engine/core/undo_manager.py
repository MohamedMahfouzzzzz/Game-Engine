# /**************************************************************************/
# /*  undo_manager.py                                                       */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Undo/Redo system for the game engine using Command pattern."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, List, Optional

from engine.core.node import Node, Node2D
from engine.core.scene import Scene

logger = logging.getLogger(__name__)


class Command(ABC):
    """Abstract base class for undoable commands."""

    def __init__(self, description: str = "") -> None:
        self.description = description
        self._executed = False

    @abstractmethod
    def execute(self) -> None:
        """Execute the command."""
        pass

    @abstractmethod
    def undo(self) -> None:
        """Undo the command."""
        pass

    @abstractmethod
    def redo(self) -> None:
        """Redo the command (default is to re-execute)."""
        self.execute()


class PropertyCommand(Command):
    """Command for setting a property on a node."""

    def __init__(
        self,
        node: Node,
        property_name: str,
        new_value: Any,
        description: str = "Change property"
    ) -> None:
        super().__init__(description)
        self.node = node
        self.property_name = property_name
        self.new_value = new_value
        self.old_value: Any = None

    def execute(self) -> None:
        if self.property_name == "name":
            self.old_value = self.node.name
            self.node.name = self.new_value
        else:
            self.old_value = self.node.get_property(self.property_name)
            self.node.set_property(self.property_name, self.new_value)
        self._executed = True

    def undo(self) -> None:
        if self.property_name == "name":
            self.node.name = self.old_value
        else:
            self.node.set_property(self.property_name, self.old_value)

    def redo(self) -> None:
        if self.property_name == "name":
            self.node.name = self.new_value
        else:
            self.node.set_property(self.property_name, self.new_value)


class TransformCommand(Command):
    """Command for changing transform properties of a Node2D."""

    def __init__(
        self,
        node: Node2D,
        new_position: Optional[tuple] = None,
        new_rotation: Optional[float] = None,
        new_scale: Optional[tuple] = None,
        description: str = "Change transform"
    ) -> None:
        super().__init__(description)
        self.node = node
        self.new_position = new_position
        self.new_rotation = new_rotation
        self.new_scale = new_scale
        self.old_position: tuple = node.get_position()
        self.old_rotation: float = node.get_rotation()
        self.old_scale: tuple = node.get_scale()

    def execute(self) -> None:
        if self.new_position is not None:
            self.node.set_position(*self.new_position)
        if self.new_rotation is not None:
            self.node.set_rotation(self.new_rotation)
        if self.new_scale is not None:
            self.node.set_scale(*self.new_scale)
        self._executed = True

    def undo(self) -> None:
        self.node.set_position(*self.old_position)
        self.node.set_rotation(self.old_rotation)
        self.node.set_scale(*self.old_scale)

    def redo(self) -> None:
        self.execute()


class AddNodeCommand(Command):
    """Command for adding a node to the scene."""

    def __init__(
        self,
        scene: Scene,
        node: Node,
        parent: Optional[Node] = None,
        description: str = "Add node"
    ) -> None:
        super().__init__(description)
        self.scene = scene
        self.node = node
        self.parent = parent or scene.root

    def execute(self) -> None:
        self.scene.add_node(self.node, self.parent)
        self._executed = True

    def undo(self) -> None:
        self.scene.remove_node(self.node)

    def redo(self) -> None:
        self.parent.add_child(self.node)
        self.scene._index_node_recursive(self.node)


class RemoveNodeCommand(Command):
    """Command for removing a node from the scene."""

    def __init__(
        self,
        scene: Scene,
        node: Node,
        description: str = "Remove node"
    ) -> None:
        super().__init__(description)
        self.scene = scene
        self.node = node
        self.parent = node.parent
        self.children_snapshot: List[Node] = []

    def execute(self) -> None:
        # Store snapshot of children for restoration
        self.children_snapshot = list(self.node.children)
        self.parent = self.node.parent
        self.scene.remove_node(self.node)
        self._executed = True

    def undo(self) -> None:
        if self.parent:
            self.parent.add_child(self.node)
            self.scene._index_node_recursive(self.node)
            # Restore children relationships
            for child in self.children_snapshot:
                if child not in self.node.children:
                    self.node.add_child(child)

    def redo(self) -> None:
        self.scene.remove_node(self.node)


class ReorderNodeCommand(Command):
    """Command for reordering a node among its siblings."""

    def __init__(
        self,
        node: Node,
        new_index: int,
        description: str = "Reorder node"
    ) -> None:
        super().__init__(description)
        self.node = node
        self.new_index = new_index
        self.parent = node.parent
        self.old_index = -1

    def execute(self) -> None:
        if self.parent:
            self.old_index = self.parent.children.index(self.node)
            self.parent.children.remove(self.node)
            # Clamp index to valid range
            index = max(0, min(self.new_index, len(self.parent.children)))
            self.parent.children.insert(index, self.node)
        self._executed = True

    def undo(self) -> None:
        if self.parent and self.old_index >= 0:
            self.parent.children.remove(self.node)
            self.parent.children.insert(self.old_index, self.node)

    def redo(self) -> None:
        if self.parent:
            self.parent.children.remove(self.node)
            index = max(0, min(self.new_index, len(self.parent.children)))
            self.parent.children.insert(index, self.node)


class UndoManager:
    """Manager for undo/redo operations."""

    def __init__(self, max_history: int = 100) -> None:
        self.max_history = max_history
        self._undo_stack: List[Command] = []
        self._redo_stack: List[Command] = []
        self._on_change_callbacks: List[Callable[[], None]] = []

    def execute(self, command: Command) -> None:
        """Execute a command and add it to the undo stack."""
        command.execute()
        self._undo_stack.append(command)
        # Clear redo stack when new action is performed
        self._redo_stack.clear()
        # Trim undo stack if it exceeds max_history
        if len(self._undo_stack) > self.max_history:
            self._undo_stack.pop(0)
        self._notify_change()

    def undo(self) -> bool:
        """Undo the last command. Returns True if successful."""
        if not self._undo_stack:
            return False
        command = self._undo_stack.pop()
        command.undo()
        self._redo_stack.append(command)
        self._notify_change()
        return True

    def redo(self) -> bool:
        """Redo the last undone command. Returns True if successful."""
        if not self._redo_stack:
            return False
        command = self._redo_stack.pop()
        command.redo()
        self._undo_stack.append(command)
        self._notify_change()
        return True

    def can_undo(self) -> bool:
        """Check if there are commands to undo."""
        return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        """Check if there are commands to redo."""
        return len(self._redo_stack) > 0

    def get_undo_description(self) -> Optional[str]:
        """Get description of the next undo command."""
        if self._undo_stack:
            return self._undo_stack[-1].description
        return None

    def get_redo_description(self) -> Optional[str]:
        """Get description of the next redo command."""
        if self._redo_stack:
            return self._redo_stack[-1].description
        return None

    def clear(self) -> None:
        """Clear all undo/redo history."""
        self._undo_stack.clear()
        self._redo_stack.clear()
        self._notify_change()

    def on_change(self, callback: Callable[[], None]) -> None:
        """Register a callback to be called when undo/redo state changes."""
        self._on_change_callbacks.append(callback)

    def _notify_change(self) -> None:
        """Notify all registered callbacks of state change."""
        for callback in self._on_change_callbacks:
            callback()

    @property
    def undo_count(self) -> int:
        """Number of commands in undo stack."""
        return len(self._undo_stack)

    @property
    def redo_count(self) -> int:
        """Number of commands in redo stack."""
        return len(self._redo_stack)


# Global undo manager instance for the application
global_undo_manager = UndoManager()
