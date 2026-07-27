from typing import Any

from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._settings import settings_manager
from .._types.watcher import Watcher


def _factory_wrapper(
    factory: ComponentFactory[Watcher],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> Watcher:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance


watcher_registry = ComponentRegistry[Watcher](
    expected_type=Watcher,
    component_label="Watcher",
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
