from kiarina.utils.common import ImportPath
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from ._types.web_name import WebName
from ._types.web_specifier import WebSpecifier


class WebSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARI2_WEB_",
        extra="ignore",
    )

    default: WebSpecifier = "kiapi"

    presets: dict[WebName, ImportPath] = Field(
        default_factory=lambda: {
            "mock": "kiari.impl.web_impl.mock:create_mock_web",
            "kiapi": "kiari.impl.web_impl.kiapi:create_kiapi_web",
        }
    )

    customs: dict[WebName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(WebSettings)
