"""Dialogue manager for in-game conversations."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .dialogue_node import DialogueNode, DialogueType, DialogueChoice
from .branching_logic import BranchingLogic


class Dialogue:
    """Single dialogue/conversation."""

    def __init__(self, dialogue_id: str, name: str):
        self.id = dialogue_id
        self.name = name
        self.nodes: Dict[str, DialogueNode] = {}
        self.start_node_id: Optional[str] = None
        self.variables: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}
        self.created_at = datetime.now().isoformat()

    def add_node(self, node: DialogueNode) -> None:
        """Add node to dialogue."""
        self.nodes[node.id] = node

        # Set first START node as start
        if node.type == DialogueType.START and not self.start_node_id:
            self.start_node_id = node.id

    def get_node(self, node_id: str) -> Optional[DialogueNode]:
        """Get node by ID."""
        return self.nodes.get(node_id)

    def get_next_node(self, current_node_id: str, choice_id: Optional[str] = None) -> Optional[DialogueNode]:
        """Get next node based on current node and optional choice."""
        current = self.get_node(current_node_id)
        if not current:
            return None

        # Handle choice
        if choice_id and current.choices:
            for choice in current.choices:
                if choice.id == choice_id:
                    return self.get_node(choice.next_node_id)

        # Default next node
        if current.next_node_id:
            return self.get_node(current.next_node_id)

        return None

    def get_valid_choices(self, node_id: str) -> List[DialogueChoice]:
        """Get valid choices for node (pass conditions)."""
        node = self.get_node(node_id)
        if not node:
            return []

        return node.get_valid_choices(self.variables)

    def set_variable(self, name: str, value: Any) -> None:
        """Set dialogue variable."""
        self.variables[name] = value

    def get_variable(self, name: str, default: Any = None) -> Any:
        """Get dialogue variable."""
        return self.variables.get(name, default)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'start_node_id': self.start_node_id,
            'nodes': {nid: node.to_dict() for nid, node in self.nodes.items()},
            'variables': self.variables,
            'metadata': self.metadata,
            'created_at': self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Dialogue':
        """Create from dictionary."""
        dialogue = cls(data['id'], data['name'])
        dialogue.start_node_id = data.get('start_node_id')
        dialogue.variables = data.get('variables', {})
        dialogue.metadata = data.get('metadata', {})
        dialogue.created_at = data.get('created_at', datetime.now().isoformat())

        for node_id, node_data in data.get('nodes', {}).items():
            node = DialogueNode.from_dict(node_data)
            dialogue.add_node(node)

        return dialogue

    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'Dialogue':
        """Deserialize from JSON."""
        data = json.loads(json_str)
        return cls.from_dict(data)


class DialogueManager:
    """Manages dialogues for game."""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.dialogues_dir = self.project_path / "Game Files" / "dialogues"
        self.dialogues_dir.mkdir(parents=True, exist_ok=True)
        self.dialogues: Dict[str, Dialogue] = {}
        self.current_dialogue: Optional[Dialogue] = None
        self.current_node_id: Optional[str] = None
        self._load_dialogues()

    def _load_dialogues(self) -> None:
        """Load all dialogues from disk."""
        for dialogue_file in self.dialogues_dir.glob("*.json"):
            try:
                with open(dialogue_file, 'r') as f:
                    data = json.load(f)
                    dialogue = Dialogue.from_dict(data)
                    self.dialogues[dialogue.id] = dialogue
            except (json.JSONDecodeError, OSError, KeyError):
                pass

    def create_dialogue(self, dialogue_id: str, name: str) -> Dialogue:
        """Create new dialogue."""
        dialogue = Dialogue(dialogue_id, name)
        self.dialogues[dialogue_id] = dialogue
        self.save_dialogue(dialogue_id)
        return dialogue

    def get_dialogue(self, dialogue_id: str) -> Optional[Dialogue]:
        """Get dialogue by ID."""
        return self.dialogues.get(dialogue_id)

    def save_dialogue(self, dialogue_id: str) -> bool:
        """Save dialogue to disk."""
        if dialogue_id not in self.dialogues:
            return False

        dialogue = self.dialogues[dialogue_id]
        file_path = self.dialogues_dir / f"{dialogue_id}.json"

        try:
            with open(file_path, 'w') as f:
                f.write(dialogue.to_json())
            return True
        except OSError:
            return False

    def delete_dialogue(self, dialogue_id: str) -> bool:
        """Delete dialogue."""
        if dialogue_id not in self.dialogues:
            return False

        del self.dialogues[dialogue_id]
        file_path = self.dialogues_dir / f"{dialogue_id}.json"
        if file_path.exists():
            file_path.unlink()

        if self.current_dialogue and self.current_dialogue.id == dialogue_id:
            self.current_dialogue = None
            self.current_node_id = None

        return True

    def start_dialogue(self, dialogue_id: str) -> Optional[DialogueNode]:
        """Start playing dialogue."""
        dialogue = self.get_dialogue(dialogue_id)
        if not dialogue or not dialogue.start_node_id:
            return None

        self.current_dialogue = dialogue
        self.current_node_id = dialogue.start_node_id
        return dialogue.get_node(dialogue.start_node_id)

    def advance_dialogue(self, choice_id: Optional[str] = None) -> Optional[DialogueNode]:
        """Advance to next dialogue node."""
        if not self.current_dialogue or not self.current_node_id:
            return None

        current_node = self.current_dialogue.get_node(self.current_node_id)
        if not current_node:
            return None

        # Apply choice effects
        if choice_id:
            for choice in current_node.choices:
                if choice.id == choice_id:
                    # Apply flag changes
                    if choice.flag_set:
                        for flag_name, value in choice.flag_set.items():
                            if isinstance(value, bool):
                                if value:
                                    BranchingLogic.add_flag(
                                        self.current_dialogue.variables,
                                        flag_name
                                    )
                                else:
                                    BranchingLogic.remove_flag(
                                        self.current_dialogue.variables,
                                        flag_name
                                    )
                            else:
                                BranchingLogic.set_variable(
                                    self.current_dialogue.variables,
                                    flag_name,
                                    value
                                )
                    break

        # Get next node
        next_node = self.current_dialogue.get_next_node(self.current_node_id, choice_id)
        if next_node:
            self.current_node_id = next_node.id
            return next_node

        return None

    def get_current_node(self) -> Optional[DialogueNode]:
        """Get current dialogue node."""
        if not self.current_dialogue or not self.current_node_id:
            return None
        return self.current_dialogue.get_node(self.current_node_id)

    def get_current_choices(self) -> List[DialogueChoice]:
        """Get available choices for current node."""
        if not self.current_dialogue or not self.current_node_id:
            return []
        return self.current_dialogue.get_valid_choices(self.current_node_id)

    def end_dialogue(self) -> None:
        """End current dialogue."""
        self.current_dialogue = None
        self.current_node_id = None

    def is_dialogue_active(self) -> bool:
        """Check if dialogue is playing."""
        return self.current_dialogue is not None

    def list_dialogues(self) -> List[str]:
        """List all dialogue IDs."""
        return list(self.dialogues.keys())

    def save_all_dialogues(self) -> None:
        """Save all dialogues."""
        for dialogue_id in self.dialogues:
            self.save_dialogue(dialogue_id)
