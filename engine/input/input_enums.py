# /**************************************************************************/
# /*  input_enums.py                                                        */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Godot Engine Input System Enums - Python Port

All input-related enums from Godot Engine, ported to Python.
Maintains exact enum values for compatibility.
"""

from enum import Enum, auto, IntEnum
from typing import Dict, List


# =============================================================================
# Joypad Buttons (26 buttons total)
# =============================================================================

class JoyButton(IntEnum):
    """Standard SDL game controller buttons."""
    A = 0
    B = 1
    X = 2
    Y = 3
    BACK = 4
    GUIDE = 5
    START = 6
    LEFT_STICK = 7
    RIGHT_STICK = 8
    LEFT_SHOULDER = 9
    RIGHT_SHOULDER = 10
    DPAD_UP = 11
    DPAD_DOWN = 12
    DPAD_LEFT = 13
    DPAD_RIGHT = 14
    MISC1 = 15
    PADDLE1 = 16
    PADDLE2 = 17
    PADDLE3 = 18
    PADDLE4 = 19
    TOUCHPAD = 20
    MISC2 = 21
    MISC3 = 22
    MISC4 = 23
    MISC5 = 24
    MISC6 = 25
    
    # Aliases for common button names
    CROSS = A
    CIRCLE = B
    SQUARE = X
    TRIANGLE = Y
    
    # Special values
    INVALID = -1
    MAX = 26
    SDL_MAX = 26


# =============================================================================
# Joypad Axes (6 axes total)
# =============================================================================

class JoyAxis(IntEnum):
    """Standard SDL game controller axes."""
    LEFT_X = 0
    LEFT_Y = 1
    RIGHT_X = 2
    RIGHT_Y = 3
    TRIGGER_LEFT = 4
    TRIGGER_RIGHT = 5
    
    # Special values
    INVALID = -1
    MAX = 6
    SDL_MAX = 6


# =============================================================================
# Joypad Hat Directions
# =============================================================================

class HatMask(IntEnum):
    """Hat/D-pad direction bitmasks."""
    CENTER = 0
    UP = 1
    RIGHT = 2
    DOWN = 4
    LEFT = 8


class HatDir(IntEnum):
    """Hat direction indices."""
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3
    MAX = 4


# =============================================================================
# Mouse Modes
# =============================================================================

class MouseMode(IntEnum):
    """Mouse visibility/capture modes."""
    VISIBLE = 0
    HIDDEN = 1
    CAPTURED = 2
    CONFINED = 3
    CONFINED_HIDDEN = 4
    MAX = 5


# =============================================================================
# Mouse Buttons
# =============================================================================

class MouseButton(IntEnum):
    """Standard mouse buttons."""
    NONE = 0
    LEFT = 1
    RIGHT = 2
    MIDDLE = 3
    WHEEL_UP = 4
    WHEEL_DOWN = 5
    WHEEL_LEFT = 6
    WHEEL_RIGHT = 7
    XBUTTON1 = 8
    XBUTTON2 = 9


class MouseButtonMask(IntEnum):
    """Mouse button bitmasks for combined states."""
    NONE = 0
    LEFT = 1
    RIGHT = 2
    MIDDLE = 4
    WHEEL_UP = 8
    WHEEL_DOWN = 16
    WHEEL_LEFT = 32
    WHEEL_RIGHT = 64
    XBUTTON1 = 128
    XBUTTON2 = 256


# =============================================================================
# Cursor Shapes
# =============================================================================

class CursorShape(IntEnum):
    """Standard cursor shapes."""
    ARROW = 0
    IBEAM = 1
    POINTING_HAND = 2
    CROSS = 3
    WAIT = 4
    BUSY = 5
    DRAG = 6
    CAN_DROP = 7
    FORBIDDEN = 8
    VSIZE = 9
    HSIZE = 10
    BDIAGSIZE = 11
    FDIAGSIZE = 12
    MOVE = 13
    VSPLIT = 14
    HSPLIT = 15
    HELP = 16
    MAX = 17


# =============================================================================
# Keyboard Keys
# =============================================================================

class Key(IntEnum):
    """Keyboard key codes (Godot/GDK keycodes)."""
    NONE = 0
    
    # Special keys
    ESCAPE = 16777217
    TAB = 16777218
    BACKSPACE = 16777219
    ENTER = 16777220
    INSERT = 16777221
    DELETE = 16777222
    PAUSE = 16777223
    PRINT = 16777224
    SYSREQ = 16777225
    CLEAR = 16777226
    HOME = 16777229
    END = 16777230
    LEFT = 16777231
    UP = 16777232
    RIGHT = 16777233
    DOWN = 16777234
    PAGEUP = 16777235
    PAGEDOWN = 16777236
    SHIFT = 16777237
    CONTROL = 16777238
    META = 16777239
    ALT = 16777240
    CAPSLOCK = 16777241
    NUMLOCK = 16777242
    SCROLLLOCK = 16777243
    F1 = 16777244
    F2 = 16777245
    F3 = 16777246
    F4 = 16777247
    F5 = 16777248
    F6 = 16777249
    F7 = 16777250
    F8 = 16777251
    F9 = 16777252
    F10 = 16777253
    F11 = 16777254
    F12 = 16777255
    F13 = 16777256
    F14 = 16777257
    F15 = 16777258
    F16 = 16777259
    F17 = 16777260
    F18 = 16777261
    F19 = 16777262
    F20 = 16777263
    F21 = 16777264
    F22 = 16777265
    F23 = 16777266
    F24 = 16777267
    F25 = 16777268
    F26 = 16777269
    F27 = 16777270
    F28 = 16777271
    F29 = 16777272
    F30 = 16777273
    F31 = 16777274
    F32 = 16777275
    F33 = 16777276
    F34 = 16777277
    F35 = 16777278
    
    # Numpad
    KP_ENTER = 16777280
    KP_MULTIPLY = 16777281
    KP_DIVIDE = 16777282
    KP_SUBTRACT = 16777283
    KP_PERIOD = 16777284
    KP_ADD = 16777285
    KP_0 = 16777286
    KP_1 = 16777287
    KP_2 = 16777288
    KP_3 = 16777289
    KP_4 = 16777290
    KP_5 = 16777291
    KP_6 = 16777292
    KP_7 = 16777293
    KP_8 = 16777294
    KP_9 = 16777295
    
    # Media keys
    MEDIA_PLAY = 16777296
    MEDIA_STOP = 16777297
    MEDIA_PREVIOUS = 16777298
    MEDIA_NEXT = 16777299
    MEDIA_RECORD = 16777300
    VOLUME_DOWN = 16777301
    VOLUME_UP = 16777302
    MUTE = 16777303
    
    # ASCII/Unicode keys (simplified)
    SPACE = 32
    EXCLAM = 33
    QUOTEDBL = 34
    NUMBERSIGN = 35
    DOLLAR = 36
    PERCENT = 37
    AMPERSAND = 38
    APOSTROPHE = 39
    PARENLEFT = 40
    PARENRIGHT = 41
    ASTERISK = 42
    PLUS = 43
    COMMA = 44
    MINUS = 45
    PERIOD = 46
    SLASH = 47
    KEY_0 = 48
    KEY_1 = 49
    KEY_2 = 50
    KEY_3 = 51
    KEY_4 = 52
    KEY_5 = 53
    KEY_6 = 54
    KEY_7 = 55
    KEY_8 = 56
    KEY_9 = 57
    COLON = 58
    SEMICOLON = 59
    LESS = 60
    EQUAL = 61
    GREATER = 62
    QUESTION = 63
    AT = 64
    A = 65
    B = 66
    C = 67
    D = 68
    E = 69
    F = 70
    G = 71
    H = 72
    I = 73
    J = 74
    K = 75
    L = 76
    M = 77
    N = 78
    O = 79
    P = 80
    Q = 81
    R = 82
    S = 83
    T = 84
    U = 85
    V = 86
    W = 87
    X = 88
    Y = 89
    Z = 90
    BRACKETLEFT = 91
    BACKSLASH = 92
    BRACKETRIGHT = 93
    ASCIICIRCUM = 94
    UNDERSCORE = 95
    QUOTELEFT = 96
    BRACELEFT = 123
    BAR = 124
    BRACERIGHT = 125
    ASCIITILDE = 126


# =============================================================================
# Input Event Types
# =============================================================================

class InputEventType(IntEnum):
    """Types of input events."""
    NONE = 0
    KEY = 1
    MOUSE_BUTTON = 2
    MOUSE_MOTION = 3
    SCREEN_TOUCH = 4
    SCREEN_DRAG = 5
    JOY_BUTTON = 6
    JOY_MOTION = 7
    GESTURE = 8
    ACTION = 9
    MAX = 10


# =============================================================================
# Joypad Axis Range
# =============================================================================

class JoyAxisRange(IntEnum):
    """Range types for axis mapping."""
    FULL_AXIS = 0
    POSITIVE_HALF_AXIS = 1
    NEGATIVE_HALF_AXIS = 2


# =============================================================================
# Joypad Event Types
# =============================================================================

class JoyEventType(IntEnum):
    """Types of joypad events in mapping."""
    NONE = 0
    BUTTON = 1
    AXIS = 2
    HAT = 3


# =============================================================================
# Device Constants
# =============================================================================

class InputConstants:
    """Input system constants."""
    JOYPADS_MAX = 16
    MAX_EVENT = 32
    DEVICE_ID_EMULATION = -1
    DEVICE_ID_INTERNAL = -2
    STANDARD_GRAVITY = 9.80665


# =============================================================================
# Joypad Button Names (for mapping database)
# =============================================================================

JOY_BUTTON_NAMES: Dict[JoyButton, str] = {
    JoyButton.A: "a",
    JoyButton.B: "b",
    JoyButton.X: "x",
    JoyButton.Y: "y",
    JoyButton.BACK: "back",
    JoyButton.GUIDE: "guide",
    JoyButton.START: "start",
    JoyButton.LEFT_STICK: "leftstick",
    JoyButton.RIGHT_STICK: "rightstick",
    JoyButton.LEFT_SHOULDER: "leftshoulder",
    JoyButton.RIGHT_SHOULDER: "rightshoulder",
    JoyButton.DPAD_UP: "dpup",
    JoyButton.DPAD_DOWN: "dpdown",
    JoyButton.DPAD_LEFT: "dpleft",
    JoyButton.DPAD_RIGHT: "dpright",
    JoyButton.MISC1: "misc1",
    JoyButton.PADDLE1: "paddle1",
    JoyButton.PADDLE2: "paddle2",
    JoyButton.PADDLE3: "paddle3",
    JoyButton.PADDLE4: "paddle4",
    JoyButton.TOUCHPAD: "touchpad",
    JoyButton.MISC2: "misc2",
    JoyButton.MISC3: "misc3",
    JoyButton.MISC4: "misc4",
    JoyButton.MISC5: "misc5",
    JoyButton.MISC6: "misc6",
}

JOY_AXIS_NAMES: Dict[JoyAxis, str] = {
    JoyAxis.LEFT_X: "leftx",
    JoyAxis.LEFT_Y: "lefty",
    JoyAxis.RIGHT_X: "rightx",
    JoyAxis.RIGHT_Y: "righty",
    JoyAxis.TRIGGER_LEFT: "lefttrigger",
    JoyAxis.TRIGGER_RIGHT: "righttrigger",
}


# =============================================================================
# Reverse lookup for parsing
# =============================================================================

JOY_BUTTON_NAME_TO_ENUM: Dict[str, JoyButton] = {v: k for k, v in JOY_BUTTON_NAMES.items()}
JOY_AXIS_NAME_TO_ENUM: Dict[str, JoyAxis] = {v: k for k, v in JOY_AXIS_NAMES.items()}
