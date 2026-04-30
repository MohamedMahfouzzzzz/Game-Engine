# /**************************************************************************/
# /*  test_signals.py                                                       */
# /**************************************************************************/

"""Unit tests for signals/slots system."""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engine.signals import (
    Signal, SignalManager,
    Slot, CallableSlot, MethodSlot
)
from engine.signals.signal import SignalConnection


class TestSignal(unittest.TestCase):
    """Test Signal class."""
    
    def test_signal_creation(self):
        """Test signal creation."""
        sig = Signal(int, str, name='test_signal')
        self.assertEqual(sig._name, 'test_signal')
        self.assertEqual(sig.connection_count, 0)
    
    def test_connect_and_emit(self):
        """Test connecting and emitting."""
        sig = Signal(int)
        received = []
        
        def handler(value):
            received.append(value)
        
        conn = sig.connect(handler)
        sig.emit(42)
        
        self.assertEqual(received, [42])
        self.assertEqual(sig.connection_count, 1)
    
    def test_disconnect(self):
        """Test disconnecting."""
        sig = Signal()
        received = []
        
        def handler():
            received.append(1)
        
        conn = sig.connect(handler)
        sig.emit()
        self.assertEqual(len(received), 1)
        
        conn.disconnect()
        sig.emit()
        self.assertEqual(len(received), 1)  # Should not increase
    
    def test_one_shot(self):
        """Test one-shot connection."""
        sig = Signal()
        count = [0]
        
        def handler():
            count[0] += 1
        
        sig.connect(handler, one_shot=True)
        sig.emit()
        sig.emit()
        
        self.assertEqual(count[0], 1)
    
    def test_priority(self):
        """Test connection priority."""
        sig = Signal()
        order = []
        
        def low():
            order.append('low')
        
        def high():
            order.append('high')
        
        sig.connect(low, priority=0)
        sig.connect(high, priority=10)
        sig.emit()
        
        self.assertEqual(order, ['high', 'low'])
    
    def test_block_unblock(self):
        """Test blocking connections."""
        sig = Signal()
        count = [0]
        
        def handler():
            count[0] += 1
        
        conn = sig.connect(handler)
        conn.block()
        sig.emit()
        self.assertEqual(count[0], 0)
        
        conn.unblock()
        sig.emit()
        self.assertEqual(count[0], 1)
    
    def test_emit_return_values(self):
        """Test emit returns handler results."""
        sig = Signal(int)
        
        def double(x):
            return x * 2
        
        sig.connect(double)
        results = sig.emit(5)
        
        self.assertEqual(results, [10])
    
    def test_no_connections_emit(self):
        """Test emitting with no connections."""
        sig = Signal(int)
        results = sig.emit(42)
        self.assertEqual(results, [])


class TestSignalManager(unittest.TestCase):
    """Test SignalManager."""
    
    def setUp(self):
        self.manager = SignalManager()
    
    def test_add_signal(self):
        """Test adding global signal."""
        sig = Signal()
        self.manager.add_signal('test', sig)
        
        self.assertIn('test', self.manager.get_signal_names())
    
    def test_connect_and_emit(self):
        """Test connect and emit through manager."""
        self.manager.add_signal('event', Signal(int))
        
        received = []
        def handler(x):
            received.append(x)
        
        self.manager.connect('event', handler)
        self.manager.emit('event', 100)
        
        self.assertEqual(received, [100])
    
    def test_create_group(self):
        """Test creating signal group."""
        group = self.manager.create_group('ui')
        
        group.add_signal('click', Signal())
        self.assertIn('click', group.get_signal_names())
    
    def test_group_connect_emit(self):
        """Test group connect and emit."""
        group = self.manager.create_group('player')
        group.add_signal('health_changed', Signal(int))
        
        received = []
        def handler(hp):
            received.append(hp)
        
        self.manager.connect('player.health_changed', handler)
        self.manager.emit('player.health_changed', 50)
        
        self.assertEqual(received, [50])
    
    def test_disconnect_all(self):
        """Test disconnect all signals."""
        self.manager.add_signal('a', Signal())
        self.manager.add_signal('b', Signal())
        
        count = [0]
        def handler():
            count[0] += 1
        
        self.manager.connect('a', handler)
        self.manager.connect('b', handler)
        
        self.manager.disconnect_all()
        
        self.manager.emit('a')
        self.manager.emit('b')
        
        self.assertEqual(count[0], 0)


class TestSlots(unittest.TestCase):
    """Test Slot classes."""
    
    def test_callable_slot(self):
        """Test CallableSlot."""
        received = []
        
        def func(x):
            received.append(x)
            return x * 2
        
        slot = CallableSlot(func, weak=False)
        result = slot.call(5)
        
        self.assertEqual(result, 10)
        self.assertEqual(received, [5])
    
    def test_callable_slot_is_alive(self):
        """Test CallableSlot is_alive."""
        def func():
            pass
        
        slot = CallableSlot(func, weak=False)
        self.assertTrue(slot.is_alive())
    
    def test_callable_slot_weak(self):
        """Test weak CallableSlot."""
        class TempFunc:
            def __call__(self, x):
                return x + 1
        
        func = TempFunc()
        slot = CallableSlot(func, weak=True)
        
        self.assertTrue(slot.is_alive())
        result = slot.call(5)
        self.assertEqual(result, 6)


if __name__ == '__main__':
    unittest.main()
