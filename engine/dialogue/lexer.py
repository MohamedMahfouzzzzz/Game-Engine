# /**************************************************************************/
# /*  dialogue/lexer.py                                                     */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Lexer for .dlg dialogue files."""

from __future__ import annotations

from typing import List, Any
from dataclasses import dataclass
from enum import Enum, auto

import logging



logger = logging.getLogger(__name__)

class DialogueTokenType(Enum):
    """Token types for dialogue language."""
    # Literals
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()
    
    # Keywords
    DIALOGUE = auto()
    CHARACTER = auto()
    CHOICE = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    SET = auto()
    EMIT = auto()
    AWAIT = auto()
    RETURN = auto()
    GOTO = auto()
    END = auto()
    
    # Symbols
    LPAREN = auto()      # (
    RPAREN = auto()      # )
    LBRACE = auto()      # {
    RBRACE = auto()      # }
    LBRACKET = auto()    # [
    RBRACKET = auto()    # ]
    COLON = auto()       # :
    SEMICOLON = auto()   # ;
    ARROW = auto()       # =>
    DOT = auto()         # .
    COMMA = auto()       # ,
    ASSIGN = auto()      # =
    
    # Operators
    EQ = auto()          # ==
    NEQ = auto()         # !=
    LT = auto()          # <
    LE = auto()          # <=
    GT = auto()          # >
    GE = auto()          # >=
    PLUS = auto()        # +
    MINUS = auto()       # -
    MUL = auto()         # *
    DIV = auto()         # /
    AND = auto()         # &&
    OR = auto()          # ||
    NOT = auto()         # !
    
    # Text formatting
    BBCODE_START = auto()   # [
    BBCODE_END = auto()     # [/...]
    
    # Special
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()
    EOF = auto()


KEYWORDS = {
    "dialogue": DialogueTokenType.DIALOGUE,
    "character": DialogueTokenType.CHARACTER,
    "choice": DialogueTokenType.CHOICE,
    "if": DialogueTokenType.IF,
    "else": DialogueTokenType.ELSE,
    "while": DialogueTokenType.WHILE,
    "set": DialogueTokenType.SET,
    "emit": DialogueTokenType.EMIT,
    "await": DialogueTokenType.AWAIT,
    "return": DialogueTokenType.RETURN,
    "goto": DialogueTokenType.GOTO,
    "end": DialogueTokenType.END,
}


@dataclass
class DialogueToken:
    """A dialogue token."""
    type: DialogueTokenType
    value: Any
    line: int
    column: int
    
    def __repr__(self) -> str:
        return f"Token({self.type.name}, {repr(self.value)})"


