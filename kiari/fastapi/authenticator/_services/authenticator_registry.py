from kiarina.utils.component_registry import ComponentRegistry

from .._settings import settings_manager
from .._types.authenticator import Authenticator

authenticator_registry = ComponentRegistry[Authenticator](
    expected_type=Authenticator,
    component_label="Authenticator",
    get_default=lambda: settings_manager.settings.default,
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
)
