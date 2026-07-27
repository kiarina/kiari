from kiarina.utils.common import ImportPath
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from ._types.history_repository_name import HistoryRepositoryName
from ._types.history_repository_specifier import HistoryRepositorySpecifier


class HistoryRepositorySettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARI2_HISTORY_REPOSITORY_",
        extra="ignore",
    )

    default: HistoryRepositorySpecifier = "null"

    presets: dict[HistoryRepositoryName, ImportPath] = Field(
        default_factory=lambda: {
            "in_memory": "kiari.impl.history_repository_impl.in_memory:InMemoryHistoryRepository",
            "local": "kiari.impl.history_repository_impl.local:create_local_history_repository",
            "null": "kiari.impl.history_repository_impl.null:NullHistoryRepository",
        }
    )

    customs: dict[HistoryRepositoryName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(HistoryRepositorySettings)
