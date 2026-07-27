from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class PubsubWatcherSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARI2_WATCHER_PUBSUB_",
        extra="ignore",
    )

    google_auth_settings_key: str | None = None
    project_id: str = ""
    subscription_id: str = ""
    max_messages: int = 1
    timeout: float = 60.0


settings_manager = SettingsManager(PubsubWatcherSettings)
