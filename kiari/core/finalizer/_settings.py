from kiarina.utils.common import ImportPath
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from ._types.finalizer_name import FinalizerName


class FinalizerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARI2_FINALIZER_",
        extra="ignore",
    )

    presets: dict[FinalizerName, ImportPath] = Field(
        default_factory=lambda: {
            "null": "kiari.impl.finalizer_impl.null:NullFinalizer",
            "subprocess": "kiari.impl.finalizer_impl.subprocess:SubprocessFinalizer",
        }
    )

    customs: dict[FinalizerName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(FinalizerSettings)
