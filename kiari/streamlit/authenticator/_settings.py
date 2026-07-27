from kiarina.utils.common import ImportPath
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from ._types.streamlit_authenticator_name import StreamlitAuthenticatorName
from ._types.streamlit_authenticator_specifier import StreamlitAuthenticatorSpecifier


class StreamlitAuthenticatorSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARI_STREAMLIT_AUTHENTICATOR_",
        extra="ignore",
    )

    default: StreamlitAuthenticatorSpecifier = "browser-session"
    presets: dict[StreamlitAuthenticatorName, ImportPath] = Field(
        default_factory=lambda: {
            "browser-session": (
                "kiari.impl.streamlit_authenticator_impl.browser_session:"
                "BrowserSessionAuthenticator"
            ),
            "oidc": "kiari.impl.streamlit_authenticator_impl.oidc:OIDCAuthenticator",
        }
    )
    customs: dict[StreamlitAuthenticatorName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(StreamlitAuthenticatorSettings)
