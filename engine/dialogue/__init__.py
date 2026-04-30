# /**************************************************************************/
# /*  dialogue/__init__.py                                                  */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Dialogue system for nonlinear branching conversations.

Similar to Godot Dialogue Manager, supports:
- Branching dialogue with choices
- Conditions and variables
- Game integration (method calls, signals)
- BBCode text formatting
- Audio/voice integration
- Translations
"""

from engine.dialogue.lexer import DialogueLexer, DialogueToken, DialogueTokenType
from engine.dialogue.parser import DialogueParser, DialogueParseError
from engine.dialogue.runtime import DialogueRuntime, DialogueState
from engine.dialogue.translations import TranslationManager

import logging


logger = logging.getLogger(__name__)


__all__ = [
    "DialogueLexer", "DialogueToken", "DialogueTokenType",
    "DialogueParser", "DialogueParseError",
    "DialogueRuntime", "DialogueState",
    "TranslationManager",
]
