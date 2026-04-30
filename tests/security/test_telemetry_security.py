# /**************************************************************************/
# /*  test_telemetry_security.py                                            */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Security tests for secure telemetry uploader.

Tests rate limiting, circuit breaker, PII sanitization,
and secure transmission.
"""

import asyncio
import json
import tempfile
from pathlib import Path

import pytest

from engine.core.errors import SecurityError
from engine.telemetry.uploader_secure import (
    SecureTelemetryUploader,
    RateLimiter,
    CircuitBreaker,
    CircuitState
)
from engine.config.secure_config import TelemetryConfig


class TestRateLimiter:
    """Test rate limiting functionality."""
    
    @pytest.mark.asyncio
    async def test_acquires_token_when_available(self):
        """Acquire token when within rate limit."""
        limiter = RateLimiter(rate=60, burst=10)
        
        # First request should succeed
        result = await limiter.acquire()
        assert result is True
    
    @pytest.mark.asyncio
    async def test_rejects_when_rate_exceeded(self):
        """Reject when rate limit exceeded."""
        limiter = RateLimiter(rate=60, burst=1)
        
        # First request succeeds
        assert await limiter.acquire() is True
        
        # Second request should fail (burst exhausted)
        result = await limiter.acquire()
        assert result is False
    
    @pytest.mark.asyncio
    async def test_replenishes_over_time(self):
        """Tokens replenish over time."""
        limiter = RateLimiter(rate=6000, burst=1)  # 100 tokens/sec
        
        # Use token
        await limiter.acquire()
        
        # Should fail immediately
        assert await limiter.acquire() is False
        
        # Wait for token
        await asyncio.sleep(0.02)  # 20ms should replenish
        
        # Should succeed now
        assert await limiter.acquire() is True
    
    @pytest.mark.asyncio
    async def test_calculates_wait_time(self):
        """Calculate time until next token available."""
        limiter = RateLimiter(rate=60, burst=1)
        
        await limiter.acquire()  # Use token
        
        wait_time = await limiter.wait_time()
        assert wait_time > 0  # Should need to wait


class TestCircuitBreaker:
    """Test circuit breaker functionality."""
    
    @pytest.mark.asyncio
    async def test_starts_closed(self):
        """Circuit starts in closed state."""
        breaker = CircuitBreaker()
        assert breaker.state == CircuitState.CLOSED
    
    @pytest.mark.asyncio
    async def test_opens_after_failures(self):
        """Opens after threshold failures."""
        breaker = CircuitBreaker(failure_threshold=3)
        
        # Record failures
        await breaker.record_failure()
        await breaker.record_failure()
        await breaker.record_failure()
        
        assert breaker.state == CircuitState.OPEN
    
    @pytest.mark.asyncio
    async def test_blocks_execution_when_open(self):
        """Block execution when circuit is open."""
        breaker = CircuitBreaker(failure_threshold=1)
        await breaker.record_failure()
        
        assert await breaker.can_execute() is False
    
    @pytest.mark.asyncio
    async def test_half_open_after_timeout(self):
        """Half-open after recovery timeout."""
        breaker = CircuitBreaker(
            failure_threshold=1,
            recovery_timeout=0.1  # Fast for testing
        )
        await breaker.record_failure()
        assert breaker.state == CircuitState.OPEN
        
        # Wait for recovery
        await asyncio.sleep(0.15)
        
        # Should be half-open now
        assert await breaker.can_execute() is True
        assert breaker.state == CircuitState.HALF_OPEN
    
    @pytest.mark.asyncio
    async def test_closes_on_success(self):
        """Close circuit on success from half-open."""
        breaker = CircuitBreaker(
            failure_threshold=1,
            recovery_timeout=0.1
        )
        
        await breaker.record_failure()
        await asyncio.sleep(0.15)
        
        # Enter half-open state
        assert await breaker.can_execute() is True
        
        # Now record success to close
        await breaker.record_success()
        
        assert breaker.state == CircuitState.CLOSED
    
    @pytest.mark.asyncio
    async def test_reopens_on_failure_from_half_open(self):
        """Reopen on failure from half-open."""
        breaker = CircuitBreaker(
            failure_threshold=1,
            recovery_timeout=0.1
        )
        
        await breaker.record_failure()
        await asyncio.sleep(0.15)
        
        # Half-open, but fail again
        await breaker.record_failure()
        
        assert breaker.state == CircuitState.OPEN


class TestPIISanitization:
    """Test PII removal from telemetry data."""
    
    def test_removes_email(self):
        """Remove email addresses."""
        uploader = SecureTelemetryUploader()
        
        data = {
            "user": "player1",
            "email": "user@example.com",  # Should be removed
            "score": 100
        }
        
        sanitized = uploader._sanitize_data(data)
        assert "email" not in sanitized
        assert sanitized["score"] == 100
    
    def test_removes_username(self):
        """Remove usernames."""
        uploader = SecureTelemetryUploader()
        
        data = {
            "username": "john_doe",  # Should be removed
            "action": "jump"
        }
        
        sanitized = uploader._sanitize_data(data)
        assert "username" not in sanitized
    
    def test_removes_ip_address(self):
        """Remove IP addresses."""
        uploader = SecureTelemetryUploader()
        
        data = {
            "ip_address": "192.168.1.1",  # Should be removed
            "event": "login"
        }
        
        sanitized = uploader._sanitize_data(data)
        assert "ip_address" not in sanitized
    
    def test_preserves_safe_data(self):
        """Keep non-PII data intact."""
        uploader = SecureTelemetryUploader()
        
        data = {
            "level": 5,
            "score": 1000,
            "duration": 120.5
        }
        
        sanitized = uploader._sanitize_data(data)
        assert sanitized == data
    
    def test_handles_nested_structures(self):
        """Sanitize nested dictionaries and lists."""
        uploader = SecureTelemetryUploader()
        
        data = {
            "player": {
                "email": "player@example.com",  # Should be removed
                "level": 10
            },
            "events": [
                {"action": "jump", "username": "player1"},  # username removed
                {"action": "shoot"}
            ]
        }
        
        sanitized = uploader._sanitize_data(data)
        assert "email" not in sanitized["player"]
        assert "username" not in sanitized["events"][0]
        assert sanitized["player"]["level"] == 10
    
    def test_truncates_long_strings(self):
        """Truncate strings over 1000 characters."""
        uploader = SecureTelemetryUploader()
        
        data = {
            "description": "A" * 2000  # Very long string
        }
        
        sanitized = uploader._sanitize_data(data)
        assert len(sanitized["description"]) <= 1000


class TestQueueManagement:
    """Test secure queue management."""
    
    @pytest.mark.asyncio
    async def test_enforces_queue_limit(self):
        """Queue size limit enforced with FIFO eviction."""
        config = TelemetryConfig(max_queue_size=2)
        uploader = SecureTelemetryUploader(config)
        
        with tempfile.TemporaryDirectory() as tmp:
            # Create test files
            for i in range(3):
                path = Path(tmp) / f"session{i}.json"
                with open(path, 'w') as f:
                    json.dump({"id": i}, f)
                
                await uploader.queue_session(path)
            
            # Queue should only contain 2 items
            assert uploader.pending_count == 2
    
    @pytest.mark.asyncio
    async def test_rejects_nonexistent_files(self):
        """Reject queuing non-existent files."""
        config = TelemetryConfig()
        uploader = SecureTelemetryUploader(config)
        
        result = await uploader.queue_session(Path("/nonexistent/file.json"))
        assert result is False
    
    @pytest.mark.asyncio
    async def test_rejects_invalid_json(self):
        """Reject files with invalid JSON."""
        config = TelemetryConfig()
        uploader = SecureTelemetryUploader(config)
        
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "invalid.json"
            with open(path, 'w') as f:
                f.write("not valid json")
            
            result = await uploader.queue_session(path)
            assert result is False
    
    @pytest.mark.asyncio
    async def test_rejects_oversized_files(self):
        """Reject files over 10MB limit."""
        config = TelemetryConfig()
        uploader = SecureTelemetryUploader(config)
        
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "large.json"
            # Write just under 10MB of data
            with open(path, 'w') as f:
                f.write('"' + "x" * (11 * 1024 * 1024) + '"')
            
            result = await uploader.queue_session(path)
            assert result is False


class TestHTTPSRequirement:
    """Test HTTPS enforcement."""
    
    @pytest.mark.asyncio
    async def test_blocks_http_endpoints(self):
        """HTTP endpoints are rejected."""
        config = TelemetryConfig(endpoint="http://example.com/telemetry")
        uploader = SecureTelemetryUploader(config)
        
        # Add dummy session
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "session.json"
            with open(path, 'w') as f:
                json.dump({"event": "test"}, f)
            await uploader.queue_session(path)
            
            # Try to upload - should fail due to HTTP
            with pytest.raises(SecurityError) as exc:
                await uploader._upload_batch_data([])
            
            assert "https" in str(exc.value).lower()


class TestDuplicatePrevention:
    """Test duplicate detection."""
    
    @pytest.mark.asyncio
    async def test_rejects_duplicate_items(self):
        """Same content shouldn't be queued twice."""
        config = TelemetryConfig(max_queue_size=10)
        uploader = SecureTelemetryUploader(config)
        
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "session.json"
            with open(path, 'w') as f:
                json.dump({"event": "test", "data": "same"}, f)
            
            # Queue same file twice
            result1 = await uploader.queue_session(path)
            result2 = await uploader.queue_session(path)
            
            # Both succeed but only one item in queue
            assert result1 is True
            assert result2 is True
            assert uploader.pending_count == 1


class TestConfigValidation:
    """Test configuration validation."""
    
    def test_validates_batch_size_range(self):
        """Batch size must be 1-1000."""
        with pytest.raises(ValueError):
            TelemetryConfig(batch_size=0)
        
        with pytest.raises(ValueError):
            TelemetryConfig(batch_size=1001)
        
        # Valid range should work
        config = TelemetryConfig(batch_size=50)
        assert config.batch_size == 50
    
    def test_validates_queue_size_range(self):
        """Queue size must be 1-10000."""
        with pytest.raises(ValueError):
            TelemetryConfig(max_queue_size=0)
        
        with pytest.raises(ValueError):
            TelemetryConfig(max_queue_size=10001)
        
        # Valid range should work
        config = TelemetryConfig(max_queue_size=100)
        assert config.max_queue_size == 100
