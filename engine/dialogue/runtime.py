"""Dialogue runtime execution."""

import csv
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from engine.dialogue.parser import DialogueNode, Line, Choice, If, Set, Emit, Call, DialogueTree

logger = logging.getLogger(__name__)


@dataclass
class DialogueState:
    """Current dialogue state."""
    current_dialogue: str = ""
    current_line: int = 0
    variables: Dict[str, Any] = field(default_factory=dict)
    waiting_for_choice: bool = False
    choices: List[Choice] = field(default_factory=list)

class DialogueRuntime:
    """Execute dialogue trees."""

    MAX_STEPS = 512
    
    def __init__(self, game_context=None):
        self.trees: Dict[str, DialogueTree] = {}
        self.characters: Dict[str, Any] = {}
        self.state = DialogueState()
        self.game = game_context
        self.signal_handlers: Dict[str, List[Callable]] = {}
        self._visited: set[tuple[str, int]] = set()
    
    def load_dialogue(self, ast_nodes: List[DialogueNode]) -> None:
        """Load dialogue AST."""
        for node in ast_nodes:
            if isinstance(node, DialogueTree):
                self.trees[node.name] = node
            # Store character definitions if needed
    
    def start(self, dialogue_name: str) -> Optional[Line]:
        """Start a dialogue tree."""
        if dialogue_name not in self.trees:
            return None
        
        self.state.current_dialogue = dialogue_name
        self.state.current_line = 0
        self.state.waiting_for_choice = False
        self.state.choices = []
        self._visited = set()
        
        return self._execute_next()
    
    def _execute_next(self) -> Optional[Line]:
        """Execute next line or handle choices."""
        steps = 0
        while steps < self.MAX_STEPS:
            steps += 1
            tree = self.trees.get(self.state.current_dialogue)
            if not tree:
                return None
            if self.state.current_line >= len(tree.statements):
                return None

            key = (self.state.current_dialogue, self.state.current_line)
            if key in self._visited:
                raise RuntimeError(f"Dialogue cycle detected at {key}")
            self._visited.add(key)

            stmt = tree.statements[self.state.current_line]
            self.state.current_line += 1
            
            result = self._execute_statement(stmt)
            if isinstance(result, Line):
                return result
            if result == "WAIT_CHOICE":
                return None
        raise RuntimeError("Dialogue step limit exceeded")
    
    def _execute_statement(self, stmt: DialogueNode) -> Any:
        """Execute a single statement."""
        if isinstance(stmt, Line):
            return stmt
        
        if isinstance(stmt, Choice):
            self.state.choices.append(stmt)
            self.state.waiting_for_choice = True
            return "WAIT_CHOICE"
        
        if isinstance(stmt, If):
            if self._eval_condition(stmt.condition):
                for s in stmt.body:
                    result = self._execute_statement(s)
                    if result:
                        return result
            elif stmt.else_body:
                for s in stmt.else_body:
                    result = self._execute_statement(s)
                    if result:
                        return result
        
        if isinstance(stmt, Set):
            self.state.variables[stmt.variable] = stmt.value
            if self.game:
                setattr(self.game, stmt.variable, stmt.value)
        
        if isinstance(stmt, Emit):
            self._emit_signal(stmt.signal, stmt.args)
        
        if isinstance(stmt, Call):
            if stmt.method == "goto" and stmt.args:
                target = stmt.args[0]
                if target in self.trees:
                    self.state.current_dialogue = target
                    self.state.current_line = 0
                    return self._execute_next()
        
        return "CONTINUE"
    
    def select_choice(self, index: int) -> Optional[Line]:
        """Select a choice and continue."""
        if 0 <= index < len(self.state.choices):
            choice = self.state.choices[index]
            self.state.choices = []
            self.state.waiting_for_choice = False
            
            if choice.target in self.trees:
                self.state.current_dialogue = choice.target
                self.state.current_line = 0
                self._visited = set()
                return self._execute_next()
        return None
    
    def _eval_condition(self, condition: Any) -> bool:
        """Evaluate a condition."""
        if isinstance(condition, tuple) and len(condition) == 3:
            op, left, right = condition
            left_val = self._resolve_value(left)
            right_val = self._resolve_value(right)
            
            if op == "==": return left_val == right_val
            if op == "!=": return left_val != right_val
            if op == "<": return left_val < right_val
            if op == ">": return left_val > right_val
        
        return bool(self._resolve_value(condition))
    
    def _resolve_value(self, value: Any) -> Any:
        """Resolve a value (variable or literal)."""
        if isinstance(value, str) and value.startswith("$"):
            return self.state.variables.get(value[1:])
        if isinstance(value, str) and value in self.state.variables:
            return self.state.variables[value]
        if isinstance(value, str) and self.game and hasattr(self.game, value):
            return getattr(self.game, value)
        return value
    
    def _emit_signal(self, signal: str, args: List[Any]) -> None:
        """Emit a signal."""
        if signal in self.signal_handlers:
            for handler in self.signal_handlers[signal]:
                handler(*args)
    
    def connect_signal(self, signal: str, handler: Callable) -> None:
        """Connect a signal handler."""
        if signal not in self.signal_handlers:
            self.signal_handlers[signal] = []
        self.signal_handlers[signal].append(handler)
    
    def get_current_line(self) -> Optional[Line]:
        """Get current line without advancing."""
        tree = self.trees.get(self.state.current_dialogue)
        if tree and 0 <= self.state.current_line < len(tree.statements):
            stmt = tree.statements[self.state.current_line]
            if isinstance(stmt, Line):
                return stmt
        return None
    
    def get_choices(self) -> List[Choice]:
        """Get available choices."""
        return self.state.choices
    
    def is_waiting_for_choice(self) -> bool:
        """Check if waiting for player choice."""
        return self.state.waiting_for_choice and len(self.state.choices) > 0


def dialogue_to_json(trees: Dict[str, DialogueTree]) -> str:
    """Serialize dialogue lines and choices to a portable JSON resource."""
    payload = {}
    for name, tree in trees.items():
        rows = []
        for stmt in tree.statements:
            if isinstance(stmt, Line):
                rows.append({"type": "line", "character": stmt.character, "text": stmt.text})
            elif isinstance(stmt, Choice):
                rows.append({"type": "choice", "text": stmt.text, "target": stmt.target})
        payload[name] = rows
    return json.dumps(payload, indent=2, ensure_ascii=False)


def dialogue_to_csv(trees: Dict[str, DialogueTree], path: str | Path) -> None:
    """Export dialogue text to CSV for localization."""
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["dialogue", "index", "type", "character", "text", "target"])
        writer.writeheader()
        for name, tree in trees.items():
            for index, stmt in enumerate(tree.statements):
                if isinstance(stmt, Line):
                    writer.writerow({
                        "dialogue": name,
                        "index": index,
                        "type": "line",
                        "character": stmt.character,
                        "text": stmt.text,
                        "target": "",
                    })
                elif isinstance(stmt, Choice):
                    writer.writerow({
                        "dialogue": name,
                        "index": index,
                        "type": "choice",
                        "character": "",
                        "text": stmt.text,
                        "target": stmt.target,
                    })
