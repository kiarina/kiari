from kiarina.utils.common import ImportPath
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from ._types.extension_command_name import ExtensionCommandName


class ExtensionCommandSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARI_EXT_COMMAND_",
        extra="ignore",
    )

    presets: dict[ExtensionCommandName, ImportPath] = Field(default_factory=dict)

    customs: dict[ExtensionCommandName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(ExtensionCommandSettings)
