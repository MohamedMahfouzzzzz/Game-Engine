# /**************************************************************************/
# /*  parser.py                                                             */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

from typing import List, Optional

from engine.scripting.gdlang.lexer import Token, TokenType, Lexer
from engine.scripting.gdlang.ast_nodes import *

import logging


logger = logging.getLogger(__name__)


class ParseError(Exception):
    pass

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> List[Statement]:
        statements = []
        while not self.is_at_end():
            if self.match(TokenType.NEWLINE):
                continue
            statements.append(self.declaration())
        return statements

    def declaration(self) -> Statement:
        try:
            if self.match(TokenType.CLASS_NAME) if hasattr(TokenType, 'CLASS_NAME') else False: 
                # Not fully implementing class_name yet, skip
                self.advance()
            
            if self.match(TokenType.EXTENDS):
                return self.class_declaration()
            if self.match(TokenType.FUNC):
                return self.function_declaration()
            if self.match(TokenType.SIGNAL):
                return self.signal_declaration()
            
            is_export = self.match(TokenType.AT_EXPORT)
            on_ready = self.match(TokenType.AT_ONREADY)
            
            if self.match(TokenType.VAR):
                return self.var_declaration(is_export, False, on_ready)
            if self.match(TokenType.CONST):
                return self.var_declaration(False, True, False)
                
            return self.statement()
        except ParseError as e:
            self.synchronize()
            raise

    def class_declaration(self) -> Statement:
        extends_type = self.consume(TokenType.IDENTIFIER, "Expect superclass name.").value
        self.consume(TokenType.NEWLINE, "Expect newline after extends.")
        return ClassDeclSt(extends_type, [])

    def function_declaration(self) -> Statement:
        name = self.consume(TokenType.IDENTIFIER, "Expect function name.").value
        self.consume(TokenType.LPAREN, "Expect '(' after function name.")
        parameters = []
        if not self.check(TokenType.RPAREN):
            parameters.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name.").value)
            while self.match(TokenType.COMMA):
                parameters.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name.").value)
        self.consume(TokenType.RPAREN, "Expect ')' after parameters.")
        self.consume(TokenType.COLON, "Expect ':' before function body.")
        body = self.block()
        return FuncDefSt(name, parameters, body)

    def signal_declaration(self) -> Statement:
        name = self.consume(TokenType.IDENTIFIER, "Expect signal name.").value
        params = []
        if self.match(TokenType.LPAREN):
            if not self.check(TokenType.RPAREN):
                params.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name.").value)
                while self.match(TokenType.COMMA):
                    params.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name.").value)
            self.consume(TokenType.RPAREN, "Expect ')' after parameters.")
        self.consume(TokenType.NEWLINE, "Expect newline after signal declaration.")
        return SignalDeclSt(name, params)

    def var_declaration(self, is_export: bool, is_const: bool, on_ready: bool) -> Statement:
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.").value
        
        initializer = None
        if self.match(TokenType.ASSIGN):
            initializer = self.expression()
            
        self.consume(TokenType.NEWLINE, "Expect newline after variable declaration.")
        return VarDeclSt(name, is_export, is_const, initializer, on_ready)

    def statement(self) -> Statement:
        if self.match(TokenType.IF):
            return self.if_statement()
        if self.match(TokenType.WHILE):
            return self.while_statement()
        if self.match(TokenType.FOR):
            return self.for_statement()
        if self.match(TokenType.RETURN):
            return self.return_statement()
        if self.match(TokenType.PASS):
            self.consume(TokenType.NEWLINE, "Expect newline after 'pass'.")
            return ExpressionSt(LiteralEx(None)) # dummy
            
        return self.expression_statement()

    def if_statement(self) -> Statement:
        condition = self.expression()
        self.consume(TokenType.COLON, "Expect ':' after if condition.")
        then_branch = self.block()
        
        elifs = []
        while self.match(TokenType.ELIF):
            elif_cond = self.expression()
            self.consume(TokenType.COLON, "Expect ':' after elif condition.")
            elif_body = self.block()
            elifs.append(ElifBranch(elif_cond, elif_body))
            
        else_branch = None
        if self.match(TokenType.ELSE):
            self.consume(TokenType.COLON, "Expect ':' after 'else'.")
            else_branch = self.block()
            
        return IfSt(condition, then_branch, elifs, else_branch)

    def while_statement(self) -> Statement:
        condition = self.expression()
        self.consume(TokenType.COLON, "Expect ':' after while condition.")
        body = self.block()
        return WhileSt(condition, body)

    def for_statement(self) -> Statement:
        name = self.consume(TokenType.IDENTIFIER, "Expect loop variable name.").value
        self.consume(TokenType.IN, "Expect 'in' after for loop variable.")
        iterable = self.expression()
        self.consume(TokenType.COLON, "Expect ':' after for loop iterable.")
        body = self.block()
        return ForSt(name, iterable, body)

    def return_statement(self) -> Statement:
        value = None
        if not self.check(TokenType.NEWLINE):
            value = self.expression()
        self.consume(TokenType.NEWLINE, "Expect newline after return value.")
        return ReturnSt(value)

    def expression_statement(self) -> Statement:
        expr = self.expression()
        if self.match(TokenType.ASSIGN, TokenType.PLUS_ASSIGN, TokenType.MINUS_ASSIGN, TokenType.STAR_ASSIGN, TokenType.SLASH_ASSIGN):
            operator = self.previous().value
            value = self.expression()
            self.consume(TokenType.NEWLINE, "Expect newline after assignment.")
            return AssignSt(expr, operator, value)
            
        self.consume(TokenType.NEWLINE, "Expect newline after expression.")
        return ExpressionSt(expr)

    def block(self) -> List[Statement]:
        statements = []
        self.consume(TokenType.NEWLINE, "Expect newline before block.")
        self.consume(TokenType.INDENT, "Expect indentation for block.")
        
        while not self.check(TokenType.DEDENT) and not self.is_at_end():
            if self.match(TokenType.NEWLINE):
                continue
            statements.append(self.declaration())
            
        self.consume(TokenType.DEDENT, "Expect dedent after block.")
        return statements

    def expression(self) -> Expression:
        return self.logic_or()

    def logic_or(self) -> Expression:
        expr = self.logic_and()
        while self.match(TokenType.OR):
            operator = self.previous().value
            right = self.logic_and()
            expr = BinaryOpEx(expr, operator, right)
        return expr

    def logic_and(self) -> Expression:
        expr = self.equality()
        while self.match(TokenType.AND):
            operator = self.previous().value
            right = self.equality()
            expr = BinaryOpEx(expr, operator, right)
        return expr

    def equality(self) -> Expression:
        expr = self.comparison()
        while self.match(TokenType.EQ, TokenType.NEQ):
            operator = self.previous().value
            right = self.comparison()
            expr = BinaryOpEx(expr, operator, right)
        return expr

    def comparison(self) -> Expression:
        expr = self.term()
        while self.match(TokenType.GT, TokenType.GE, TokenType.LT, TokenType.LE):
            operator = self.previous().value
            right = self.term()
            expr = BinaryOpEx(expr, operator, right)
        return expr

    def term(self) -> Expression:
        expr = self.factor()
        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous().value
            right = self.factor()
            expr = BinaryOpEx(expr, operator, right)
        return expr

    def factor(self) -> Expression:
        expr = self.unary()
        while self.match(TokenType.SLASH, TokenType.STAR, TokenType.MOD):
            operator = self.previous().value
            right = self.unary()
            expr = BinaryOpEx(expr, operator, right)
        return expr

    def unary(self) -> Expression:
        if self.match(TokenType.NOT, TokenType.MINUS):
            operator = self.previous().value
            right = self.unary()
            return UnaryOpEx(operator, right)
        return self.call()

    def call(self) -> Expression:
        expr = self.primary()
        while True:
            if self.match(TokenType.LPAREN):
                expr = self.finish_call(expr)
            elif self.match(TokenType.DOT):
                name = self.consume(TokenType.IDENTIFIER, "Expect property name after '.'.").value
                expr = MemberAccessEx(expr, name)
            elif self.match(TokenType.LBRACKET):
                index = self.expression()
                self.consume(TokenType.RBRACKET, "Expect ']' after index.")
                expr = IndexAccessEx(expr, index)
            else:
                break
        return expr

    def finish_call(self, callee: Expression) -> Expression:
        arguments = []
        if not self.check(TokenType.RPAREN):
            arguments.append(self.expression())
            while self.match(TokenType.COMMA):
                arguments.append(self.expression())
        self.consume(TokenType.RPAREN, "Expect ')' after arguments.")
        return CallEx(callee, arguments)

    def primary(self) -> Expression:
        if self.match(TokenType.NUMBER, TokenType.STRING):
            return LiteralEx(self.previous().value)
        if self.match(TokenType.IDENTIFIER):
            val = self.previous().value
            if val == "true": return LiteralEx(True)
            if val == "false": return LiteralEx(False)
            if val == "null": return LiteralEx(None)
            return IdentifierEx(val)
        if self.match(TokenType.DOLAR_NODE):
            # $NodePath is translated to get_node("NodePath")
            return CallEx(IdentifierEx("get_node"), [LiteralEx(self.previous().value)])
            
        if self.match(TokenType.LPAREN):
            expr = self.expression()
            self.consume(TokenType.RPAREN, "Expect ')' after expression.")
            return expr
            
        raise self.error(self.peek(), "Expect expression.")

    def match(self, *types) -> bool:
        for t in types:
            if self.check(t):
                self.advance()
                return True
        return False

    def check(self, type_: str) -> bool:
        if self.is_at_end():
            if type_ == TokenType.NEWLINE:
                return True # EOF implies newline
            return False
        return self.peek().type == type_

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self) -> bool:
        return self.peek().type == TokenType.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def consume(self, type_: str, message: str) -> Token:
        if self.check(type_):
            return self.advance()
        raise self.error(self.peek(), message)

    def error(self, token: Token, message: str) -> ParseError:
        err = f"[{token.line}:{token.column}] Error at '{token.value}': {message}"
        return ParseError(err)

    def synchronize(self) -> None:
        self.advance()
        while not self.is_at_end():
            if self.previous().type == TokenType.NEWLINE:
                return
            if self.peek().type in (TokenType.FUNC, TokenType.VAR, TokenType.IF, 
                                     TokenType.WHILE, TokenType.FOR, TokenType.RETURN):
                return
            self.advance()
