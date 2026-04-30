# /**************************************************************************/
# /*  test_commands.py                                                      */
# /**************************************************************************/

"""Unit tests for command system."""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engine.core.commands import (
    Command, CommandResult, CommandHistory,
    Transaction
)


class SimpleCommand(Command):
    """Test command that toggles a flag."""
    
    def __init__(self):
        super().__init__('SimpleCommand')
        self.executed = False
    
    def execute(self):
        self.executed = True
        self._mark_executed()
        return CommandResult.SUCCESS
    
    def undo(self):
        self.executed = False
        self._mark_undone()
        return CommandResult.SUCCESS


class FailingCommand(Command):
    """Test command that always fails."""
    
    def __init__(self):
        super().__init__('FailingCommand')
    
    def execute(self):
        return CommandResult.FAILED
    
    def undo(self):
        return CommandResult.SUCCESS


class TestCommand(unittest.TestCase):
    """Test Command base class."""
    
    def test_command_initial_state(self):
        """Test initial command state."""
        cmd = SimpleCommand()
        self.assertEqual(cmd.name, 'SimpleCommand')
        self.assertFalse(cmd.is_executed)
        self.assertFalse(cmd.is_undone)
    
    def test_command_execute(self):
        """Test command execution."""
        cmd = SimpleCommand()
        result = cmd.execute()
        
        self.assertEqual(result, CommandResult.SUCCESS)
        self.assertTrue(cmd.executed)
        self.assertTrue(cmd.is_executed)
    
    def test_command_undo(self):
        """Test command undo."""
        cmd = SimpleCommand()
        cmd.execute()
        result = cmd.undo()
        
        self.assertEqual(result, CommandResult.SUCCESS)
        self.assertFalse(cmd.executed)
        self.assertTrue(cmd.is_undone)


class TestCommandHistory(unittest.TestCase):
    """Test CommandHistory."""
    
    def setUp(self):
        self.history = CommandHistory()
    
    def test_initial_state(self):
        """Test initial history state."""
        self.assertFalse(self.history.can_undo)
        self.assertFalse(self.history.can_redo)
        self.assertEqual(self.history.undo_count, 0)
    
    def test_execute_adds_to_history(self):
        """Test executing adds command to history."""
        cmd = SimpleCommand()
        self.history.execute(cmd)
        
        self.assertTrue(cmd.is_executed)
        self.assertTrue(self.history.can_undo)
    
    def test_undo(self):
        """Test undo operation."""
        cmd = SimpleCommand()
        self.history.execute(cmd)
        self.assertTrue(cmd.executed)
        
        result = self.history.undo()
        self.assertTrue(result)
        self.assertFalse(cmd.executed)
        self.assertTrue(self.history.can_redo)
    
    def test_redo(self):
        """Test redo operation."""
        cmd = SimpleCommand()
        self.history.execute(cmd)
        self.history.undo()
        self.assertFalse(cmd.executed)
        
        result = self.history.redo()
        self.assertTrue(result)
        self.assertTrue(cmd.executed)
    
    def test_undo_limit(self):
        """Test undo limit."""
        self.history.set_limit(3)
        
        # Execute 5 commands
        for i in range(5):
            cmd = SimpleCommand()
            self.history.execute(cmd)
        
        # Should only have 3 in history
        self.assertEqual(self.history.undo_count, 3)
    
    def test_clear(self):
        """Test clearing history."""
        cmd = SimpleCommand()
        self.history.execute(cmd)
        
        self.history.clear()
        
        self.assertFalse(self.history.can_undo)
        self.assertEqual(self.history.undo_count, 0)
    
    def test_begin_end_undo_group(self):
        """Test undo grouping."""
        self.history.begin_undo_group('Test Group')
        
        cmd1 = SimpleCommand()
        cmd2 = SimpleCommand()
        self.history.execute(cmd1)
        self.history.execute(cmd2)
        
        self.history.end_undo_group()
        
        # Should be one undoable group
        self.assertEqual(self.history.undo_count, 1)


class TestTransaction(unittest.TestCase):
    """Test Transaction context manager."""
    
    def setUp(self):
        self.history = CommandHistory()
    
    def test_transaction_execute(self):
        """Test transaction executes commands."""
        with Transaction(self.history, 'Test Transaction'):
            cmd = SimpleCommand()
            self.history.execute(cmd)
        
        self.assertTrue(cmd.is_executed)
    
    def test_transaction_rollback_on_exception(self):
        """Test transaction rolls back on exception."""
        cmd = SimpleCommand()
        
        try:
            with Transaction(self.history, 'Test Transaction'):
                self.history.execute(cmd)
                raise RuntimeError('Test error')
        except RuntimeError:
            pass
        
        # Command should be undone
        self.assertFalse(cmd.executed)


if __name__ == '__main__':
    unittest.main()
