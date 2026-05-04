"""Game save and load management."""

from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import json

from .db_manager import DatabaseManager
from .state_serializer import StateSerializer
from engine.security import KeyManager
from engine.io.encrypted_format import EncryptedFormat


class SaveMetadata:
    """Metadata for a save slot."""

    def __init__(self, slot: int, name: str = ""):
        self.slot = slot
        self.name = name or f"Save {slot}"
        self.playtime = 0
        self.level = "Unknown"
        self.created_at = datetime.now().isoformat()
        self.modified_at = datetime.now().isoformat()
        self.character_name = ""
        self.location = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'slot': self.slot,
            'name': self.name,
            'playtime': self.playtime,
            'level': self.level,
            'created_at': self.created_at,
            'modified_at': self.modified_at,
            'character_name': self.character_name,
            'location': self.location
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SaveMetadata':
        """Create from dictionary."""
        meta = cls(data['slot'], data.get('name', ''))
        meta.playtime = data.get('playtime', 0)
        meta.level = data.get('level', 'Unknown')
        meta.created_at = data.get('created_at', datetime.now().isoformat())
        meta.modified_at = data.get('modified_at', datetime.now().isoformat())
        meta.character_name = data.get('character_name', '')
        meta.location = data.get('location', '')
        return meta


class SaveManager:
    """Manages game saves with database and encryption."""

    MAX_SAVE_SLOTS = 20

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.db = DatabaseManager(str(project_path))
        self.key_manager = KeyManager(str(project_path))
        self.encrypted_format = EncryptedFormat(str(project_path))

    def create_save_slot(self, slot: int, name: str = "") -> None:
        """Create new save slot."""
        if not (1 <= slot <= self.MAX_SAVE_SLOTS):
            raise ValueError(f"Invalid slot number: {slot}")

        metadata = SaveMetadata(slot, name)

        # Store in database
        self.db.insert('save_slots', {
            'slot_number': slot,
            'save_data': b'{}',
            'metadata': json.dumps(metadata.to_dict())
        })

    def save_game(self, slot: int, game_state: Dict[str, Any],
                  metadata: Optional[SaveMetadata] = None,
                  encrypt: bool = True) -> None:
        """Save game state to slot."""
        if not (1 <= slot <= self.MAX_SAVE_SLOTS):
            raise ValueError(f"Invalid slot number: {slot}")

        if metadata is None:
            metadata = SaveMetadata(slot)
        else:
            metadata.modified_at = datetime.now().isoformat()

        # Serialize game state
        serialized = StateSerializer.to_binary(game_state)

        # Store in database
        where = "slot_number = ?"
        existing = self.db.fetch_one(
            "SELECT id FROM save_slots WHERE slot_number = ?",
            (slot,)
        )

        if existing:
            self.db.update(
                'save_slots',
                {
                    'save_data': serialized,
                    'metadata': json.dumps(metadata.to_dict())
                },
                where,
                (slot,)
            )
        else:
            self.db.insert('save_slots', {
                'slot_number': slot,
                'save_data': serialized,
                'metadata': json.dumps(metadata.to_dict())
            })

        # Also save encrypted copy to file
        if encrypt:
            encrypted_data = {
                'state': StateSerializer.to_json(game_state),
                'metadata': metadata.to_dict()
            }
            self.encrypted_format.save(encrypted_data, slot, encrypt=True)

    def load_game(self, slot: int) -> tuple[Dict[str, Any], SaveMetadata]:
        """Load game state from slot."""
        if not (1 <= slot <= self.MAX_SAVE_SLOTS):
            raise ValueError(f"Invalid slot number: {slot}")

        # Try to load from encrypted file first
        try:
            encrypted_data = self.encrypted_format.load(slot, decrypt=True)
            game_state = StateSerializer.from_json(encrypted_data['state'])
            metadata = SaveMetadata.from_dict(encrypted_data['metadata'])
            return game_state, metadata
        except (FileNotFoundError, ValueError):
            pass

        # Fallback to database
        save_data = self.db.fetch_one(
            "SELECT save_data, metadata FROM save_slots WHERE slot_number = ?",
            (slot,)
        )

        if not save_data:
            raise FileNotFoundError(f"Save slot {slot} not found")

        game_state = StateSerializer.from_binary(save_data['save_data'])
        metadata_dict = json.loads(save_data['metadata'])
        metadata = SaveMetadata.from_dict(metadata_dict)

        return game_state, metadata

    def delete_save(self, slot: int) -> None:
        """Delete save slot."""
        if not (1 <= slot <= self.MAX_SAVE_SLOTS):
            raise ValueError(f"Invalid slot number: {slot}")

        # Delete from database
        self.db.delete('save_slots', "slot_number = ?", (slot,))

        # Delete encrypted file
        self.encrypted_format.delete_slot(slot)

    def get_all_saves(self) -> List[SaveMetadata]:
        """Get metadata for all saves."""
        saves = self.db.fetch_all("SELECT metadata FROM save_slots ORDER BY slot_number")

        result = []
        for save in saves:
            try:
                metadata_dict = json.loads(save['metadata'])
                metadata = SaveMetadata.from_dict(metadata_dict)
                result.append(metadata)
            except json.JSONDecodeError:
                pass

        return result

    def get_save_metadata(self, slot: int) -> Optional[SaveMetadata]:
        """Get metadata for specific save slot."""
        save = self.db.fetch_one(
            "SELECT metadata FROM save_slots WHERE slot_number = ?",
            (slot,)
        )

        if not save:
            return None

        try:
            metadata_dict = json.loads(save['metadata'])
            return SaveMetadata.from_dict(metadata_dict)
        except json.JSONDecodeError:
            return None

    def auto_save(self, game_state: Dict[str, Any],
                  metadata: Optional[SaveMetadata] = None) -> int:
        """Create auto-save (uses slot 0)."""
        auto_slot = 0
        if metadata:
            metadata.name = "Auto-save"
        else:
            metadata = SaveMetadata(auto_slot, "Auto-save")

        self.save_game(auto_slot, game_state, metadata, encrypt=True)
        return auto_slot

    def list_save_slots(self) -> List[int]:
        """List all available save slots."""
        saves = self.db.fetch_all(
            "SELECT slot_number FROM save_slots ORDER BY slot_number"
        )
        return [save['slot_number'] for save in saves]

    def is_save_slot_used(self, slot: int) -> bool:
        """Check if save slot has data."""
        save = self.db.fetch_one(
            "SELECT id FROM save_slots WHERE slot_number = ?",
            (slot,)
        )
        return save is not None

    def get_playtime(self, slot: int) -> int:
        """Get playtime for save slot in seconds."""
        metadata = self.get_save_metadata(slot)
        return metadata.playtime if metadata else 0

    def update_playtime(self, slot: int, seconds: int) -> None:
        """Update playtime for save slot."""
        metadata = self.get_save_metadata(slot)
        if metadata:
            metadata.playtime = seconds
            self.db.update(
                'save_slots',
                {'metadata': json.dumps(metadata.to_dict())},
                'slot_number = ?',
                (slot,)
            )
