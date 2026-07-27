from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsKey, SettingsManager


class SlackWatcherSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARI2_WATCHER_SLACK_",
        extra="ignore",
    )

    slack_settings_key: SettingsKey | None = None
    channel_ids: list[str] = Field(default_factory=list)
    require_mention_in_channels: bool = False
    max_file_size_mb: float = 10.0
    is_multi_workspace: bool = False
    oauth_server_host: str = "0.0.0.0"
    oauth_server_port: int = 3000
    file_installation_store_base_dir: str | None = None
    attachment_dir: str | None = None

    @field_validator("channel_ids", mode="before")
    @classmethod
    def _parse_channel_ids(cls, value: Any) -> Any:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]

        return value


settings_manager = SettingsManager(SlackWatcherSettings)
