# /**************************************************************************/
# /*  bytecode.py                                                           */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Bytecode definitions for gdlang VM."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Any, Dict, Optional
from enum import Enum, auto

import logging



logger = logging.getLogger(__name__)

class OpCode(Enum):
    """Bytecode operation codes."""
    # Stack operations
    PUSH_CONST = auto()      # Push constant from constant pool
    PUSH_NULL = auto()       # Push null
    PUSH_TRUE = auto()       # Push true
    PUSH_FALSE = auto()      # Push false
    POP = auto()             # Pop value from stack
    DUP = auto()             # Duplicate top of stack
    SWAP = auto()            # Swap top two stack values
    
    # Variable operations
    LOAD_LOCAL = auto()      # Load local variable
    STORE_LOCAL = auto()     # Store to local variable
    LOAD_GLOBAL = auto()     # Load global variable
    STORE_GLOBAL = auto()    # Store to global variable
    LOAD_MEMBER = auto()     # Load member (obj.property)
    STORE_MEMBER = auto()    # Store to member
    
    # Arithmetic
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    MOD = auto()
    NEG = auto()             # Negate
    
    # Comparison
    EQ = auto()
    NEQ = auto()
    LT = auto()
    LE = auto()
    GT = auto()
    GE = auto()
    
    # Logical
    AND = auto()
    OR = auto()
    NOT = auto()
    
    # Control flow
    JUMP = auto()            # Unconditional jump
    JUMP_IF_FALSE = auto()   # Jump if top of stack is falsy
    JUMP_IF_TRUE = auto()    # Jump if top of stack is truthy
    CALL = auto()            # Call function
    CALL_MEMBER = auto()     # Call method on object
    RETURN = auto()          # Return from function
    
    # Collection
    BUILD_ARRAY = auto()     # Build array from stack values
    BUILD_DICT = auto()      # Build dictionary
    INDEX_GET = auto()       # Get item by index/key
    INDEX_SET = auto()       # Set item by index/key
    
    # Special
    EMIT_SIGNAL = auto()     # Emit a signal
    YIELD = auto()           # Yield/resume
    AWAIT = auto()           # Await async operation


@dataclass
class Instruction:
    """Single bytecode instruction."""
    opcode: OpCode
    operand: Any = None
    line: int = 0
    
    def __repr__(self) -> str:
        if self.operand is not None:
            return f"{self.opcode.name} {self.operand}"
        return self.opcode.name


@dataclass
class Chunk:
    """A chunk of bytecode (function or script)."""
    name: str
    instructions: List[Instruction] = field(default_factory=list)
    constants: List[Any] = field(default_factory=list)
    local_count: int = 0
    param_count: int = 0
    
    def add_const(self, value: Any) -> int:
        """Add constant to pool, return index."""
        # Check if constant already exists
        for i, c in enumerate(self.constants):
            if c == value:
                return i
        self.constants.append(value)
        return len(self.constants) - 1
    
    def write(self, opcode: OpCode, operand: Any = None, line: int = 0) -> None:
        """Write instruction to chunk."""
        self.instructions.append(Instruction(opcode, operand, line))
    
    def disassemble(self) -> str:
        """Disassemble chunk to readable format."""
        lines = [f"== {self.name} =="]
        for i, inst in enumerate(self.instructions):
            if inst.operand is not None:
                const_val = ""
                if inst.opcode == OpCode.PUSH_CONST:
                    const_val = f" [{self.constants[inst.operand]!r}]"
                lines.append(f"{i:04d}  {inst.opcode.name:15} {inst.operand}{const_val}")
            else:
                lines.append(f"{i:04d}  {inst.opcode.name}")
        return "\n".join(lines)


@dataclass
class CompiledScript:
    """Fully compiled script with main chunk and functions."""
    main_chunk: Chunk
    functions: Dict[str, Chunk] = field(default_factory=dict)
    classes: Dict[str, Any] = field(default_factory=dict)
    signals: Dict[str, List[str]] = field(default_factory=dict)
    exports: List[str] = field(default_factory=list)
    onready: List[str] = field(default_factory=list)
