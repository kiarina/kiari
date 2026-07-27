from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class LocalHistoryRepositorySettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARI2_CORE_HISTORY_REPOSITORY_LOCAL_",
        extra="ignore",
    )

    file_name: str = "history.json"


settings_manager = SettingsManager(LocalHistoryRepositorySettings)
