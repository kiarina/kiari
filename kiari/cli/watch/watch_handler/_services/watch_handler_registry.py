from typing import Any

from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._settings import settings_manager
from .._types.watch_handler import WatchHandler


def _factory_wrapper(
    factory: ComponentFactory[WatchHandler],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> WatchHandler:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance


watch_handler_registry = ComponentRegistry[WatchHandler](
    expected_type=WatchHandler,
    component_label="WatchHandler",
    get_default=lambda: settings_manager.settings.default,
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
