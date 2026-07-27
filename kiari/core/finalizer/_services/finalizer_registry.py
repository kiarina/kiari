from typing import Any

from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._settings import settings_manager
from .._types.finalizer import Finalizer


def _factory_wrapper(
    factory: ComponentFactory[Finalizer],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> Finalizer:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance


finalizer_registry = ComponentRegistry[Finalizer](
    expected_type=Finalizer,
    component_label="Finalizer",
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
