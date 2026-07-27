from typing import Any

from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._settings import settings_manager
from .._types.streamlit_authenticator import StreamlitAuthenticator


def _factory_wrapper(
    factory: ComponentFactory[StreamlitAuthenticator],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> StreamlitAuthenticator:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance


streamlit_authenticator_registry = ComponentRegistry[StreamlitAuthenticator](
    expected_type=StreamlitAuthenticator,
    component_label="StreamlitAuthenticator",
    get_default=lambda: settings_manager.settings.default,
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
