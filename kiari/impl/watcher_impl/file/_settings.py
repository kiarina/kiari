from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from ._types.change_type import ChangeType


class FileWatcherSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARI2_WATCHER_FILE_",
        extra="ignore",
    )

    paths: list[str] = Field(default_factory=lambda: ["."])
    include_patterns: list[str] = Field(default_factory=list)
    exclude_patterns: list[str] = Field(default_factory=list)
    change_types: list[ChangeType] = Field(default_factory=list)
    debounce: float = 1.0

    @field_validator(
        "paths",
        "include_patterns",
        "exclude_patterns",
        "change_types",
        mode="before",
    )
    @classmethod
    def _parse_list(cls, value: Any) -> Any:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]

        return value


settings_manager = SettingsManager(FileWatcherSettings)
