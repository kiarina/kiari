from typing import Any

from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._settings import settings_manager
from .._types.batch_handler import BatchHandler


def _factory_wrapper(
    factory: ComponentFactory[BatchHandler],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> BatchHandler:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance


batch_handler_registry = ComponentRegistry[BatchHandler](
    expected_type=BatchHandler,
    component_label="BatchHandler",
    get_default=lambda: settings_manager.settings.default,
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
