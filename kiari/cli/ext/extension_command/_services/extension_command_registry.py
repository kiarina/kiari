from typing import Any

from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._settings import settings_manager
from .._types.extension_command import ExtensionCommand


def _factory_wrapper(
    factory: ComponentFactory[ExtensionCommand],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> ExtensionCommand:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance


extension_command_registry = ComponentRegistry[ExtensionCommand](
    expected_type=ExtensionCommand,
    component_label="ExtensionCommand",
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
