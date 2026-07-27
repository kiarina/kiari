from kiarina.utils.common import ImportPath
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from ._types.authenticator_name import AuthenticatorName
from ._types.authenticator_specifier import AuthenticatorSpecifier


class AuthenticatorSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARI_FASTAPI_AUTHENTICATOR_",
        extra="ignore",
    )

    default: AuthenticatorSpecifier = "none"
    presets: dict[AuthenticatorName, ImportPath] = Field(
        default_factory=lambda: {
            "none": "kiari.impl.authenticator_impl.none:NoneAuthenticator",
            "bearer": "kiari.impl.authenticator_impl.bearer:BearerAuthenticator",
        }
    )
    customs: dict[AuthenticatorName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(AuthenticatorSettings)
