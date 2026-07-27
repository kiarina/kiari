# Depends on pyautogui and pyperclip.
# pyautogui is imported when Keyboard.press or Keyboard.hotkey is executed.
# pyperclip is imported when Keyboard.write is executed.
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._models.keyboard import Keyboard
    from ._types.keyboard_key import KeyboardKey

__all__ = [
    # ._models
    "Keyboard",
    # ._types
    "KeyboardKey",
]


def __getattr__(name: str) -> object:
    if name not in __all__:
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._models
        "Keyboard": "._models.keyboard",
        # ._types
        "KeyboardKey": "._types.keyboard_key",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
