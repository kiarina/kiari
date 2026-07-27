from typing import Literal

Action = Literal[
    "keyboard_press",
    "keyboard_hotkey",
    "keyboard_write",
    "mouse_click",
    "mouse_down",
    "mouse_move",
    "mouse_up",
    "screenshot",
]
