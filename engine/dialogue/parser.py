# /**************************************************************************/
# /*  dialogue/parser.py                                                    */
# /**************************************************************************/

"""Parser for .dlg dialogue files."""

from __future__ import annotations
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from engine.dialogue.lexer import DialogueToken, DialogueTokenType

import logging


logger = logging.getLogger(__name__)

class DialogueParseError(Exception):
    """Parse error."""
    pass

@dataclass
class DialogueNode:
    """Base class for dialogue AST nodes."""
    pass

@dataclass
class CharacterDef(DialogueNode):
    """Character definition."""
    name: str
    properties: Dict[str, Any]

@dataclass
class DialogueTree(DialogueNode):
    """Dialogue tree definition."""
    name: str
    statements: List[DialogueNode]

@dataclass
class Line(DialogueNode):
    """A dialogue line."""
    character: str
    text: str
    bbcode: bool = True

@dataclass
class Choice(DialogueNode):
    """Choice/branch."""
    text: str
    target: str  # Dialogue name to jump to
    condition: Optional[Any] = None

@dataclass
class If(DialogueNode):
    """Conditional block."""
    condition: Any
    body: List[DialogueNode]
    else_body: Optional[List[DialogueNode]] = None

@dataclass
class Set(DialogueNode):
    """Variable assignment."""
    variable: str
    value: Any

@dataclass
class Emit(DialogueNode):
    """Emit signal."""
    signal: str
    args: List[Any]

@dataclass
class Call(DialogueNode):
    """Call game function."""
    method: str
    args: List[Any]

