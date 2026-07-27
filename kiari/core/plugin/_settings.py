from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class PluginSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARI_PLUGIN_",
        extra="ignore",
    )

    module_prefix: str = "kiari_plugin"


settings_manager = SettingsManager(PluginSettings)
