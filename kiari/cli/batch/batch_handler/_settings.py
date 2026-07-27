from kiarina.utils.common import ImportPath
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from ._types.batch_handler_name import BatchHandlerName
from ._types.batch_handler_specifier import BatchHandlerSpecifier


class BatchHandlerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARI_BATCH_HANDLER_",
        extra="ignore",
    )

    default: BatchHandlerSpecifier = "vanilla"

    presets: dict[BatchHandlerName, ImportPath] = Field(
        default_factory=lambda: {
            "vanilla": "kiari.impl.batch_handler_impl.vanilla:VanillaBatchHandler",
        }
    )

    customs: dict[BatchHandlerName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(BatchHandlerSettings)
