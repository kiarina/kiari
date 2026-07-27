from typing import Any

from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._settings import settings_manager
from .._types.slash_command import SlashCommand


def _factory_wrapper(
    factory: ComponentFactory[SlashCommand],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> SlashCommand:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance


slash_command_registry = ComponentRegistry[SlashCommand](
    expected_type=SlashCommand,
    component_label="SlashCommand",
    get_aliases=lambda: settings_manager.settings.aliases,
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
