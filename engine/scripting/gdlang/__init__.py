# /**************************************************************************/
# /*  __init__.py                                                           */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""GDScript-like Custom Language package."""

from engine.scripting.gdlang.lexer import Lexer, Token, TokenType
from engine.scripting.gdlang.parser import Parser, ParseError
from engine.scripting.gdlang.interpreter import Interpreter, RuntimeErrorGd
from engine.scripting.gdlang.compiler import compile_ast, Compiler, CompileError
from engine.scripting.gdlang.vm import VM, VMError, GDLangVMRuntime
from engine.scripting.gdlang.bytecode import (
    OpCode, Chunk, CompiledScript, Instruction
)
import logging

logger = logging.getLogger(__name__)

from engine.scripting.gdlang.type_system import (
    # 2D Types
    Vector2, Vector2i,
    # Rectangle Types
    Rect2, Rect2i,
    # Color Type
    Color,
    # Transform Types
    Transform2D,
    # Array Types
    Array, Dict,
    # String Types
    StringName, NodePath,
    # Callable & Signal
    Callable, Signal,
    # Packed Arrays
    PackedByteArray,
    PackedInt32Array,
    PackedFloat32Array,
    PackedStringArray,
    PackedVector2Array,
    PackedColorArray,
    # RID
    RID,
)

__all__ = [
    # Lexer & Parser
    "Lexer", "Token", "TokenType",
    "Parser", "ParseError",
    # Interpreter & Compiler
    "Interpreter", "RuntimeErrorGd",
    "compile_ast", "Compiler", "CompileError",
    # VM
    "VM", "VMError", "GDLangVMRuntime",
    # Bytecode
    "OpCode", "Chunk", "CompiledScript", "Instruction",
    # 2D Types
    "Vector2", "Vector2i",
    # Rectangle Types
    "Rect2", "Rect2i",
    # Color Type
    "Color",
    # Transform Types
    "Transform2D",
    # Array Types
    "Array", "Dict",
    # String Types
    "StringName", "NodePath",
    # Callable & Signal
    "Callable", "Signal",
    # Packed Arrays
    "PackedByteArray",
    "PackedInt32Array",
    "PackedFloat32Array",
    "PackedStringArray",
    "PackedVector2Array",
    "PackedColorArray",
    # RID
    "RID",
]
