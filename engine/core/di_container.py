# /**************************************************************************/
# /*  di_container.py                                                       */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Dependency Injection Container for clean architecture.

Features:
- Service registration and resolution
- Lifecycle management (singleton, scoped, transient)
- Factory injection support
- Circular dependency detection
- Lazy initialization
"""

from __future__ import annotations

import inspect
import logging
from abc import ABC
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, get_type_hints

from engine.core.errors import EngineError

logger = logging.getLogger(__name__)

T = TypeVar('T')


class Lifecycle(Enum):
    """Service lifecycle options."""
    SINGLETON = "singleton"  # One instance for app lifetime
    SCOPED = "scoped"        # One instance per scope (e.g., request)
    TRANSIENT = "transient"  # New instance every resolution


@dataclass
class ServiceDescriptor:
    """Service registration descriptor."""
    interface: Type
    implementation: Type
    lifecycle: Lifecycle
    instance: Any = None
    factory: Optional[Callable[..., Any]] = None


class DIError(EngineError):
    """Dependency injection error."""
    pass


class CircularDependencyError(DIError):
    """Circular dependency detected."""
    pass


class ServiceNotFoundError(DIError):
    """Service not registered."""
    pass


class DIContainer:
    """Production-grade dependency injection container."""
    
    def __init__(self):
        self._services: Dict[Type, ServiceDescriptor] = {}
        self._singletons: Dict[Type, Any] = {}
        self._scopes: Dict[str, Dict[Type, Any]] = {}
        self._resolution_stack: List[Type] = []
    
    def register(
        self,
        interface: Type[T],
        implementation: Type[T],
        lifecycle: Lifecycle = Lifecycle.TRANSIENT,
        factory: Optional[Callable[..., T]] = None
    ) -> "DIContainer":
        """Register a service.
        
        Args:
            interface: Abstract type or protocol
            implementation: Concrete implementation
            lifecycle: Instance lifetime
            factory: Optional factory function
            
        Returns:
            Self for fluent API
        """
        if not issubclass(implementation, interface):
            raise DIError(
                f"{implementation} is not subclass of {interface}"
            )
        
        descriptor = ServiceDescriptor(
            interface=interface,
            implementation=implementation,
            lifecycle=lifecycle,
            factory=factory
        )
        
        self._services[interface] = descriptor
        logger.debug(f"Registered {interface.__name__} -> {implementation.__name__}")
        return self
    
    def register_instance(self, interface: Type[T], instance: T) -> "DIContainer":
        """Register pre-created instance (always singleton)."""
        descriptor = ServiceDescriptor(
            interface=interface,
            implementation=type(instance),
            lifecycle=Lifecycle.SINGLETON,
            instance=instance
        )
        self._services[interface] = descriptor
        self._singletons[interface] = instance
        return self
    
    def resolve(self, interface: Type[T], scope_id: Optional[str] = None) -> T:
        """Resolve a service with automatic dependency injection.
        
        Args:
            interface: Type to resolve
            scope_id: Optional scope identifier
            
        Returns:
            Resolved instance
            
        Raises:
            ServiceNotFoundError: If service not registered
            CircularDependencyError: If circular dependency detected
        """
        if interface not in self._services:
            # Try to auto-register concrete types
            if inspect.isclass(interface):
                return self._create_instance(interface, scope_id)
            raise ServiceNotFoundError(f"Service not registered: {interface}")
        
        descriptor = self._services[interface]
        
        # Handle based on lifecycle
        if descriptor.lifecycle == Lifecycle.SINGLETON:
            return self._get_singleton(descriptor)
        
        elif descriptor.lifecycle == Lifecycle.SCOPED:
            if scope_id is None:
                raise DIError(f"Scope required for {interface}")
            return self._get_scoped(descriptor, scope_id)
        
        else:  # TRANSIENT
            return self._create_instance(descriptor.implementation, scope_id, descriptor.factory)
    
    def _get_singleton(self, descriptor: ServiceDescriptor) -> Any:
        """Get or create singleton instance."""
        if descriptor.interface in self._singletons:
            return self._singletons[descriptor.interface]
        
        instance = self._create_instance(
            descriptor.implementation,
            factory=descriptor.factory
        )
        self._singletons[descriptor.interface] = instance
        return instance
    
    def _get_scoped(self, descriptor: ServiceDescriptor, scope_id: str) -> Any:
        """Get or create scoped instance."""
        if scope_id not in self._scopes:
            self._scopes[scope_id] = {}
        
        scope = self._scopes[scope_id]
        if descriptor.interface in scope:
            return scope[descriptor.interface]
        
        instance = self._create_instance(
            descriptor.implementation,
            scope_id=scope_id,
            factory=descriptor.factory
        )
        scope[descriptor.interface] = instance
        return instance
    
    def _create_instance(
        self,
        implementation: Type[T],
        scope_id: Optional[str] = None,
        factory: Optional[Callable[..., T]] = None
    ) -> T:
        """Create instance with constructor injection."""
        # Circular dependency check
        if implementation in self._resolution_stack:
            cycle = " -> ".join(
                t.__name__ for t in self._resolution_stack + [implementation]
            )
            raise CircularDependencyError(f"Circular dependency: {cycle}")
        
        self._resolution_stack.append(implementation)
        
        try:
            # Use factory if provided
            if factory:
                return factory(self)
            
            # Get constructor parameters
            sig = inspect.signature(implementation.__init__)
            type_hints = get_type_hints(implementation.__init__)
            
            # Resolve dependencies
            kwargs = {}
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                
                # Get parameter type
                param_type = type_hints.get(param_name, Any)
                
                # Skip if has default value and not in type hints
                if param.default is not inspect.Parameter.empty:
                    if param_type is Any:
                        continue
                
                # Resolve dependency
                if param_type is not Any:
                    try:
                        kwargs[param_name] = self.resolve(param_type, scope_id)
                    except ServiceNotFoundError:
                        if param.default is inspect.Parameter.empty:
                            raise
            
            # Create instance
            return implementation(**kwargs)
            
        finally:
            self._resolution_stack.pop()
    
    def create_scope(self, scope_id: str) -> "Scope":
        """Create new resolution scope."""
        return Scope(self, scope_id)
    
    def clear_scope(self, scope_id: str) -> None:
        """Clear all scoped instances."""
        if scope_id in self._scopes:
            del self._scopes[scope_id]
    
    def build_provider(self) -> "ServiceProvider":
        """Build immutable service provider."""
        return ServiceProvider(self._services.copy(), self._singletons.copy())


class Scope:
    """Resolution scope for scoped services."""
    
    def __init__(self, container: DIContainer, scope_id: str):
        self._container = container
        self._scope_id = scope_id
    
    def resolve(self, interface: Type[T]) -> T:
        """Resolve service within this scope."""
        return self._container.resolve(interface, self._scope_id)
    
    def __enter__(self) -> "Scope":
        return self
    
    def __exit__(self, *args) -> None:
        self._container.clear_scope(self._scope_id)


class ServiceProvider:
    """Immutable, thread-safe service provider."""
    
    def __init__(
        self,
        services: Dict[Type, ServiceDescriptor],
        singletons: Dict[Type, Any]
    ):
        self._services = services
        self._singletons = singletons
    
    def get_service(self, interface: Type[T]) -> Optional[T]:
        """Get service if registered."""
        if interface in self._singletons:
            return self._singletons[interface]
        
        descriptor = self._services.get(interface)
        if descriptor and descriptor.instance:
            return descriptor.instance
        
        return None
    
    def is_registered(self, interface: Type) -> bool:
        """Check if service is registered."""
        return interface in self._services


# Global container instance
_global_container: Optional[DIContainer] = None


def get_container() -> DIContainer:
    """Get global DI container."""
    global _global_container
    if _global_container is None:
        _global_container = DIContainer()
    return _global_container


def reset_container() -> None:
    """Reset global container (for testing)."""
    global _global_container
    _global_container = None


# Decorator for dependency injection
def inject(func: Callable) -> Callable:
    """Decorator to inject dependencies into function."""
    sig = inspect.signature(func)
    type_hints = get_type_hints(func)
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        container = get_container()
        
        # Resolve missing dependencies
        for param_name, param in sig.parameters.items():
            if param_name in kwargs:
                continue
            
            param_type = type_hints.get(param_name)
            if param_type and container.is_registered(param_type):
                kwargs[param_name] = container.resolve(param_type)
        
        return func(*args, **kwargs)
    
    return wrapper


# Example usage and factory functions
def configure_services() -> DIContainer:
    """Configure production services."""
    container = get_container()
    
    # Register core services
    from engine.core.project_secure import SecureProject, ProjectConfig
    from engine.extensions.manager_secure import SecureExtensionManager
    from engine.telemetry.uploader_secure import SecureTelemetryUploader
    from engine.config.secure_config import TelemetryConfig
    
    # Configuration (singleton)
    config = ProjectConfig(
        enable_encryption=True,
        lazy_loading=True,
        auto_backup=True
    )
    container.register_instance(ProjectConfig, config)
    
    # Telemetry config (singleton)
    telemetry_config = TelemetryConfig(
        endpoint="https://telemetry.gameengine.example",
        batch_size=50,
        rate_limit=120
    )
    container.register_instance(TelemetryConfig, telemetry_config)
    
    # Extension manager (singleton)
    container.register(
        SecureExtensionManager,
        SecureExtensionManager,
        lifecycle=Lifecycle.SINGLETON,
        factory=lambda c: SecureExtensionManager(
            extensions_dir="~/.game_engine/extensions"
        )
    )
    
    # Telemetry uploader (scoped)
    container.register(
        SecureTelemetryUploader,
        SecureTelemetryUploader,
        lifecycle=Lifecycle.SCOPED
    )
    
    return container
