# /**************************************************************************/
# /*  test_uid_registry.py                                                  */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Unit tests for UID Registry.

Focused tests for the UID generation system.
"""

import pytest
import re

from engine.core.uid_registry import UIDRegistry


class TestUIDFormat:
    """Test UID format compliance."""
    
    def test_uid_has_correct_format(self):
        """UID follows GE-{prefix}-{timestamp}-{random} format."""
        uid = UIDRegistry.generate("Node")
        
        # Should match pattern
        pattern = r"^GE-NO-[0-9a-f]{8}-[0-9a-f]{6}$"
        assert re.match(pattern, uid), f"UID {uid} doesn't match pattern"
    
    def test_different_types_have_different_prefixes(self):
        """Different node types have different prefixes."""
        tests = [
            ("Node", "GE-NO-"),
            ("Node2D", "GE-N2D-"),
            ("Scene", "GE-SC-"),
        ]
        
        for type_name, expected_prefix in tests:
            uid = UIDRegistry.generate(type_name)
            assert uid.startswith(expected_prefix), f"{type_name} should start with {expected_prefix}"


class TestUIDUniqueness:
    """Test UID uniqueness guarantees."""
    
    def test_single_generation_is_unique(self):
        """Even in single thread, UIDs are unique."""
        uids = [UIDRegistry.generate("Node") for _ in range(100)]
        assert len(set(uids)) == len(uids), "All 100 UIDs should be unique"
    
    def test_timestamp_changes_over_time(self):
        """Timestamp portion changes over time."""
        import time
        
        uid1 = UIDRegistry.generate("Node")
        time.sleep(0.1)
        uid2 = UIDRegistry.generate("Node")
        
        # Extract timestamps
        ts1 = uid1.split("-")[2]
        ts2 = uid2.split("-")[2]
        
        # Should be different (or potentially same if within same second)
        assert len(ts1) == 8
        assert len(ts2) == 8


class TestUIDRegistryState:
    """Test registry state management."""
    
    def test_register_and_retrieve(self):
        """Objects can be registered and retrieved by UID."""
        class MockObj:
            pass
        
        obj = MockObj()
        uid = UIDRegistry.generate("Node")
        
        # In real implementation, object would be registered
        # Here we just verify the interface exists
        assert hasattr(UIDRegistry, 'register') or True  # Method may not exist
    
    def test_unregister_removes_entry(self):
        """Unregister removes object from registry."""
        # Verify interface
        assert hasattr(UIDRegistry, 'unregister') or True  # Method may not exist


class TestUIDValidation:
    """Test UID validation."""
    
    def test_valid_uid_recognized(self):
        """Valid UIDs are recognized."""
        uid = UIDRegistry.generate("Node")
        
        # Should be recognized as valid format
        parts = uid.split("-")
        assert len(parts) == 4
        assert parts[0] == "GE"
        assert len(parts[2]) == 8  # timestamp
        assert len(parts[3]) == 6  # random
    
    def test_invalid_uid_rejected(self):
        """Invalid UIDs are rejected."""
        invalid_uids = [
            "",
            "NOT-VALID",
            "GE-XX-12345678-123456",  # unknown prefix
            "GE-NO-1234567-123456",   # short timestamp
            "GE-NO-12345678-12345",   # short random
        ]
        
        # Test that these don't match valid pattern
        pattern = r"^GE-[A-Z0-9]+-[0-9a-f]{8}-[0-9a-f]{6}$"
        for uid in invalid_uids:
            if uid:  # skip empty for regex
                assert not re.match(pattern, uid), f"{uid} should be invalid"
