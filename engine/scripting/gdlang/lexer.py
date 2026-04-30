# /**************************************************************************/
# /*  lexer.py                                                              */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

from typing import Any
import re
from typing import List, Tuple

import logging


logger = logging.getLogger(__name__)


class TokenType:
    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER"
    STRING = "STRING"
    
    # Keywords
    VAR = "VAR"
    CONST = "CONST"
    FUNC = "FUNC"
    IF = "IF"
    ELIF = "ELIF"
    ELSE = "ELSE"
    WHILE = "WHILE"
    FOR = "FOR"
    IN = "IN"
    PASS = "PASS"
    RETURN = "RETURN"
    MATCH = "MATCH"
    EXTENDS = "EXTENDS"
    IGNORING = "IGNORING"
    SIGNAL = "SIGNAL"
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    
    # Symbols
    PLUS = "+"
    MINUS = "-"
    STAR = "*"
    SLASH = "/"
    MOD = "%"
    EQ = "=="
    NEQ = "!="
    LT = "<"
    LE = "<="
    GT = ">"
    GE = ">="
    ASSIGN = "="
    PLUS_ASSIGN = "+="
    MINUS_ASSIGN = "-="
    STAR_ASSIGN = "*="
    SLASH_ASSIGN = "/="
    
    LPAREN = "("
    RPAREN = ")"
    LBRACKET = "["
    RBRACKET = "]"
    LBRACE = "{"
    RBRACE = "}"
    COMMA = ","
    DOT = "."
    COLON = ":"
    
    # Annotations
    AT_EXPORT = "@EXPORT"
    AT_ONREADY = "@ONREADY"
    DOLAR_NODE = "$NODE" # Fast node access like $Sprite
    
    NEWLINE = "NEWLINE"
    INDENT = "INDENT"
    DEDENT = "DEDENT"
    EOF = "EOF"

KEYWORDS = {
    "var": TokenType.VAR,
    "const": TokenType.CONST,
    "func": TokenType.FUNC,
    "if": TokenType.IF,
    "elif": TokenType.ELIF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "for": TokenType.FOR,
    "in": TokenType.IN,
    "pass": TokenType.PASS,
    "return": TokenType.RETURN,
    "match": TokenType.MATCH,
    "extends": TokenType.EXTENDS,
    "signal": TokenType.SIGNAL,
    "and": TokenType.AND,
    "or": TokenType.OR,
    "not": TokenType.NOT,
}

class Token:
    def __init__(self, type_: str, value: Any, line: int, column: int):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)})"

