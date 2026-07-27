from typing import Any

from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._settings import settings_manager
from .._types.web import Web


def _factory_wrapper(
    factory: ComponentFactory[Web],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> Web:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance


web_registry = ComponentRegistry[Web](
    expected_type=Web,
    component_label="Web",
    get_default=lambda: settings_manager.settings.default,
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
