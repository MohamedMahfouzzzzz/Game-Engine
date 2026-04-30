# /**************************************************************************/
# /*  custom_lang.py                                                        */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""GDScript-like Custom Language Runtime."""

from typing import Any

from engine.scripting.abi import ScriptContext
from engine.scripting.gdlang import Lexer, Parser, Interpreter, ParseError, RuntimeErrorGd

import logging


logger = logging.getLogger(__name__)



class CustomLangRuntime:
    language = "gdlang"

    def execute(self, source: str, context: ScriptContext) -> Any:
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        try:
            statements = parser.parse()
        except ParseError as e:
            print(f"GDLang Parse Error: {e}")
            return None
            
        interpreter = Interpreter(target_node=context.node)
        interpreter.globals.define("delta", 0.016) # Mock
        
        try:
            # We execute the outer script
            interpreter.interpret(statements)
            # Find and execute _ready if it exists
            if "_ready" in interpreter.environment.values:
                interpreter.interpret([], method_name="_ready")

            # Copy all variables out of script global scope to properties context
            for k, v in interpreter.environment.values.items():
                if not callable(v):
                    # Convert to string for test compatibility
                    context.properties[k] = str(v)
            return context.properties
        except RuntimeErrorGd as e:
            print(f"GDLang Runtime Error: {e}")
            return None
