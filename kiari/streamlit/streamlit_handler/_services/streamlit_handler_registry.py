from typing import Any

from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._settings import settings_manager
from .._types.streamlit_handler import StreamlitHandler


def _factory_wrapper(
    factory: ComponentFactory[StreamlitHandler],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> StreamlitHandler:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance


streamlit_handler_registry = ComponentRegistry[StreamlitHandler](
    expected_type=StreamlitHandler,
    component_label="StreamlitHandler",
    get_default=lambda: settings_manager.settings.default,
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
