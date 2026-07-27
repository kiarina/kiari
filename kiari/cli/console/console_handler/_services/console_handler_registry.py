from typing import Any

from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._settings import settings_manager
from .._types.console_handler import ConsoleHandler


def _factory_wrapper(
    factory: ComponentFactory[ConsoleHandler],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> ConsoleHandler:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance


console_handler_registry = ComponentRegistry[ConsoleHandler](
    expected_type=ConsoleHandler,
    component_label="ConsoleHandler",
    get_default=lambda: settings_manager.settings.default,
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
