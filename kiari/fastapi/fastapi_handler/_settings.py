from kiarina.utils.common import ImportPath
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from ._types.fastapi_handler_name import FastAPIHandlerName
from ._types.fastapi_handler_specifier import FastAPIHandlerSpecifier


class FastAPIHandlerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARI_FASTAPI_HANDLER_",
        extra="ignore",
    )

    default: FastAPIHandlerSpecifier = "vanilla"
    presets: dict[FastAPIHandlerName, ImportPath] = Field(
        default_factory=lambda: {
            "vanilla": "kiari.impl.fastapi_handler_impl.vanilla:VanillaFastAPIHandler",
        }
    )
    customs: dict[FastAPIHandlerName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(FastAPIHandlerSettings)
