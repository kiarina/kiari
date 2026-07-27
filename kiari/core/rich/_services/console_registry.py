from typing import Any

from kiarina.utils.object_registry import ObjectRegistry
from rich.console import Console


def _factory(name: str, config: dict[str, Any]) -> Console:
    return Console(**config)


console_registry = ObjectRegistry[Console, dict[str, Any]](
    expected_type=Console,
    object_label="Console",
    get_default=lambda: "default",
    get_presets=lambda: {
        "default": {"stderr": True, "highlight": False},
    },
    factory=_factory,
)
