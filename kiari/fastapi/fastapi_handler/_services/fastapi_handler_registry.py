from typing import Any

from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._settings import settings_manager
from .._types.fastapi_handler import FastAPIHandler


def _factory_wrapper(
    factory: ComponentFactory[FastAPIHandler],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> FastAPIHandler:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance


fastapi_handler_registry = ComponentRegistry[FastAPIHandler](
    expected_type=FastAPIHandler,
    component_label="FastAPIHandler",
    get_default=lambda: settings_manager.settings.default,
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
