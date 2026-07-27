from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class OIDCAuthenticatorSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARI_STREAMLIT_OIDC_",
        extra="ignore",
    )

    provider: str | None = None
    display_name_claim: str = "name"


settings_manager = SettingsManager(OIDCAuthenticatorSettings)
