from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_chrome_bridge import create_chrome_bridge
    from ._settings import ChromeSettings, settings_manager

__all__ = ["create_chrome_bridge", "ChromeSettings", "settings_manager"]


def __getattr__(name: str) -> object:
    if name not in __all__:
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        "create_chrome_bridge": "._helpers.create_chrome_bridge",
        "ChromeSettings": "._settings",
        "settings_manager": "._settings",
    }
    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
