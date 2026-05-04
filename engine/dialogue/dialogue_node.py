"""Dialogue node and graph structure."""

from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime


class DialogueType(Enum):
    """Type of dialogue node."""

    DIALOGUE = "dialogue"
    CHOICE = "choice"
    ACTION = "action"
    CONDITION = "condition"
    START = "start"
    END = "end"


class EmotionType(Enum):
    """Character emotion."""

    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    CONFUSED = "confused"
    SURPRISED = "surprised"


@dataclass
class DialogueChoice:
    """Choice option in dialogue."""

    id: str
    text: str
    next_node_id: str
    condition: Optional[str] = None  # Variable condition
    flag_set: Optional[Dict[str, Any]] = None  # Flags to set


@dataclass
class DialogueNode:
    """Node in dialogue tree."""

    id: str
    type: DialogueType
    character: str = "Narrator"
    text: str = ""
    emotion: EmotionType = EmotionType.NEUTRAL
    next_node_id: Optional[str] = None
    choices: List[DialogueChoice] = None
    actions: List[Dict[str, Any]] = None
    condition: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.choices is None:
            self.choices = []
        if self.actions is None:
            self.actions = []
        if self.variables is None:
            self.variables = {}
        if self.metadata is None:
            self.metadata = {}

    def add_choice(self, choice: DialogueChoice) -> None:
        """Add choice to node."""
        self.choices.append(choice)

    def add_action(self, action_type: str, **params) -> None:
        """Add action to node."""
        action = {'type': action_type}
        action.update(params)
        self.actions.append(action)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['type'] = self.type.value
        data['emotion'] = self.emotion.value
        data['choices'] = [
            {
                'id': c.id,
                'text': c.text,
                'next_node_id': c.next_node_id,
                'condition': c.condition,
                'flag_set': c.flag_set
            }
            for c in self.choices
        ]
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DialogueNode':
        """Create from dictionary."""
        data_copy = data.copy()
        data_copy['type'] = DialogueType(data['type'])
        data_copy['emotion'] = EmotionType(data['emotion'])

        # Reconstruct choices
        choices = []
        for choice_data in data_copy.pop('choices', []):
            choices.append(DialogueChoice(**choice_data))
        data_copy['choices'] = choices

        return cls(**data_copy)

    def is_end_node(self) -> bool:
        """Check if this is an end node."""
        return self.type == DialogueType.END

    def is_choice_node(self) -> bool:
        """Check if this node has choices."""
        return len(self.choices) > 0

    def get_valid_choices(self, variables: Dict[str, Any]) -> List[DialogueChoice]:
        """Get choices that pass conditions."""
        from .branching_logic import BranchingLogic

        valid_choices = []
        for choice in self.choices:
            if choice.condition is None:
                valid_choices.append(choice)
            elif BranchingLogic.evaluate_condition(choice.condition, variables):
                valid_choices.append(choice)

        return valid_choices
