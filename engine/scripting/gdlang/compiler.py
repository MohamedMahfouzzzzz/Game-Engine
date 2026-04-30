# /**************************************************************************/
# /*  compiler.py                                                           */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""AST to Bytecode compiler for gdlang."""

from __future__ import annotations

from typing import List, Dict, Any, Optional

from engine.scripting.gdlang.bytecode import (
    OpCode, Chunk, CompiledScript, Instruction
)
from engine.scripting.gdlang.ast_nodes import *

import logging



logger = logging.getLogger(__name__)

class CompileError(Exception):
    """Compilation error."""
    pass


class LocalVar:
    """Local variable tracking."""
    def __init__(self, name: str, depth: int):
        self.name = name
        self.depth = depth


class Compiler:
    """Compiles AST to bytecode."""
    
    def __init__(self):
        self.current_chunk: Chunk = None
        self.script = None
        self.locals: List[LocalVar] = []
        self.scope_depth = 0
        self.function_chunks: Dict[str, Chunk] = {}
        self.class_chunks: Dict[str, Any] = {}
        self.signals: Dict[str, List[str]] = {}
        self.exports: List[str] = []
        self.onready: List[str] = []
        
    def compile(self, statements: List[Statement]) -> CompiledScript:
        """Compile list of statements to bytecode."""
        self.current_chunk = Chunk("<main>")
        
        for stmt in statements:
            self._compile_statement(stmt)
        
        # Add implicit return at end
        self.current_chunk.write(OpCode.PUSH_NULL)
        self.current_chunk.write(OpCode.RETURN)
        
        return CompiledScript(
            main_chunk=self.current_chunk,
            functions=self.function_chunks,
            classes=self.class_chunks,
            signals=self.signals,
            exports=self.exports,
            onready=self.onready
        )
    
    def _compile_statement(self, stmt: Statement) -> None:
        """Compile a single statement."""
        if isinstance(stmt, VarDeclSt):
            self._compile_var_decl(stmt)
        elif isinstance(stmt, FuncDefSt):
            self._compile_func_def(stmt)
        elif isinstance(stmt, AssignSt):
            self._compile_assign(stmt)
        elif isinstance(stmt, ExpressionSt):
            self._compile_expression(stmt.expression)
            self.current_chunk.write(OpCode.POP)  # Discard result
        elif isinstance(stmt, IfSt):
            self._compile_if(stmt)
        elif isinstance(stmt, WhileSt):
            self._compile_while(stmt)
        elif isinstance(stmt, ForSt):
            self._compile_for(stmt)
        elif isinstance(stmt, ReturnSt):
            self._compile_return(stmt)
        elif isinstance(stmt, SignalDeclSt):
            self._compile_signal(stmt)
        elif isinstance(stmt, ClassDeclSt):
            self._compile_class(stmt)
        elif isinstance(stmt, PassSt):
            pass  # No-op
        else:
            raise CompileError(f"Unknown statement type: {type(stmt)}")
    
    def _compile_var_decl(self, stmt: VarDeclSt) -> None:
        """Compile variable declaration."""
        # Track exports and onready
        if stmt.is_export:
            self.exports.append(stmt.name)
        if stmt.on_ready:
            self.onready.append(stmt.name)
        
        # Compile initializer if present
        if stmt.initializer:
            self._compile_expression(stmt.initializer)
        else:
            self.current_chunk.write(OpCode.PUSH_NULL)
        
        # Store in local or global
        if self.scope_depth > 0:
            # Local variable
            self.locals.append(LocalVar(stmt.name, self.scope_depth))
            self.current_chunk.local_count += 1
            # Value is already on stack, no need to store explicitly
        else:
            # Global variable
            idx = self.current_chunk.add_const(stmt.name)
            self.current_chunk.write(OpCode.STORE_GLOBAL, idx)
    
    def _compile_func_def(self, stmt: FuncDefSt) -> None:
        """Compile function definition."""
        # Create new chunk for function
        func_chunk = Chunk(stmt.name)
        func_chunk.param_count = len(stmt.params)
        
        # Save current context
        prev_chunk = self.current_chunk
        prev_locals = self.locals
        prev_depth = self.scope_depth
        
        # Switch to function context
        self.current_chunk = func_chunk
        self.locals = []
        self.scope_depth = 1
        
        # Add parameters as locals
        for param in stmt.params:
            self.locals.append(LocalVar(param, 1))
        
        # Compile function body
        for body_stmt in stmt.body:
            self._compile_statement(body_stmt)
        
        # Add implicit return if needed
        if not func_chunk.instructions or func_chunk.instructions[-1].opcode != OpCode.RETURN:
            func_chunk.write(OpCode.PUSH_NULL)
            func_chunk.write(OpCode.RETURN)
        
        # Store function chunk
        self.function_chunks[stmt.name] = func_chunk
        
        # Restore context
        self.current_chunk = prev_chunk
        self.locals = prev_locals
        self.scope_depth = prev_depth
        
        # Store function reference in main chunk
        idx = self.current_chunk.add_const(stmt.name)
        self.current_chunk.write(OpCode.PUSH_CONST, idx)
        if self.scope_depth > 0:
            self.locals.append(LocalVar(stmt.name, self.scope_depth))
        else:
            self.current_chunk.write(OpCode.STORE_GLOBAL, idx)
    
    def _compile_assign(self, stmt: AssignSt) -> None:
        """Compile assignment."""
        self._compile_expression(stmt.value)
        
        if isinstance(stmt.target, IdentifierEx):
            name = stmt.target.name
            # Check if local
            for i, local in enumerate(reversed(self.locals)):
                if local.name == name:
                    # Handle compound assignment
                    if stmt.operator != "=":
                        self.current_chunk.write(OpCode.LOAD_LOCAL, len(self.locals) - 1 - i)
                        self._compile_binary_op(stmt.operator[:-1])  # Remove =
                    self.current_chunk.write(OpCode.STORE_LOCAL, len(self.locals) - 1 - i)
                    return
            
            # Global
            idx = self.current_chunk.add_const(name)
            if stmt.operator != "=":
                self.current_chunk.write(OpCode.LOAD_GLOBAL, idx)
                self._compile_binary_op(stmt.operator[:-1])
            self.current_chunk.write(OpCode.STORE_GLOBAL, idx)
            
        elif isinstance(stmt.target, MemberAccessEx):
            self._compile_expression(stmt.target.object)
            idx = self.current_chunk.add_const(stmt.target.member)
            self.current_chunk.write(OpCode.PUSH_CONST, idx)
            if stmt.operator != "=":
                self.current_chunk.write(OpCode.DUP)
                self.current_chunk.write(OpCode.INDEX_GET)
                self._compile_binary_op(stmt.operator[:-1])
            self.current_chunk.write(OpCode.STORE_MEMBER)
    
    def _compile_if(self, stmt: IfSt) -> None:
        """Compile if statement."""
        self._compile_expression(stmt.condition)
        
        # Jump to else/endif if condition is false
        jump_if_false_idx = len(self.current_chunk.instructions)
        self.current_chunk.write(OpCode.JUMP_IF_FALSE, 0)  # Placeholder
        
        # Compile then branch
        for body_stmt in stmt.then_branch:
            self._compile_statement(body_stmt)
        
        # Jump over else branches
        jump_end_idx = len(self.current_chunk.instructions)
        self.current_chunk.write(OpCode.JUMP, 0)  # Placeholder
        
        # Patch the jump_if_false to here
        else_start = len(self.current_chunk.instructions)
        self.current_chunk.instructions[jump_if_false_idx].operand = else_start
        
        # Compile elif branches
        for elif_b in stmt.elifs:
            self._compile_expression(elif_b.condition)
            jump_elif_idx = len(self.current_chunk.instructions)
            self.current_chunk.write(OpCode.JUMP_IF_FALSE, 0)
            
            for body_stmt in elif_b.body:
                self._compile_statement(body_stmt)
            
            # Jump over remaining branches
            jump_after_elif = len(self.current_chunk.instructions)
            self.current_chunk.write(OpCode.JUMP, 0)
            
            # Patch this elif's jump
            self.current_chunk.instructions[jump_elif_idx].operand = len(self.current_chunk.instructions)
        
        # Compile else branch
        if stmt.else_branch:
            for body_stmt in stmt.else_branch:
                self._compile_statement(body_stmt)
        
        # Patch all end jumps
        end_idx = len(self.current_chunk.instructions)
        self.current_chunk.instructions[jump_end_idx].operand = end_idx
        for i, inst in enumerate(self.current_chunk.instructions):
            if inst.opcode == OpCode.JUMP and inst.operand == 0 and i > jump_end_idx:
                self.current_chunk.instructions[i].operand = end_idx
    
    def _compile_while(self, stmt: WhileSt) -> None:
        """Compile while loop."""
        loop_start = len(self.current_chunk.instructions)
        
        self._compile_expression(stmt.condition)
        jump_exit_idx = len(self.current_chunk.instructions)
        self.current_chunk.write(OpCode.JUMP_IF_FALSE, 0)
        
        for body_stmt in stmt.body:
            self._compile_statement(body_stmt)
        
        self.current_chunk.write(OpCode.JUMP, loop_start)
        
        exit_idx = len(self.current_chunk.instructions)
        self.current_chunk.instructions[jump_exit_idx].operand = exit_idx
    
    def _compile_for(self, stmt: ForSt) -> None:
        """Compile for loop."""
        # Compile iterable
        self._compile_expression(stmt.iterable)
        
        # TODO: Implement iterator protocol
        # For now, simple array iteration
        self.scope_depth += 1
        self.locals.append(LocalVar(stmt.iterator_name, self.scope_depth))
        
        for body_stmt in stmt.body:
            self._compile_statement(body_stmt)
        
        self.scope_depth -= 1
        self.locals.pop()
    
    def _compile_return(self, stmt: ReturnSt) -> None:
        """Compile return statement."""
        if stmt.value:
            self._compile_expression(stmt.value)
        else:
            self.current_chunk.write(OpCode.PUSH_NULL)
        self.current_chunk.write(OpCode.RETURN)
    
    def _compile_signal(self, stmt: SignalDeclSt) -> None:
        """Compile signal declaration."""
        self.signals[stmt.name] = stmt.params
    
    def _compile_class(self, stmt: ClassDeclSt) -> None:
        """Compile class declaration."""
        # TODO: Full class compilation
        self.class_chunks[stmt.extends] = stmt
    
    def _compile_expression(self, expr: Expression) -> None:
        """Compile expression."""
        if isinstance(expr, LiteralEx):
            self._compile_literal(expr)
        elif isinstance(expr, IdentifierEx):
            self._compile_identifier(expr)
        elif isinstance(expr, BinaryOpEx):
            self._compile_binary(expr)
        elif isinstance(expr, UnaryOpEx):
            self._compile_unary(expr)
        elif isinstance(expr, CallEx):
            self._compile_call(expr)
        elif isinstance(expr, MemberAccessEx):
            self._compile_member_access(expr)
        elif isinstance(expr, IndexAccessEx):
            self._compile_index_access(expr)
        else:
            raise CompileError(f"Unknown expression type: {type(expr)}")
    
    def _compile_literal(self, expr: LiteralEx) -> None:
        """Compile literal expression."""
        if expr.value is None:
            self.current_chunk.write(OpCode.PUSH_NULL)
        elif expr.value is True:
            self.current_chunk.write(OpCode.PUSH_TRUE)
        elif expr.value is False:
            self.current_chunk.write(OpCode.PUSH_FALSE)
        else:
            idx = self.current_chunk.add_const(expr.value)
            self.current_chunk.write(OpCode.PUSH_CONST, idx)
    
    def _compile_identifier(self, expr: IdentifierEx) -> None:
        """Compile identifier expression."""
        name = expr.name
        
        # Check locals (in reverse order)
        for i, local in enumerate(reversed(self.locals)):
            if local.name == name:
                self.current_chunk.write(OpCode.LOAD_LOCAL, len(self.locals) - 1 - i)
                return
        
        # Global
        idx = self.current_chunk.add_const(name)
        self.current_chunk.write(OpCode.LOAD_GLOBAL, idx)
    
    def _compile_binary(self, expr: BinaryOpEx) -> None:
        """Compile binary expression."""
        self._compile_expression(expr.left)
        self._compile_expression(expr.right)
        self._compile_binary_op(expr.operator)
    
    def _compile_binary_op(self, op: str) -> None:
        """Compile binary operator."""
        op_map = {
            "+": OpCode.ADD,
            "-": OpCode.SUB,
            "*": OpCode.MUL,
            "/": OpCode.DIV,
            "%": OpCode.MOD,
            "==": OpCode.EQ,
            "!=": OpCode.NEQ,
            "<": OpCode.LT,
            "<=": OpCode.LE,
            ">": OpCode.GT,
            ">=": OpCode.GE,
            "and": OpCode.AND,
            "or": OpCode.OR,
        }
        
        if op in op_map:
            self.current_chunk.write(op_map[op])
        else:
            raise CompileError(f"Unknown operator: {op}")
    
    def _compile_unary(self, expr: UnaryOpEx) -> None:
        """Compile unary expression."""
        self._compile_expression(expr.right)
        
        if expr.operator == "-":
            self.current_chunk.write(OpCode.NEG)
        elif expr.operator == "not":
            self.current_chunk.write(OpCode.NOT)
        else:
            raise CompileError(f"Unknown unary operator: {expr.operator}")
    
    def _compile_call(self, expr: CallEx) -> None:
        """Compile call expression."""
        # Compile arguments first (they go on stack)
        for arg in expr.arguments:
            self._compile_expression(arg)
        
        # Compile callee
        self._compile_expression(expr.callee)
        
        # Call instruction
        self.current_chunk.write(OpCode.CALL, len(expr.arguments))
    
    def _compile_member_access(self, expr: MemberAccessEx) -> None:
        """Compile member access expression."""
        self._compile_expression(expr.object)
        idx = self.current_chunk.add_const(expr.member)
        self.current_chunk.write(OpCode.PUSH_CONST, idx)
        self.current_chunk.write(OpCode.LOAD_MEMBER)
    
    def _compile_index_access(self, expr: IndexAccessEx) -> None:
        """Compile index access expression."""
        self._compile_expression(expr.object)
        self._compile_expression(expr.index)
        self.current_chunk.write(OpCode.INDEX_GET)


def compile_ast(statements: List[Statement]) -> CompiledScript:
    """Main entry point: compile AST to bytecode."""
    compiler = Compiler()
    return compiler.compile(statements)
