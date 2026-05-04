"""Serialization of game state for database storage."""

import json
import pickle
import base64
from typing import Any, Dict, Optional, List


class StateSerializer:
    """Handles serialization of game entities and scenes."""

    @staticmethod
    def serialize_scene(scene: Any) -> Dict[str, Any]:
        """Serialize scene to dictionary."""
        return {
            'id': getattr(scene, 'id', None),
            'name': getattr(scene, 'name', 'Scene'),
            'entities': StateSerializer._serialize_entities(
                getattr(scene, 'entities', [])
            ),
            'metadata': {
                'active': getattr(scene, 'active', True),
                'visible': getattr(scene, 'visible', True),
            }
        }

    @staticmethod
    def deserialize_scene(data: Dict[str, Any]) -> Dict[str, Any]:
        """Deserialize scene from dictionary."""
        return {
            'id': data.get('id'),
            'name': data.get('name'),
            'entities': StateSerializer._deserialize_entities(
                data.get('entities', [])
            ),
            'metadata': data.get('metadata', {})
        }

    @staticmethod
    def serialize_entity(entity: Any) -> Dict[str, Any]:
        """Serialize entity to dictionary."""
        components = {}

        # Get components
        if hasattr(entity, 'components'):
            for comp_name, component in entity.components.items():
                components[comp_name] = StateSerializer._serialize_component(component)

        return {
            'id': getattr(entity, 'id', None),
            'name': getattr(entity, 'name', 'Entity'),
            'components': components,
            'properties': StateSerializer._safe_serialize(
                getattr(entity, 'properties', {})
            )
        }

    @staticmethod
    def deserialize_entity(data: Dict[str, Any]) -> Dict[str, Any]:
        """Deserialize entity from dictionary."""
        components = {}

        for comp_name, comp_data in data.get('components', {}).items():
            components[comp_name] = StateSerializer._deserialize_component(comp_data)

        return {
            'id': data.get('id'),
            'name': data.get('name'),
            'components': components,
            'properties': data.get('properties', {})
        }

    @staticmethod
    def _serialize_entities(entities: List[Any]) -> List[Dict[str, Any]]:
        """Serialize list of entities."""
        return [StateSerializer.serialize_entity(entity) for entity in entities]

    @staticmethod
    def _deserialize_entities(entities_data: List[Dict]) -> List[Dict[str, Any]]:
        """Deserialize list of entities."""
        return [StateSerializer.deserialize_entity(data) for data in entities_data]

    @staticmethod
    def _serialize_component(component: Any) -> Dict[str, Any]:
        """Serialize component."""
        data = {}

        # Get all public attributes
        for attr in dir(component):
            if not attr.startswith('_'):
                try:
                    value = getattr(component, attr)
                    # Skip methods
                    if not callable(value):
                        data[attr] = StateSerializer._safe_serialize(value)
                except (AttributeError, RuntimeError):
                    pass

        return data

    @staticmethod
    def _deserialize_component(data: Dict[str, Any]) -> Dict[str, Any]:
        """Deserialize component."""
        return data

    @staticmethod
    def _safe_serialize(obj: Any) -> Any:
        """Safely serialize object to JSON-compatible format."""
        if obj is None or isinstance(obj, (bool, int, float, str)):
            return obj

        if isinstance(obj, (list, tuple)):
            return [StateSerializer._safe_serialize(item) for item in obj]

        if isinstance(obj, dict):
            return {
                str(k): StateSerializer._safe_serialize(v)
                for k, v in obj.items()
            }

        # Try to handle custom objects
        if hasattr(obj, '__dict__'):
            try:
                return StateSerializer._safe_serialize(obj.__dict__)
            except (TypeError, ValueError):
                pass

        # Fallback to string representation
        return str(obj)

    @staticmethod
    def to_json(data: Dict[str, Any]) -> str:
        """Convert to JSON string."""
        return json.dumps(data, indent=2, default=str)

    @staticmethod
    def from_json(json_str: str) -> Dict[str, Any]:
        """Convert from JSON string."""
        return json.loads(json_str)

    @staticmethod
    def to_binary(data: Dict[str, Any]) -> bytes:
        """Serialize to binary format."""
        json_str = StateSerializer.to_json(data)
        return json_str.encode('utf-8')

    @staticmethod
    def from_binary(binary_data: bytes) -> Dict[str, Any]:
        """Deserialize from binary format."""
        json_str = binary_data.decode('utf-8')
        return StateSerializer.from_json(json_str)

    @staticmethod
    def to_base64(data: Dict[str, Any]) -> str:
        """Encode to base64."""
        binary = StateSerializer.to_binary(data)
        return base64.b64encode(binary).decode('ascii')

    @staticmethod
    def from_base64(encoded: str) -> Dict[str, Any]:
        """Decode from base64."""
        binary = base64.b64decode(encoded.encode('ascii'))
        return StateSerializer.from_binary(binary)
