from typing import Any

from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._settings import settings_manager
from .._types.history_repository import HistoryRepository


def _factory_wrapper(
    factory: ComponentFactory[HistoryRepository],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> HistoryRepository:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance


history_repository_registry = ComponentRegistry[HistoryRepository](
    expected_type=HistoryRepository,
    component_label="HistoryRepository",
    get_default=lambda: settings_manager.settings.default,
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
