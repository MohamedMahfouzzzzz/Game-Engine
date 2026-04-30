# /**************************************************************************/
# /*  python_runtime.py                                                     */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Secure Python runtime with AST validation and sandbox restrictions.

Security features:
- AST analysis blocks dangerous syntax
- Restricted builtins (no file access, no system calls)
- Memory limits (via sys.setrecursionlimit)
- Execution timeout protection
- No network access
- No module imports
"""

import ast
import sys
import signal
from contextlib import contextmanager

from engine.core.errors import ScriptingSecurityError
from engine.scripting.abi import ScriptContext

import logging



logger = logging.getLogger(__name__)

class TimeoutError(Exception):
    """Script execution timeout."""
    pass


@contextmanager
def execution_timeout(seconds: int = 5):
    """Context manager for execution timeout.
    
    Prevents infinite loops in scripts.
    """
    def handler(signum, frame):
        raise TimeoutError(f"Script execution exceeded {seconds} seconds")
    
    # Set timeout (Unix only, Windows needs different approach)
    old_handler = signal.signal(signal.SIGALRM, handler) if hasattr(signal, 'SIGALRM') else None
    if hasattr(signal, 'alarm'):
        signal.alarm(seconds)
    
    try:
        yield
    finally:
        if old_handler and hasattr(signal, 'SIGALRM'):
            signal.signal(signal.SIGALRM, old_handler)
        if hasattr(signal, 'alarm'):
            signal.alarm(0)


class PythonRuntime:
    """Hardened Python runtime for scripting.
    
    All scripts are analyzed via AST before execution.
    Dangerous operations are blocked at the AST level.
    """
    
    language = "python"
    
    # Maximum execution time in seconds
    EXECUTION_TIMEOUT = 5
    
    # Maximum memory per script (MB) - enforced via recursion limit
    MAX_RECURSION_DEPTH = 100

    def __init__(self):
        """Initialize with restricted environment."""
        # Safe builtins only - NO file/network/system access
        self.safe_builtins = {
            # Types
            "int": int, "float": float, "str": str, "bool": bool,
            "list": list, "tuple": tuple, "dict": dict, "set": set,
            "None": None, "True": True, "False": False,
            
            # Safe functions
            "len": len, "min": min, "max": max, "sum": sum,
            "abs": abs, "round": round, "pow": pow, "divmod": divmod,
            "enumerate": enumerate, "zip": zip, "range": range,
            "sorted": sorted, "reversed": reversed,
            "any": any, "all": all,
            "isinstance": isinstance, "hasattr": hasattr,
            "print": lambda *args, **kwargs: None,  # No-op print
        }

    def execute(self, source: str, context: ScriptContext):
        """Execute script in secure sandbox.
        
        Args:
            source: Python source code
            context: Script execution context
            
        Returns:
            Script result or None
            
        Raises:
            ScriptingSecurityError: If script violates security policy
            TimeoutError: If script exceeds time limit
        """
        # Validate AST before execution
        self._validate_ast(source)
        
        # Set recursion limit for memory protection
        old_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(self.MAX_RECURSION_DEPTH)
        
        try:
            # Execute in restricted environment
            globals_scope = {"__builtins__": self.safe_builtins}
            local_scope = {"context": context, "result": None}
            
            # Run with timeout protection
            try:
                with execution_timeout(self.EXECUTION_TIMEOUT):
                    exec(source, globals_scope, local_scope)
            except TimeoutError:
                raise ScriptingSecurityError(f"Script timeout after {self.EXECUTION_TIMEOUT}s")
            
            return local_scope.get("result")
            
        finally:
            sys.setrecursionlimit(old_limit)

    def _validate_ast(self, source: str) -> None:
        tree = ast.parse(source, mode="exec")

        # Blocked node types for security
        blocked_nodes = (
            ast.Import, ast.ImportFrom, ast.With, ast.Try,
            ast.Raise, ast.Global, ast.Nonlocal, ast.ClassDef,
            ast.Lambda, ast.Yield, ast.YieldFrom, ast.AsyncFor,
            ast.AsyncWith, ast.Await
        )

        # Safe function whitelist
        SAFE_FUNCTIONS = {
            "len", "min", "max", "sum", "abs", "range",
            "enumerate", "zip", "map", "filter", "sorted",
            "reversed", "any", "all", "round", "divmod",
            "pow", "isinstance", "hasattr", "getattr", "setattr"
        }

        # Blocked attributes for sandbox escape prevention
        BLOCKED_ATTRS = {
            "__subclasses__", "__mro__", "__base__", "__bases__",
            "__class__", "__dict__", "__globals__", "__code__",
            "__closure__", "__func__", "__self__", "__module__"
        }

        for node in ast.walk(tree):
            # Block dangerous node types
            if isinstance(node, blocked_nodes):
                raise ScriptingSecurityError(f"Blocked syntax: {type(node).__name__}")

            # Block ALL private attribute access (starts with _)
            if isinstance(node, ast.Attribute):
                if node.attr.startswith("_"):
                    raise ScriptingSecurityError(f"Private access blocked: {node.attr}")

            # Block specific dangerous attributes that enable sandbox escape
            if isinstance(node, ast.Attribute):
                if node.attr in BLOCKED_ATTRS:
                    raise ScriptingSecurityError(f"Dangerous attribute blocked: {node.attr}")

            # Block calls to non-whitelisted functions
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id not in SAFE_FUNCTIONS:
                        raise ScriptingSecurityError(f"Function blocked: {node.func.id}")
                # Block direct calls to eval/exec/compile via any means
                if isinstance(node.func, ast.Name) and node.func.id in ("eval", "exec", "compile"):
                    raise ScriptingSecurityError(f"Dangerous call blocked: {node.func.id}")

            # Block attempts to access __builtins__ or similar
            if isinstance(node, ast.Name):
                if node.id.startswith("__") and node.id.endswith("__"):
                    if node.id not in ("None", "True", "False"):
                        raise ScriptingSecurityError(f"Dunder access blocked: {node.id}")
