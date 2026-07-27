from kiarina.utils.common import ImportPath
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from ._types.watch_handler_name import WatchHandlerName
from ._types.watch_handler_specifier import WatchHandlerSpecifier


class WatchHandlerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARI2_WATCH_HANDLER_",
        extra="ignore",
    )

    default: WatchHandlerSpecifier = "vanilla"

    presets: dict[WatchHandlerName, ImportPath] = Field(
        default_factory=lambda: {
            "slack": "kiari.impl.watch_handler_impl.slack:SlackWatchHandler",
            "vanilla": "kiari.impl.watch_handler_impl.vanilla:VanillaWatchHandler",
        }
    )

    customs: dict[WatchHandlerName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(WatchHandlerSettings)
