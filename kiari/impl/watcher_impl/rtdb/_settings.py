from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsKey, SettingsManager


class RTDBWatcherSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARI2_WATCHER_RTDB_",
        extra="ignore",
    )

    firebase_settings_key: SettingsKey | None = None
    database_url: str = ""
    path: str = "/"


settings_manager = SettingsManager(RTDBWatcherSettings)
