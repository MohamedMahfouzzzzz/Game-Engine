"""Hierarchical telemetry tree for engine monitoring."""

from enum import Enum
from typing import Optional, Dict, List, Any
from datetime import datetime
import json


class EventType(Enum):
    """Types of telemetry events."""

    ENGINE_START = "engine_start"
    ENGINE_STOP = "engine_stop"
    SCENE_LOAD = "scene_load"
    SCENE_UNLOAD = "scene_unload"
    ENTITY_SPAWN = "entity_spawn"
    ENTITY_DESTROY = "entity_destroy"
    COMPONENT_ADD = "component_add"
    COMPONENT_REMOVE = "component_remove"
    SAVE_GAME = "save_game"
    LOAD_GAME = "load_game"
    COLLISION = "collision"
    SCRIPT_ERROR = "script_error"
    PERFORMANCE_WARNING = "performance_warning"
    MEMORY_SPIKE = "memory_spike"
    DEBUG_MARKER = "debug_marker"
    CUSTOM = "custom"


class TelemetryNode:
    """Single node in telemetry tree."""

    def __init__(self, name: str, event_type: EventType, timestamp: Optional[datetime] = None):
        self.name = name
        self.event_type = event_type
        self.timestamp = timestamp or datetime.now()
        self.duration: float = 0.0
        self.children: List['TelemetryNode'] = []
        self.parent: Optional['TelemetryNode'] = None
        self.data: Dict[str, Any] = {}
        self.level = 0

    def add_child(self, child: 'TelemetryNode') -> 'TelemetryNode':
        """Add child node."""
        child.parent = self
        child.level = self.level + 1
        self.children.append(child)
        return child

    def set_duration(self, duration: float) -> None:
        """Set node duration in milliseconds."""
        self.duration = duration

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'event_type': self.event_type.value,
            'timestamp': self.timestamp.isoformat(),
            'duration_ms': self.duration,
            'data': self.data,
            'children': [child.to_dict() for child in self.children]
        }

    def __repr__(self) -> str:
        indent = "  " * self.level
        return f"{indent}{self.name} ({self.event_type.value})"


class TelemetryTree:
    """Hierarchical tree of telemetry events."""

    def __init__(self, name: str = "TelemetryTree"):
        self.name = name
        self.root = TelemetryNode("root", EventType.CUSTOM)
        self.current_node = self.root
        self.event_count = 0
        self.start_time = datetime.now()

    def push_event(self, name: str, event_type: EventType) -> TelemetryNode:
        """Push new event onto stack."""
        node = TelemetryNode(name, event_type)
        self.current_node.add_child(node)
        self.current_node = node
        self.event_count += 1
        return node

    def pop_event(self, duration: float = 0.0) -> Optional[TelemetryNode]:
        """Pop current event from stack."""
        if self.current_node.parent:
            if duration > 0:
                self.current_node.set_duration(duration)
            prev = self.current_node
            self.current_node = self.current_node.parent
            return prev
        return None

    def log_event(self, name: str, event_type: EventType,
                  data: Optional[Dict[str, Any]] = None) -> None:
        """Log event at current level."""
        node = self.push_event(name, event_type)
        if data:
            node.data = data
        self.pop_event()

    def get_event_path(self) -> str:
        """Get path to current event."""
        path = []
        node = self.current_node
        while node and node.parent:
            path.insert(0, node.name)
            node = node.parent
        return " -> ".join(path)

    def get_root_events(self) -> List[TelemetryNode]:
        """Get all root-level events."""
        return self.root.children

    def get_events_by_type(self, event_type: EventType) -> List[TelemetryNode]:
        """Find all events of specific type."""
        result = []

        def search(node: TelemetryNode) -> None:
            if node.event_type == event_type:
                result.append(node)
            for child in node.children:
                search(child)

        search(self.root)
        return result

    def get_event_count(self, event_type: Optional[EventType] = None) -> int:
        """Count events by type."""
        if event_type is None:
            return self.event_count

        return len(self.get_events_by_type(event_type))

    def get_total_duration(self, event_type: Optional[EventType] = None) -> float:
        """Get total duration of events."""
        events = (
            self.get_events_by_type(event_type)
            if event_type
            else self.get_root_events()
        )
        return sum(event.duration for event in events)

    def get_average_duration(self, event_type: EventType) -> float:
        """Get average duration for event type."""
        events = self.get_events_by_type(event_type)
        if not events:
            return 0.0
        return sum(e.duration for e in events) / len(events)

    def clear(self) -> None:
        """Clear tree."""
        self.root = TelemetryNode("root", EventType.CUSTOM)
        self.current_node = self.root
        self.event_count = 0
        self.start_time = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'start_time': self.start_time.isoformat(),
            'event_count': self.event_count,
            'events': [child.to_dict() for child in self.root.children]
        }

    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps(self.to_dict(), indent=2)

    def print_tree(self) -> None:
        """Print tree structure."""
        print(f"=== {self.name} ===")
        for child in self.root.children:
            self._print_node(child)

    def _print_node(self, node: TelemetryNode, indent: int = 0) -> None:
        """Print node and children."""
        prefix = "  " * indent
        print(f"{prefix}{node.name} ({node.event_type.value}) - {node.duration:.2f}ms")
        for child in node.children:
            self._print_node(child, indent + 1)

    def get_stats(self) -> Dict[str, Any]:
        """Get telemetry statistics."""
        stats = {}
        for event_type in EventType:
            events = self.get_events_by_type(event_type)
            if events:
                stats[event_type.value] = {
                    'count': len(events),
                    'total_duration_ms': sum(e.duration for e in events),
                    'average_duration_ms': self.get_average_duration(event_type)
                }
        return stats
