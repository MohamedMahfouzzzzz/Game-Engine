# /**************************************************************************/
# /*  ast_nodes.py                                                          */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""AST node definitions for the custom GDScript-like language."""

from dataclasses import dataclass
from typing import List, Optional, Any

import logging


logger = logging.getLogger(__name__)


class ASTNode:
    pass

class Expression(ASTNode):
    pass

class Statement(ASTNode):
    pass

@dataclass
class LiteralEx(Expression):
    value: Any

@dataclass
class IdentifierEx(Expression):
    name: str

@dataclass
class BinaryOpEx(Expression):
    left: Expression
    operator: str
    right: Expression

@dataclass
class UnaryOpEx(Expression):
    operator: str
    right: Expression

@dataclass
class CallEx(Expression):
    callee: Expression
    arguments: List[Expression]

@dataclass
class MemberAccessEx(Expression):
    object: Expression
    member: str

@dataclass
class IndexAccessEx(Expression):
    object: Expression
    index: Expression

@dataclass
class VarDeclSt(Statement):
    name: str
    is_export: bool
    is_const: bool
    initializer: Optional[Expression]
    on_ready: bool = False

@dataclass
class AssignSt(Statement):
    target: Expression
    operator: str  # '=', '+=', etc
    value: Expression

@dataclass
class ExpressionSt(Statement):
    expression: Expression

@dataclass
class ReturnSt(Statement):
    value: Optional[Expression]

@dataclass
class IfSt(Statement):
    condition: Expression
    then_branch: List[Statement]
    elifs: List['ElifBranch']
    else_branch: Optional[List[Statement]]

@dataclass
class ElifBranch:
    condition: Expression
    body: List[Statement]

@dataclass
class ForSt(Statement):
    iterator_name: str
    iterable: Expression
    body: List[Statement]

@dataclass
class WhileSt(Statement):
    condition: Expression
    body: List[Statement]

@dataclass
class FuncDefSt(Statement):
    name: str
    params: List[str]
    body: List[Statement]

@dataclass
class SignalDeclSt(Statement):
    name: str
    params: List[str]

@dataclass
class ClassDeclSt(Statement):
    extends_type: str
    body: List[Statement]