class DialogueParser:
    """Parser for dialogue files."""
    
    def __init__(self, tokens: List[DialogueToken]):
        self.tokens = tokens
        self.current = 0
    
    def parse(self) -> List[DialogueNode]:
        """Parse tokens into AST."""
        nodes = []
        while not self._is_at_end():
            node = self._parse_declaration()
            if node:
                nodes.append(node)
        return nodes
    
    def _parse_declaration(self) -> Optional[DialogueNode]:
        """Parse top-level declaration."""
        if self._match(DialogueTokenType.CHARACTER):
            return self._parse_character()
        if self._match(DialogueTokenType.DIALOGUE):
            return self._parse_dialogue()
        self._advance()
        return None
    
    def _parse_character(self) -> CharacterDef:
        """Parse character definition."""
        name = self._consume(DialogueTokenType.IDENTIFIER, "Expected character name").value
        self._consume(DialogueTokenType.LBRACE, "Expected { after character name")
        props = self._parse_properties()
        self._consume(DialogueTokenType.RBRACE, "Expected } after character properties")
        return CharacterDef(name, props)
    
    def _parse_dialogue(self) -> DialogueTree:
        """Parse dialogue tree."""
        name = self._consume(DialogueTokenType.IDENTIFIER, "Expected dialogue name").value
        self._consume(DialogueTokenType.LBRACE, "Expected { after dialogue name")
        statements = self._parse_statements()
        self._consume(DialogueTokenType.RBRACE, "Expected } after dialogue body")
        return DialogueTree(name, statements)
    
    def _parse_properties(self) -> Dict[str, Any]:
        """Parse property assignments."""
        props = {}
        while not self._check(DialogueTokenType.RBRACE) and not self._is_at_end():
            if self._match(DialogueTokenType.IDENTIFIER):
                key = self._previous().value
                self._consume(DialogueTokenType.ASSIGN, "Expected = after property name")
                value = self._parse_value()
                props[key] = value
        return props
    
    def _parse_statements(self) -> List[DialogueNode]:
        """Parse list of statements."""
        stmts = []
        while not self._check(DialogueTokenType.RBRACE) and not self._is_at_end():
            stmt = self._parse_statement()
            if stmt:
                stmts.append(stmt)
        return stmts
    
    def _parse_statement(self) -> Optional[DialogueNode]:
        """Parse a single statement."""
        # Character: "Text"
        if self._check(DialogueTokenType.IDENTIFIER):
            char = self._advance().value
            self._consume(DialogueTokenType.COLON, "Expected : after character name")
            text = self._consume(DialogueTokenType.STRING, "Expected text").value
            return Line(char, text)
        
        # choice { ... }
        if self._match(DialogueTokenType.CHOICE):
            return self._parse_choice()
        
        # if condition { ... }
        if self._match(DialogueTokenType.IF):
            return self._parse_if()
        
        # set variable = value
        if self._match(DialogueTokenType.SET):
            return self._parse_set()
        
        # emit signal(args)
        if self._match(DialogueTokenType.EMIT):
            return self._parse_emit()
        
        # => target (goto)
        if self._match(DialogueTokenType.ARROW):
            target = self._consume(DialogueTokenType.IDENTIFIER, "Expected target name").value
            return Call("goto", [target])
        
        self._advance()
        return None
    
    def _parse_choice(self) -> Choice:
        """Parse choice statement."""
        text = self._consume(DialogueTokenType.STRING, "Expected choice text").value
        self._consume(DialogueTokenType.ARROW, "Expected => after choice")
        target = self._consume(DialogueTokenType.IDENTIFIER, "Expected target dialogue").value
        return Choice(text, target)
    
    def _parse_if(self) -> If:
        """Parse if statement."""
        condition = self._parse_expression()
        self._consume(DialogueTokenType.LBRACE, "Expected { after condition")
        body = self._parse_statements()
        else_body = None
        if self._match(DialogueTokenType.ELSE):
            self._consume(DialogueTokenType.LBRACE, "Expected { after else")
            else_body = self._parse_statements()
            self._consume(DialogueTokenType.RBRACE, "Expected } after else body")
        self._consume(DialogueTokenType.RBRACE, "Expected } after if body")
        return If(condition, body, else_body)
    
    def _parse_set(self) -> Set:
        """Parse set statement."""
        var = self._consume(DialogueTokenType.IDENTIFIER, "Expected variable name").value
        self._consume(DialogueTokenType.ASSIGN, "Expected = after variable")
        value = self._parse_value()
        return Set(var, value)
    
    def _parse_emit(self) -> Emit:
        """Parse emit statement."""
        signal = self._consume(DialogueTokenType.IDENTIFIER, "Expected signal name").value
        args = []
        if self._match(DialogueTokenType.LPAREN):
            while not self._check(DialogueTokenType.RPAREN):
                args.append(self._parse_value())
                self._match(DialogueTokenType.COMMA)
            self._consume(DialogueTokenType.RPAREN, "Expected ) after emit args")
        return Emit(signal, args)
    
    def _parse_value(self) -> Any:
        """Parse a value."""
        if self._match(DialogueTokenType.STRING):
            return self._previous().value
        if self._match(DialogueTokenType.NUMBER):
            return self._previous().value
        if self._match(DialogueTokenType.IDENTIFIER):
            return self._previous().value
        if self._match(DialogueTokenType.TRUE):
            return True
        if self._match(DialogueTokenType.FALSE):
            return False
        return None
    
    def _parse_expression(self) -> Any:
        """Parse expression."""
        # Simple expression parsing
        left = self._parse_value()
        
        if self._match(DialogueTokenType.EQ):
            return ("==", left, self._parse_value())
        if self._match(DialogueTokenType.NEQ):
            return ("!=", left, self._parse_value())
        if self._match(DialogueTokenType.LT):
            return ("<", left, self._parse_value())
        if self._match(DialogueTokenType.GT):
            return (">", left, self._parse_value())
        
        return left
    
    def _match(self, *types) -> bool:
        """Match any of the given token types."""
        for t in types:
            if self._check(t):
                self._advance()
                return True
        return False
    
    def _check(self, type_) -> bool:
        """Check if current token is of given type."""
        if self._is_at_end():
            return False
        return self._peek().type == type_
    
    def _advance(self) -> DialogueToken:
        """Advance to next token."""
        if not self._is_at_end():
            self.current += 1
        return self._previous()
    
    def _is_at_end(self) -> bool:
        """Check if at end of tokens."""
        return self._peek().type == DialogueTokenType.EOF
    
    def _peek(self) -> DialogueToken:
        """Get current token."""
        return self.tokens[self.current]
    
    def _previous(self) -> DialogueToken:
        """Get previous token."""
        return self.tokens[self.current - 1]
    
    def _consume(self, type_, message: str) -> DialogueToken:
        """Consume token of expected type."""
        if self._check(type_):
            return self._advance()
        raise DialogueParseError(f"{message} at line {self._peek().line}")

def parse_dialogue(tokens: List[DialogueToken]) -> List[DialogueNode]:
    """Parse dialogue tokens into AST."""
    parser = DialogueParser(tokens)
    return parser.parse()
