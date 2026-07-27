from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class BearerAuthenticatorSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARI_FASTAPI_AUTHENTICATOR_BEARER_",
        extra="ignore",
    )

    api_key: SecretStr | None = None


settings_manager = SettingsManager(BearerAuthenticatorSettings)