class DialogueLexer:
    """Lexer for dialogue files."""
    
    def __init__(self, source: str):
        self.source = source + "\n"
        self.pos = 0
        self.line = 1
        self.col = 1
        
        self.indent_stack = [0]
        self.tokens: List[DialogueToken] = []
    
    def tokenize(self) -> List[DialogueToken]:
        """Tokenize the source code."""
        while self.pos < len(self.source):
            char = self.source[self.pos]
            
            # Whitespace
            if char in " \t":
                self._advance()
                continue
            
            # Newline
            if char == "\n":
                self._add_token(DialogueTokenType.NEWLINE, "\n")
                self._advance()
                self._handle_indentation()
                continue
            
            # Comments
            if char == "#":
                while self.pos < len(self.source) and self.source[self.pos] != "\n":
                    self._advance()
                continue
            
            # Strings
            if char in '"\'':
                self._read_string(char)
                continue
            
            # Numbers
            if char.isdigit():
                self._read_number()
                continue
            
            # Identifiers
            if char.isalpha() or char == "_":
                self._read_identifier()
                continue
            
            # Two-character operators
            if self._match_op("==", DialogueTokenType.EQ): continue
            if self._match_op("!=", DialogueTokenType.NEQ): continue
            if self._match_op("<=", DialogueTokenType.LE): continue
            if self._match_op(">=", DialogueTokenType.GE): continue
            if self._match_op("&&", DialogueTokenType.AND): continue
            if self._match_op("||", DialogueTokenType.OR): continue
            if self._match_op("=>", DialogueTokenType.ARROW): continue
            
            # Single-character operators
            if self._match_single(char):
                self._advance()
                continue
            
            # Unknown - skip
            self._advance()
        
        # Cleanup indents
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self._add_token(DialogueTokenType.DEDENT, "")
        
        self._add_token(DialogueTokenType.EOF, "")
        return [t for t in self.tokens if t.type != DialogueTokenType.NEWLINE or 
                (self.tokens and self.tokens[-1].type != DialogueTokenType.NEWLINE)]
    
    def _advance(self) -> str:
        """Advance and return current char."""
        char = self.source[self.pos]
        self.pos += 1
        if char == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return char
    
    def _handle_indentation(self) -> None:
        """Handle indentation after newline."""
        spaces = 0
        while self.pos < len(self.source) and self.source[self.pos] in " \t":
            spaces += 4 if self.source[self.pos] == "\t" else 1
            self._advance()
        
        if self.pos < len(self.source) and self.source[self.pos] in "\n#":
            return  # Empty line or comment
        
        current_indent = self.indent_stack[-1]
        
        if spaces > current_indent:
            self.indent_stack.append(spaces)
            self._add_token(DialogueTokenType.INDENT, spaces)
        elif spaces < current_indent:
            while len(self.indent_stack) > 1 and spaces < self.indent_stack[-1]:
                self.indent_stack.pop()
                self._add_token(DialogueTokenType.DEDENT, "")
    
    def _read_identifier(self) -> None:
        """Read an identifier or keyword."""
        start = self.pos
        while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] == "_"):
            self._advance()
        
        value = self.source[start:self.pos]
        token_type = KEYWORDS.get(value, DialogueTokenType.IDENTIFIER)
        self._add_token(token_type, value)
    
    def _read_number(self) -> None:
        """Read a number."""
        start = self.pos
        is_float = False
        while self.pos < len(self.source) and (self.source[self.pos].isdigit() or self.source[self.pos] == "."):
            if self.source[self.pos] == ".":
                is_float = True
            self._advance()
        
        value = self.source[start:self.pos]
        self._add_token(DialogueTokenType.NUMBER, float(value) if is_float else int(value))
    
    def _read_string(self, quote: str) -> None:
        """Read a string literal."""
        self._advance()  # Skip opening quote
        start = self.pos
        
        while self.pos < len(self.source) and self.source[self.pos] != quote:
            if self.source[self.pos] == "\\":
                self._advance()  # Skip escape
            self._advance()
        
        value = self.source[start:self.pos]
        self._add_token(DialogueTokenType.STRING, value)
        self._advance()  # Skip closing quote
    
    def _match_op(self, op: str, token_type: DialogueTokenType) -> bool:
        """Try to match a multi-character operator."""
        if self.source.startswith(op, self.pos):
            self._add_token(token_type, op)
            for _ in op:
                self._advance()
            return True
        return False
    
    def _match_single(self, char: str) -> bool:
        """Try to match a single-character token."""
        symbols = {
            "(": DialogueTokenType.LPAREN,
            ")": DialogueTokenType.RPAREN,
            "{": DialogueTokenType.LBRACE,
            "}": DialogueTokenType.RBRACE,
            "[": DialogueTokenType.LBRACKET,
            "]": DialogueTokenType.RBRACKET,
            ":": DialogueTokenType.COLON,
            ";": DialogueTokenType.SEMICOLON,
            ".": DialogueTokenType.DOT,
            ",": DialogueTokenType.COMMA,
            "=": DialogueTokenType.ASSIGN,
            "<": DialogueTokenType.LT,
            ">": DialogueTokenType.GT,
            "+": DialogueTokenType.PLUS,
            "-": DialogueTokenType.MINUS,
            "*": DialogueTokenType.MUL,
            "/": DialogueTokenType.DIV,
            "!": DialogueTokenType.NOT,
        }
        
        if char in symbols:
            self._add_token(symbols[char], char)
            return True
        return False
    
    def _add_token(self, token_type: DialogueTokenType, value: Any) -> None:
        """Add a token."""
        if token_type == DialogueTokenType.NEWLINE and self.tokens and self.tokens[-1].type == DialogueTokenType.NEWLINE:
            return
        self.tokens.append(DialogueToken(token_type, value, self.line, self.col))
