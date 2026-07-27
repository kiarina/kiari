# Depends on mss and Pillow.
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._models.monitor import Monitor
    from ._schemas.monitor_snapshot import MonitorSnapshot
    from ._schemas.multiple_monitor_capture import MultipleMonitorCapture
    from ._schemas.point import Point
    from ._schemas.rect import Rect
    from ._schemas.size import Size
    from ._types.monitor_index import MonitorIndex
    from ._views.monitor_info import MonitorInfo

__all__ = [
    # ._models
    "Monitor",
    # ._schemas
    "MonitorSnapshot",
    "MultipleMonitorCapture",
    "Point",
    "Rect",
    "Size",
    # ._types
    "MonitorIndex",
    # ._views
    "MonitorInfo",
]


def __getattr__(name: str) -> object:
    if name not in __all__:
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._models
        "Monitor": "._models.monitor",
        # ._schemas
        "MonitorSnapshot": "._schemas.monitor_snapshot",
        "MultipleMonitorCapture": "._schemas.multiple_monitor_capture",
        "Point": "._schemas.point",
        "Rect": "._schemas.rect",
        "Size": "._schemas.size",
        # ._types
        "MonitorIndex": "._types.monitor_index",
        # ._views
        "MonitorInfo": "._views.monitor_info",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
