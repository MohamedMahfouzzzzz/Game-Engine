# /**************************************************************************/
# /*  vm.py                                                                 */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Stack-based bytecode virtual machine for gdlang."""

from __future__ import annotations

from typing import List, Any, Dict, Optional, Callable
from dataclasses import dataclass, field

from engine.scripting.gdlang.bytecode import (
    OpCode, Chunk, CompiledScript, Instruction
)
from engine.scripting.gdlang.type_system import Vector2, Color, Rect2

import logging



logger = logging.getLogger(__name__)

class VMError(RuntimeError):
    """VM execution error."""
    pass


@dataclass
class CallFrame:
    """A call frame for function execution."""
    chunk: Chunk
    ip: int = 0  # Instruction pointer
    stack_base: int = 0
    locals: Dict[int, Any] = field(default_factory=dict)


class VM:
    """Stack-based bytecode interpreter with security limits.
    
    Security features:
    - Maximum stack size to prevent stack overflow
    - Maximum call depth to prevent infinite recursion
    - Maximum execution steps (instruction count) for timeout
    - Type-safe operations
    """
    
    # Security limits
    MAX_STACK_SIZE = 1000          # Max stack elements
    MAX_CALL_DEPTH = 50            # Max function call depth
    MAX_EXECUTION_STEPS = 100000   # Max instructions to execute (timeout)
    
    def __init__(self, target_node=None):
        self.stack: List[Any] = []
        self.frames: List[CallFrame] = []
        self.globals: Dict[str, Any] = {}
        self.script: CompiledScript = None
        self.target_node = target_node
        
        # Execution tracking for security
        self._execution_steps = 0
        
        # Initialize built-ins
        self._init_builtins()
    
    def _init_builtins(self) -> None:
        """Initialize built-in functions and types.
        
        Registers all GDScript-compatible types for native use.
        """
        from engine.scripting.gdlang.type_system import (
            Vector2, Vector2i,
            Rect2, Rect2i,
            Color, Transform2D,
            Array, Dict,
            StringName, NodePath,
            Callable, Signal,
            PackedByteArray,
            PackedInt32Array,
            PackedFloat32Array,
            PackedStringArray,
            PackedVector2Array,
            PackedColorArray,
            RID,
        )
        
        self.globals["print"] = self._builtin_print
        
        # 2D Types
        self.globals["Vector2"] = Vector2
        self.globals["Vector2i"] = Vector2i

        # Rectangle Types
        self.globals["Rect2"] = Rect2
        self.globals["Rect2i"] = Rect2i
        
        # Color
        self.globals["Color"] = Color
        
        # Transform
        self.globals["Transform2D"] = Transform2D
        
        # Array Types
        self.globals["Array"] = Array
        self.globals["Dictionary"] = Dict
        
        # String Types
        self.globals["StringName"] = StringName
        self.globals["NodePath"] = NodePath
        
        # Callable & Signal
        self.globals["Callable"] = Callable
        self.globals["Signal"] = Signal
        
        # Packed Arrays
        self.globals["PackedByteArray"] = PackedByteArray
        self.globals["PackedInt32Array"] = PackedInt32Array
        self.globals["PackedFloat32Array"] = PackedFloat32Array
        self.globals["PackedStringArray"] = PackedStringArray
        self.globals["PackedVector2Array"] = PackedVector2Array
        self.globals["PackedColorArray"] = PackedColorArray
        
        # RID
        self.globals["RID"] = RID
        
        # Node access
        if self.target_node:
            self.globals["self"] = self.target_node
    
    def _builtin_print(self, *args) -> None:
        """Built-in print function."""
        print(*args)
    
    def run(self, script: CompiledScript, method_name: Optional[str] = None) -> Any:
        """Run compiled script."""
        self.script = script
        
        # Determine which chunk to run
        if method_name and method_name in script.functions:
            chunk = script.functions[method_name]
        else:
            chunk = script.main_chunk
        
        # Create initial frame
        frame = CallFrame(chunk=chunk)
        self.frames.append(frame)
        
        try:
            return self._execute()
        except VMError as e:
            # Add stack trace
            trace = self._format_stack_trace()
            raise VMError(f"{e}\n{trace}")
    
    def _execute(self) -> Any:
        """Main execution loop with security checks."""
        while self.frames:
            # Security: Check call depth
            if len(self.frames) > self.MAX_CALL_DEPTH:
                raise VMError(
                    f"Maximum call depth exceeded ({self.MAX_CALL_DEPTH}). "
                    "Possible infinite recursion."
                )
            
            # Security: Check execution steps (timeout)
            self._execution_steps += 1
            if self._execution_steps > self.MAX_EXECUTION_STEPS:
                raise VMError(
                    f"Maximum execution steps exceeded ({self.MAX_EXECUTION_STEPS}). "
                    "Possible infinite loop."
                )
            
            frame = self.frames[-1]
            
            if frame.ip >= len(frame.chunk.instructions):
                # End of chunk
                self.frames.pop()
                continue
            
            inst = frame.chunk.instructions[frame.ip]
            frame.ip += 1
            
            try:
                result = self._execute_instruction(inst, frame)
                if result is not None:  # Return value
                    self.frames.pop()
                    if not self.frames:
                        return result
                    self._push(result)
            except Exception as e:
                if isinstance(e, VMError):
                    raise
                raise VMError(f"At instruction {frame.ip-1}: {e}")
        
        # Return top of stack or None
        if self.stack:
            return self._pop()
        return None
    
    def _execute_instruction(self, inst: Instruction, frame: CallFrame) -> Optional[Any]:
        """Execute a single instruction."""
        op = inst.opcode
        
        # Stack operations
        if op == OpCode.PUSH_CONST:
            self._push(frame.chunk.constants[inst.operand])
        elif op == OpCode.PUSH_NULL:
            self._push(None)
        elif op == OpCode.PUSH_TRUE:
            self._push(True)
        elif op == OpCode.PUSH_FALSE:
            self._push(False)
        elif op == OpCode.POP:
            self._pop()
        elif op == OpCode.DUP:
            self._push(self.stack[-1])
        elif op == OpCode.SWAP:
            self.stack[-1], self.stack[-2] = self.stack[-2], self.stack[-1]
        
        # Variable operations
        elif op == OpCode.LOAD_LOCAL:
            idx = inst.operand + frame.stack_base
            self._push(frame.locals.get(idx, None))
        elif op == OpCode.STORE_LOCAL:
            idx = inst.operand + frame.stack_base
            frame.locals[idx] = self._pop()
        elif op == OpCode.LOAD_GLOBAL:
            name = frame.chunk.constants[inst.operand]
            if name in self.globals:
                self._push(self.globals[name])
            else:
                raise VMError(f"Undefined global: {name}")
        elif op == OpCode.STORE_GLOBAL:
            name = frame.chunk.constants[inst.operand]
            self.globals[name] = self._pop()
        elif op == OpCode.LOAD_MEMBER:
            member = self._pop()
            obj = self._pop()
            if hasattr(obj, member):
                self._push(getattr(obj, member))
            else:
                raise VMError(f"Object has no member: {member}")
        elif op == OpCode.STORE_MEMBER:
            value = self._pop()
            member = self._pop()
            obj = self._pop()
            if hasattr(obj, member):
                setattr(obj, member, value)
            else:
                raise VMError(f"Cannot set member on object: {member}")
        
        # Arithmetic
        elif op == OpCode.ADD:
            b, a = self._pop(), self._pop()
            self._push(a + b)
        elif op == OpCode.SUB:
            b, a = self._pop(), self._pop()
            self._push(a - b)
        elif op == OpCode.MUL:
            b, a = self._pop(), self._pop()
            self._push(a * b)
        elif op == OpCode.DIV:
            b, a = self._pop(), self._pop()
            if b == 0:
                raise VMError("Division by zero")
            self._push(a / b)
        elif op == OpCode.MOD:
            b, a = self._pop(), self._pop()
            self._push(a % b)
        elif op == OpCode.NEG:
            self._push(-self._pop())
        
        # Comparison
        elif op == OpCode.EQ:
            b, a = self._pop(), self._pop()
            self._push(a == b)
        elif op == OpCode.NEQ:
            b, a = self._pop(), self._pop()
            self._push(a != b)
        elif op == OpCode.LT:
            b, a = self._pop(), self._pop()
            self._push(a < b)
        elif op == OpCode.LE:
            b, a = self._pop(), self._pop()
            self._push(a <= b)
        elif op == OpCode.GT:
            b, a = self._pop(), self._pop()
            self._push(a > b)
        elif op == OpCode.GE:
            b, a = self._pop(), self._pop()
            self._push(a >= b)
        
        # Logical
        elif op == OpCode.AND:
            b, a = self._pop(), self._pop()
            self._push(self._is_truthy(a) and self._is_truthy(b))
        elif op == OpCode.OR:
            b, a = self._pop(), self._pop()
            self._push(self._is_truthy(a) or self._is_truthy(b))
        elif op == OpCode.NOT:
            self._push(not self._is_truthy(self._pop()))
        
        # Control flow
        elif op == OpCode.JUMP:
            frame.ip = inst.operand
        elif op == OpCode.JUMP_IF_FALSE:
            if not self._is_truthy(self._pop()):
                frame.ip = inst.operand
        elif op == OpCode.JUMP_IF_TRUE:
            if self._is_truthy(self._pop()):
                frame.ip = inst.operand
        
        # Function call
        elif op == OpCode.CALL:
            arg_count = inst.operand
            args = [self._pop() for _ in range(arg_count)]
            args.reverse()
            callee = self._pop()
            return self._call_function(callee, args)
        
        elif op == OpCode.RETURN:
            return self._pop()
        
        # Collections
        elif op == OpCode.BUILD_ARRAY:
            count = inst.operand
            items = [self._pop() for _ in range(count)]
            items.reverse()
            self._push(items)
        elif op == OpCode.BUILD_DICT:
            count = inst.operand
            pairs = [(self._pop(), self._pop()) for _ in range(count)]
            d = {}
            for k, v in reversed(pairs):
                d[k] = v
            self._push(d)
        elif op == OpCode.INDEX_GET:
            idx = self._pop()
            obj = self._pop()
            if isinstance(obj, list):
                self._push(obj[idx])
            elif isinstance(obj, dict):
                self._push(obj.get(idx))
            else:
                raise VMError(f"Cannot index object of type {type(obj)}")
        elif op == OpCode.INDEX_SET:
            value = self._pop()
            idx = self._pop()
            obj = self._pop()
            if isinstance(obj, list):
                obj[idx] = value
            elif isinstance(obj, dict):
                obj[idx] = value
            else:
                raise VMError(f"Cannot index object of type {type(obj)}")
        
        else:
            raise VMError(f"Unknown opcode: {op}")
        
        return None
    
    def _push(self, value: Any) -> None:
        """Push value onto stack with security check."""
        # Security: Check stack size to prevent stack overflow
        if len(self.stack) >= self.MAX_STACK_SIZE:
            raise VMError(
                f"Stack overflow: maximum stack size ({self.MAX_STACK_SIZE}) exceeded. "
                "Possible infinite recursion or excessive data."
            )
        self.stack.append(value)
    
    def _pop(self) -> Any:
        """Pop value from stack."""
        if not self.stack:
            raise VMError("Stack underflow")
        return self.stack.pop()
    
    def _is_truthy(self, value: Any) -> bool:
        """Check if value is truthy."""
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, (list, str)):
            return len(value) > 0
        return True
    
    def _call_function(self, callee: Any, args: List[Any]) -> Optional[Any]:
        """Call a function."""
        # Check if it's a compiled chunk
        if isinstance(callee, Chunk):
            if callee.param_count != len(args):
                raise VMError(f"Expected {callee.param_count} arguments, got {len(args)}")
            
            frame = CallFrame(chunk=callee, stack_base=len(self.stack))
            
            # Store arguments as locals
            for i, arg in enumerate(args):
                frame.locals[i] = arg
            
            self.frames.append(frame)
            return None  # Continue execution
        
        # Python callable
        if callable(callee):
            result = callee(*args)
            self._push(result)
            return None
        
        raise VMError(f"Cannot call object of type {type(callee)}")
    
    def _format_stack_trace(self) -> str:
        """Format stack trace for debugging."""
        lines = ["Stack trace:"]
        for i, frame in enumerate(reversed(self.frames)):
            lines.append(f"  {i}: {frame.chunk.name} (ip={frame.ip})")
        return "\n".join(lines)
    
    def get_global(self, name: str) -> Any:
        """Get global variable."""
        return self.globals.get(name)
    
    def set_global(self, name: str, value: Any) -> None:
        """Set global variable."""
        self.globals[name] = value


class GDLangVMRuntime:
    """Wrapper to match ScriptRuntime protocol."""
    language = "gdlang_vm"
    
    def __init__(self):
        pass
    
    def execute(self, source: str, context) -> Any:
        """Execute gdlang source using VM."""
        from engine.scripting.gdlang.lexer import Lexer
        from engine.scripting.gdlang.parser import Parser, ParseError
        from engine.scripting.gdlang.compiler import compile_ast
        
        # Compile
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        try:
            statements = parser.parse()
        except ParseError as e:
            print(f"Parse Error: {e}")
            return None
        
        compiled = compile_ast(statements)
        
        # Execute
        vm = VM(target_node=context.node if hasattr(context, 'node') else None)
        
        # Set up initial globals from context
        if hasattr(context, 'properties'):
            for k, v in context.properties.items():
                vm.set_global(k, v)
        
        result = vm.run(compiled)
         
        # Copy globals back to context and collect user-defined variables
        user_vars = {}
        if hasattr(context, 'properties'):
            for k in list(vm.globals.keys()):
                if k not in ['print', 'Vector2', 'Color', 'Rect2', 'self']:
                    value = vm.get_global(k)
                    context.properties[k] = value
                    user_vars[k] = value
         
        return user_vars if user_vars else result
