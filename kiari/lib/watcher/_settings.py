from kiarina.utils.common import ImportPath
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from ._types.watcher_name import WatcherName


class WatcherSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARI2_WATCHER_",
        extra="ignore",
    )

    presets: dict[WatcherName, ImportPath] = Field(
        default_factory=lambda: {
            "file": "kiari.impl.watcher_impl.file:create_file_watcher",
            "pubsub": "kiari.impl.watcher_impl.pubsub:create_pubsub_watcher",
            "rtdb": "kiari.impl.watcher_impl.rtdb:create_rtdb_watcher",
            "slack": "kiari.impl.watcher_impl.slack:create_slack_watcher",
        }
    )

    customs: dict[WatcherName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(WatcherSettings)