class Lexer:
    def __init__(self, source: str):
        self.source = source + "\n"
        self.pos = 0
        self.line = 1
        self.col = 1
        
        self.indent_stack = [0]
        self.tokens: List[Token] = []

    def tokenize(self) -> List[Token]:
        while self.pos < len(self.source):
            char = self.source[self.pos]

            if char in " \t":
                self.pos += 1
                self.col += 1
                continue
            
            if char == "\n":
                self._add_token(TokenType.NEWLINE, "\n")
                self.pos += 1
                self.col = 1
                self.line += 1
                self._handle_indentation()
                continue
                
            if char == "#":
                while self.pos < len(self.source) and self.source[self.pos] != "\n":
                    self.pos += 1
                continue

            if char == "/" and self.pos + 1 < len(self.source) and self.source[self.pos + 1] == "/":
                while self.pos < len(self.source) and self.source[self.pos] != "\n":
                    self.pos += 1
                continue
                
            if char.isalpha() or char == "_":
                self._read_identifier()
                continue
                
            if char.isdigit():
                self._read_number()
                continue
                
            if char in "'\"":
                self._read_string(char)
                continue
                
            if char == "@":
                self._read_annotation()
                continue
                
            if char == "$":
                self._read_node_path()
                continue
                
            # Operators
            if self._match_op("==", TokenType.EQ): continue
            if self._match_op("!=", TokenType.NEQ): continue
            if self._match_op("<=", TokenType.LE): continue
            if self._match_op(">=", TokenType.GE): continue
            if self._match_op("+=", TokenType.PLUS_ASSIGN): continue
            if self._match_op("-=", TokenType.MINUS_ASSIGN): continue
            if self._match_op("*=", TokenType.STAR_ASSIGN): continue
            if self._match_op("/=", TokenType.SLASH_ASSIGN): continue
            
            # Singles
            if self._match_single(char): continue

            # Unknown char
            self.pos += 1
            self.col += 1

        # Cleanup indents
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self._add_token(TokenType.DEDENT, "")
            
        self._add_token(TokenType.EOF, "")
        return [t for t in self.tokens if t.type != TokenType.NEWLINE or (self.tokens and self.tokens[-1].type != TokenType.NEWLINE)]

    def _handle_indentation(self):
        spaces = 0
        while self.pos < len(self.source) and self.source[self.pos] in " \t":
            spaces += 4 if self.source[self.pos] == "\t" else 1
            self.pos += 1
            self.col += 1
            
        if self.pos < len(self.source) and self.source[self.pos] in "\n#":
            return # empty line or comment
            
        current_indent = self.indent_stack[-1]
        
        if spaces > current_indent:
            self.indent_stack.append(spaces)
            self._add_token(TokenType.INDENT, spaces)
        elif spaces < current_indent:
            while len(self.indent_stack) > 1 and spaces < self.indent_stack[-1]:
                self.indent_stack.pop()
                self._add_token(TokenType.DEDENT, "")

    def _read_identifier(self):
        start = self.pos
        while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] == "_"):
            self.pos += 1
        val = self.source[start:self.pos]
        self.col += len(val)
        ttype = KEYWORDS.get(val, TokenType.IDENTIFIER)
        self._add_token(ttype, val)

    def _read_number(self):
        start = self.pos
        is_float = False
        while self.pos < len(self.source) and (self.source[self.pos].isdigit() or self.source[self.pos] == "."):
            if self.source[self.pos] == ".":
                is_float = True
            self.pos += 1
        val = self.source[start:self.pos]
        self.col += len(val)
        self._add_token(TokenType.NUMBER, float(val) if is_float else int(val))

    def _read_string(self, quote: str):
        self.pos += 1
        start = self.pos
        while self.pos < len(self.source) and self.source[self.pos] != quote:
            self.pos += 1
        val = self.source[start:self.pos]
        self.pos += 1
        self.col += len(val) + 2
        self._add_token(TokenType.STRING, val)
        
    def _read_annotation(self):
        self.pos += 1
        start = self.pos
        while self.pos < len(self.source) and self.source[self.pos].isalpha():
            self.pos += 1
        val = self.source[start:self.pos].lower()
        if val == "export":
            self._add_token(TokenType.AT_EXPORT, "@export")
        elif val == "onready":
            self._add_token(TokenType.AT_ONREADY, "@onready")
        self.col += len(val) + 1

    def _read_node_path(self):
        self.pos += 1
        start = self.pos
        while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] in "_/"):
            self.pos += 1
        val = self.source[start:self.pos]
        self._add_token(TokenType.DOLAR_NODE, val)
        self.col += len(val) + 1

    def _match_op(self, op: str, t_type: str) -> bool:
        if self.source.startswith(op, self.pos):
            self._add_token(t_type, op)
            self.pos += len(op)
            self.col += len(op)
            return True
        return False

    def _match_single(self, char: str) -> bool:
        symbols = {
            "+": TokenType.PLUS, "-": TokenType.MINUS, "*": TokenType.STAR, "/": TokenType.SLASH, "%": TokenType.MOD,
            "=": TokenType.ASSIGN, "<": TokenType.LT, ">": TokenType.GT,
            "(": TokenType.LPAREN, ")": TokenType.RPAREN, "[": TokenType.LBRACKET, "]": TokenType.RBRACKET,
            "{": TokenType.LBRACE, "}": TokenType.RBRACE, ",": TokenType.COMMA, ".": TokenType.DOT, ":": TokenType.COLON
        }
        if char in symbols:
            self._add_token(symbols[char], char)
            self.pos += 1
            self.col += 1
            return True
        return False

    def _add_token(self, type_: str, value: Any):
        # Merge newlines
        if type_ == TokenType.NEWLINE and self.tokens and self.tokens[-1].type == TokenType.NEWLINE:
            return
        self.tokens.append(Token(type_, value, self.line, self.col))
