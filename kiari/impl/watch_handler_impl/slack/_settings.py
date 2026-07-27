from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsKey, SettingsManager


class SlackWatchHandlerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARI2_WATCH_HANDLER_SLACK_",
        extra="ignore",
    )

    slack_settings_key: SettingsKey | None = None
    is_multi_workspace: bool = False
    file_installation_store_base_dir: str | None = None
    team_id: str = ""
    channel_id: str = ""
    thread_ts: str = ""


settings_manager = SettingsManager(SlackWatchHandlerSettings)
