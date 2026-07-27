from typing import Any

from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._settings import settings_manager
from .._types.schedule_handler import ScheduleHandler


def _factory_wrapper(
    factory: ComponentFactory[ScheduleHandler],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> ScheduleHandler:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance


schedule_handler_registry = ComponentRegistry[ScheduleHandler](
    expected_type=ScheduleHandler,
    component_label="ScheduleHandler",
    get_default=lambda: settings_manager.settings.default,
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
