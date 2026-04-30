# /**************************************************************************/
# /*  interpreter.py                                                        */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

import inspect
from typing import Any, Dict, List, Optional

from engine.scripting.gdlang.ast_nodes import *
from engine.scripting.gdlang.type_system import Vector2, Color, Rect2

import logging


logger = logging.getLogger(__name__)


class RuntimeErrorGd(Exception):
    pass

class ReturnException(Exception):
    def __init__(self, value: Any):
        self.value = value

class Environment:
    def __init__(self, enclosing: Optional['Environment'] = None):
        self.values: Dict[str, Any] = {}
        self.enclosing = enclosing

    def define(self, name: str, value: Any):
        self.values[name] = value

    def assign(self, name: str, value: Any):
        if name in self.values:
            self.values[name] = value
            return
        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return
        raise RuntimeErrorGd(f"Undefined variable '{name}'.")

    def get(self, name: str) -> Any:
        if name in self.values:
            return self.values[name]
        if self.enclosing is not None:
            return self.enclosing.get(name)
        raise RuntimeErrorGd(f"Undefined variable '{name}'.")

class Interpreter:
    def __init__(self, target_node=None):
        self.globals = Environment()
        self.environment = self.globals
        self.target_node = target_node  # The Engine Node this script is attached to

        # Built-ins
        self.globals.define("print", print)
        self.globals.define("Vector2", Vector2)
        self.globals.define("Color", Color)
        self.globals.define("Rect2", Rect2)

    def interpret(self, statements: List[Statement], method_name: Optional[str] = None, args: List[Any] = None):
        try:
            # First pass: definitions
            for stmt in statements:
                if isinstance(stmt, VarDeclSt):
                    self.execute(stmt)
                elif isinstance(stmt, FuncDefSt):
                    self.execute(stmt)
            
            # If executing a specific method
            if method_name:
                func = self.environment.get(method_name)
                return self.call_function(func, args or [])
                
        except RuntimeErrorGd as e:
            print(f"GDLang Runtime Error: {e}")

    def execute(self, stmt: Statement):
        if isinstance(stmt, VarDeclSt):
            value = None
            if stmt.initializer:
                value = self.evaluate(stmt.initializer)
            self.environment.define(stmt.name, value)
            # If script has export, attach it to node's properties
            if stmt.is_export and self.target_node:
                setattr(self.target_node, stmt.name, value)  # simple binding

        elif isinstance(stmt, FuncDefSt):
             self.environment.define(stmt.name, stmt)

        elif isinstance(stmt, AssignSt):
            value = self.evaluate(stmt.value)
            
            # Handle assignment logic based on operator target
            if isinstance(stmt.target, IdentifierEx):
                current = None
                if stmt.operator != "=":
                    current = self.environment.get(stmt.target.name)
            
                if stmt.operator == "=": final_val = value
                elif stmt.operator == "+=": final_val = current + value
                elif stmt.operator == "-=": final_val = current - value
                elif stmt.operator == "*=": final_val = current * value
                elif stmt.operator == "/=": final_val = current / value
                else: final_val = value

                self.environment.assign(stmt.target.name, final_val)
                
            elif isinstance(stmt.target, MemberAccessEx):
                obj = self.evaluate(stmt.target.object)
                current = getattr(obj, stmt.target.member) if stmt.operator != "=" else None
                
                if stmt.operator == "=": final_val = value
                elif stmt.operator == "+=": final_val = current + value
                elif stmt.operator == "-=": final_val = current - value
                
                setattr(obj, stmt.target.member, final_val)
                
        elif isinstance(stmt, ExpressionSt):
            self.evaluate(stmt.expression)

        elif isinstance(stmt, IfSt):
            if self.is_truthy(self.evaluate(stmt.condition)):
                self.execute_block(stmt.then_branch, Environment(self.environment))
            else:
                executed = False
                for elif_b in stmt.elifs:
                    if self.is_truthy(self.evaluate(elif_b.condition)):
                        self.execute_block(elif_b.body, Environment(self.environment))
                        executed = True
                        break
                if not executed and stmt.else_branch:
                    self.execute_block(stmt.else_branch, Environment(self.environment))

        elif isinstance(stmt, WhileSt):
            while self.is_truthy(self.evaluate(stmt.condition)):
                self.execute_block(stmt.body, Environment(self.environment))

        elif isinstance(stmt, ForSt):
            iterable = self.evaluate(stmt.iterable)
            for item in iterable:
                env = Environment(self.environment)
                env.define(stmt.iterator_name, item)
                self.execute_block(stmt.body, env)

        elif isinstance(stmt, ReturnSt):
            value = None
            if stmt.value is not None:
                value = self.evaluate(stmt.value)
            raise ReturnException(value)

    def execute_block(self, statements: List[Statement], env: Environment):
        previous = self.environment
        try:
            self.environment = env
            for stmt in statements:
                self.execute(stmt)
        finally:
            self.environment = previous

    def evaluate(self, expr: Expression) -> Any:
        if isinstance(expr, LiteralEx):
            return expr.value
            
        if isinstance(expr, IdentifierEx):
            # Special scope: check node properties/methods first if target_node exists
            if self.target_node:
                if hasattr(self.target_node, expr.name):
                    return getattr(self.target_node, expr.name)
            return self.environment.get(expr.name)

        if isinstance(expr, BinaryOpEx):
            left = self.evaluate(expr.left)
            right = self.evaluate(expr.right)
            
            op = expr.operator
            if op == "+": return left + right
            elif op == "-": return left - right
            elif op == "*": return left * right
            elif op == "/": return left / right
            elif op == "%": return left % right
            elif op == "==": return left == right
            elif op == "!=": return left != right
            elif op == "<": return left < right
            elif op == "<=": return left <= right
            elif op == ">": return left > right
            elif op == ">=": return left >= right
            elif op == "and": return self.is_truthy(left) and self.is_truthy(right)
            elif op == "or": return self.is_truthy(left) or self.is_truthy(right)

        if isinstance(expr, UnaryOpEx):
            right = self.evaluate(expr.right)
            if expr.operator == "-": return -right
            if expr.operator == "not": return not self.is_truthy(right)

        if isinstance(expr, CallEx):
            callee = self.evaluate(expr.callee)
            args = [self.evaluate(a) for a in expr.arguments]
            return self.call_function(callee, args)

        if isinstance(expr, MemberAccessEx):
            obj = self.evaluate(expr.object)
            if hasattr(obj, expr.member):
                return getattr(obj, expr.member)
            raise RuntimeErrorGd(f"Object does not have property '{expr.member}'.")

        raise RuntimeErrorGd(f"Unknown expression type {type(expr)}")

    def call_function(self, callee: Any, args: List[Any]) -> Any:
        # User defined script func
        if isinstance(callee, FuncDefSt):
            env = Environment(self.environment)
            for i in range(len(callee.params)):
                env.define(callee.params[i], args[i] if i < len(args) else None)
            try:
                self.execute_block(callee.body, env)
            except ReturnException as r:
                return r.value
            return None
            
        # Python callable (native node methods or builtins)
        if callable(callee):
            # Inspect to handle varargs or mismatch gracefully
            sig = inspect.signature(callee)
            try:
                sig.bind(*args)
                return callee(*args)
            except TypeError:
                # If arg mismatch, try passing as is and let python handle error 
                return callee(*args)

        raise RuntimeErrorGd("Can only call functions and classes.")

    def is_truthy(self, obj: Any) -> bool:
        if obj is None: return False
        if isinstance(obj, bool): return obj
        return True
