from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kiarina.agi.agent import BaseAgent as Agent

__all__ = [
    # --------------------------------------------------
    # kiarina_agi
    # --------------------------------------------------
    # kiarina.agi.agent
    "Agent",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    # Map attribute names to their module paths
    # Format: "name": "module_path" or "name": ("module_path", "attr_name")
    # fmg: off
    module_map: dict[str, str | tuple[str, str]] = {
        # --------------------------------------------------
        # kiarina_agi
        # --------------------------------------------------
        # kiarina.agi.agent
        "Agent": ("kiarina.agi.agent", "BaseAgent"),
    }
    # fmt: on

    module_info = module_map[name]

    if isinstance(module_info, tuple):
        # Tuple format: (module_path, attr_name)
        module_path, attr_name = module_info
        module = import_module(module_path)
        attr = getattr(module, attr_name)
    else:
        # String format: module_path (attr_name is the same as name)
        module_path = module_info
        module = import_module(module_path)
        attr = getattr(module, name)

    globals()[name] = attr
    return attr
