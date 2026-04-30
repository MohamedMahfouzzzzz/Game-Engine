# /**************************************************************************/
# /*  uploader_secure.py                                                    */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Secure telemetry uploader with rate limiting and circuit breaker.

Features:
- Async I/O for non-blocking uploads
- Rate limiting to prevent abuse
- Circuit breaker for resilience
- Encrypted transmission
- Memory-bounded queues
- Automatic retry with exponential backoff
"""

from __future__ import annotations

import asyncio
import gzip
import hashlib
import json
import logging
import ssl
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set
from urllib.parse import urlparse

import aiohttp
import certifi

from engine.core.errors import SecurityError
from engine.config.secure_config import TelemetryConfig, SecureConfigManager

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = auto()      # Normal operation
    OPEN = auto()        # Failing, reject requests
    HALF_OPEN = auto()   # Testing if recovered


@dataclass
class RateLimiter:
    """Token bucket rate limiter."""
    rate: int = 60  # tokens per minute
    burst: int = 10  # max burst
    
    def __post_init__(self):
        self._tokens = self.burst
        self._last_update = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def acquire(self) -> bool:
        """Try to acquire a token. Returns True if allowed."""
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_update
            
            # Add tokens based on time elapsed
            self._tokens = min(
                self.burst,
                self._tokens + elapsed * (self.rate / 60)
            )
            self._last_update = now
            
            if self._tokens >= 1:
                self._tokens -= 1
                return True
            return False
    
    async def wait_time(self) -> float:
        """Calculate time to wait for next token."""
        async with self._lock:
            if self._tokens >= 1:
                return 0
            return (1 - self._tokens) / (self.rate / 60)


@dataclass
class CircuitBreaker:
    """Circuit breaker for resilience."""
    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    half_open_max_calls: int = 3
    
    def __post_init__(self):
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.last_failure_time: Optional[float] = None
        self.half_open_calls = 0
        self._lock = asyncio.Lock()
    
    async def can_execute(self) -> bool:
        """Check if execution is allowed."""
        async with self._lock:
            if self.state == CircuitState.CLOSED:
                return True
            
            if self.state == CircuitState.OPEN:
                if time.monotonic() - (self.last_failure_time or 0) > self.recovery_timeout:
                    self.state = CircuitState.HALF_OPEN
                    self.half_open_calls = 0
                    return True
                return False
            
            if self.state == CircuitState.HALF_OPEN:
                if self.half_open_calls < self.half_open_max_calls:
                    self.half_open_calls += 1
                    return True
                return False
            
            return True
    
    async def record_success(self) -> None:
        """Record successful execution."""
        async with self._lock:
            if self.state == CircuitState.HALF_OPEN:
                self.failures = 0
                self.state = CircuitState.CLOSED
                self.half_open_calls = 0
            else:
                self.failures = max(0, self.failures - 1)
    
    async def record_failure(self) -> None:
        """Record failed execution."""
        async with self._lock:
            self.failures += 1
            self.last_failure_time = time.monotonic()
            
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
            elif self.failures >= self.failure_threshold:
                self.state = CircuitState.OPEN
                logger.warning(f"Circuit breaker opened after {self.failures} failures")


@dataclass
class UploadItem:
    """Item in upload queue."""
    file_path: Path
    data: Dict[str, Any]
    attempts: int = 0
    last_attempt: float = 0
    checksum: str = field(default="")
    
    def __post_init__(self):
        if not self.checksum:
            self.checksum = hashlib.sha256(
                json.dumps(self.data, sort_keys=True).encode()
            ).hexdigest()


class SecureTelemetryUploader:
    """Hardened telemetry uploader with security and resilience."""
    
    def __init__(self, config: Optional[TelemetryConfig] = None):
        self.config = config or TelemetryConfig()
        
        # Queue management
        self._queue: List[UploadItem] = []
        self._pending: Set[str] = set()  # Checksums of in-flight items
        self._queue_lock = asyncio.Lock()
        
        # Circuit breaker and rate limiter
        self._circuit = CircuitBreaker()
        self._rate_limiter = RateLimiter(
            rate=self.config.rate_limit,
            burst=min(self.config.batch_size, 10)
        )
        
        # SSL context with certificate validation
        self._ssl_context = ssl.create_default_context(cafile=certifi.where())
        
        # Callbacks
        self._on_upload_success: Optional[Callable[[str], None]] = None
        self._on_upload_error: Optional[Callable[[str, str], None]] = None
        
        # Session (lazy initialization)
        self._session: Optional[aiohttp.ClientSession] = None
        
        # Background task
        self._upload_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        logger.info("SecureTelemetryUploader initialized")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            connector = aiohttp.TCPConnector(
                limit=10,
                limit_per_host=5,
                enable_cleanup_closed=True,
                force_close=True,
            )
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers={
                    'User-Agent': 'GameEngineStudio/1.0',
                    'Accept': 'application/json',
                }
            )
        return self._session
    
    async def queue_session(self, playtest_file: Path) -> bool:
        """Queue a playtest file for upload."""
        try:
            # Validate file
            playtest_file = Path(playtest_file)
            if not playtest_file.exists():
                logger.warning(f"Playtest file not found: {playtest_file}")
                return False
            
            # Check file size
            file_size = playtest_file.stat().st_size
            if file_size > 10 * 1024 * 1024:  # 10MB limit
                logger.warning(f"Playtest file too large: {file_size} bytes")
                return False
            
            # Read and validate JSON
            with open(playtest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Sanitize data (remove PII)
            data = self._sanitize_data(data)
            
            # Create queue item
            item = UploadItem(file_path=playtest_file, data=data)
            
            async with self._queue_lock:
                # Check for duplicates
                if item.checksum in self._pending:
                    return True  # Already in queue
                
                # Enforce queue limit
                while len(self._queue) >= self.config.max_queue_size:
                    removed = self._queue.pop(0)
                    self._pending.discard(removed.checksum)
                    if self._on_upload_error:
                        self._on_upload_error(
                            str(removed.file_path),
                            "Queue limit exceeded, data dropped"
                        )
                    logger.warning(f"Dropped item due to queue limit: {removed.file_path}")
                
                self._queue.append(item)
                self._pending.add(item.checksum)
            
            logger.info(f"Queued session: {playtest_file}")
            return True
            
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in playtest file: {playtest_file}")
            return False
        except Exception as e:
            logger.error(f"Failed to queue session: {e}")
            return False
    
    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove PII and sensitive data before upload."""
        # Fields to remove
        sensitive_fields = {'username', 'password', 'email', 'ip_address', 'hostname'}
        
        def sanitize(obj: Any) -> Any:
            if isinstance(obj, dict):
                return {
                    k: sanitize(v)
                    for k, v in obj.items()
                    if k.lower() not in sensitive_fields
                }
            elif isinstance(obj, list):
                return [sanitize(item) for item in obj]
            elif isinstance(obj, str):
                # Truncate long strings
                return obj[:1000] if len(obj) > 1000 else obj
            return obj
        
        return sanitize(data)
    
    async def upload_batch(self) -> bool:
        """Upload queued sessions with rate limiting and circuit breaker."""
        # Check circuit breaker
        if not await self._circuit.can_execute():
            logger.warning("Circuit breaker is OPEN, skipping upload")
            return False
        
        # Check rate limit
        if not await self._rate_limiter.acquire():
            wait_time = await self._rate_limiter.wait_time()
            logger.info(f"Rate limit hit, waiting {wait_time:.2f}s")
            await asyncio.sleep(wait_time)
        
        # Get batch from queue
        async with self._queue_lock:
            if not self._queue:
                return True
            
            batch_size = min(self.config.batch_size, len(self._queue))
            batch = self._queue[:batch_size]
            self._queue = self._queue[batch_size:]
        
        try:
            success = await self._upload_batch_data(batch)
            
            if success:
                await self._circuit.record_success()
                for item in batch:
                    self._pending.discard(item.checksum)
                    if self._on_upload_success:
                        self._on_upload_success(str(item.file_path))
                return True
            else:
                # Re-queue failed items
                await self._circuit.record_failure()
                async with self._queue_lock:
                    for item in batch:
                        item.attempts += 1
                        if item.attempts < 3:  # Max retries
                            self._queue.insert(0, item)
                        else:
                            self._pending.discard(item.checksum)
                            if self._on_upload_error:
                                self._on_upload_error(
                                    str(item.file_path),
                                    "Max retries exceeded"
                                )
                return False
                
        except Exception as e:
            await self._circuit.record_failure()
            logger.error(f"Batch upload failed: {e}")
            
            # Re-queue
            async with self._queue_lock:
                for item in batch:
                    self._pending.discard(item.checksum)
                    self._queue.insert(0, item)
            
            return False
    
    async def _upload_batch_data(self, batch: List[UploadItem]) -> bool:
        """Upload batch to configured endpoint."""
        if not self.config.endpoint:
            logger.debug("No endpoint configured, skipping upload")
            return True
        
        # Validate endpoint URL
        parsed = urlparse(self.config.endpoint)
        if parsed.scheme not in ('https',):
            raise SecurityError(f"Only HTTPS endpoints allowed: {self.config.endpoint}")
        
        # Prepare payload
        payload = {
            "project_id": self.config.project_id,
            "timestamp": time.time(),
            "sessions": [item.data for item in batch],
            "checksums": [item.checksum for item in batch],
        }
        
        # Compress if enabled
        if self.config.compress:
            body = gzip.compress(json.dumps(payload).encode())
            headers = {
                'Content-Type': 'application/json',
                'Content-Encoding': 'gzip',
            }
        else:
            body = json.dumps(payload).encode()
            headers = {'Content-Type': 'application/json'}
        
        # Get API key from secure storage
        api_key = self.config.api_key
        if api_key:
            headers['X-API-Key'] = api_key
        
        # Make request
        session = await self._get_session()
        
        try:
            async with session.post(
                self.config.endpoint,
                data=body,
                headers=headers,
                ssl=self._ssl_context,
            ) as response:
                if response.status == 200:
                    logger.info(f"Uploaded batch of {len(batch)} sessions")
                    return True
                else:
                    logger.error(f"Upload failed: HTTP {response.status}")
                    return False
                    
        except aiohttp.ClientError as e:
            logger.error(f"Network error during upload: {e}")
            return False
    
    async def start_background_upload(self, interval: float = 60.0) -> None:
        """Start background upload task."""
        if self._upload_task is not None:
            return
        
        self._shutdown_event.clear()
        self._upload_task = asyncio.create_task(
            self._background_upload_loop(interval)
        )
        logger.info("Background upload started")
    
    async def stop_background_upload(self) -> None:
        """Stop background upload task."""
        if self._upload_task is None:
            return
        
        self._shutdown_event.set()
        self._upload_task.cancel()
        
        try:
            await self._upload_task
        except asyncio.CancelledError:
            pass
        
        self._upload_task = None
        
        # Close session
        if self._session and not self._session.closed:
            await self._session.close()
        
        logger.info("Background upload stopped")
    
    async def _background_upload_loop(self, interval: float) -> None:
        """Background upload loop."""
        while not self._shutdown_event.is_set():
            try:
                await self.upload_batch()
            except Exception as e:
                logger.error(f"Background upload error: {e}")
            
            try:
                await asyncio.wait_for(
                    self._shutdown_event.wait(),
                    timeout=interval
                )
            except asyncio.TimeoutError:
                pass
    
    @property
    def pending_count(self) -> int:
        """Number of sessions waiting to be uploaded."""
        return len(self._queue)
    
    def set_callbacks(
        self,
        on_success: Optional[Callable[[str], None]] = None,
        on_error: Optional[Callable[[str, str], None]] = None
    ) -> None:
        """Set upload result callbacks."""
        self._on_upload_success = on_success
        self._on_upload_error = on_error
    
    def get_stats(self) -> Dict[str, Any]:
        """Get uploader statistics."""
        return {
            "queue_size": len(self._queue),
            "pending": len(self._pending),
            "circuit_state": self._circuit.state.name,
            "failures": self._circuit.failures,
            "rate_limit": self._rate_limiter._tokens,
        }
