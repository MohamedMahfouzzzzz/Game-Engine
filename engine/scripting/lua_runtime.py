# /**************************************************************************/
# /*  lua_runtime.py                                                        */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

from engine.scripting.abi import ScriptContext
from engine.scripting.external_runtime import run_lua

import logging


logger = logging.getLogger(__name__)



class LuaRuntime:
    language = "lua"

    def execute(self, source: str, context: ScriptContext):
        return run_lua(source, context)
