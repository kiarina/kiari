# Depends on pyautogui.
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._models.mouse import Mouse
    from ._types.mouse_button import MouseButton

__all__ = [
    # ._models
    "Mouse",
    # ._types
    "MouseButton",
]


def __getattr__(name: str) -> object:
    if name not in __all__:
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._models
        "Mouse": "._models.mouse",
        # ._types
        "MouseButton": "._types.mouse_button",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
