from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._services.gui import gui

__all__ = ["gui"]


def __getattr__(name: str) -> object:
    if name not in __all__:
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        "gui": "._services.gui",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
