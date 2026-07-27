from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class KiapiWebSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARI2_WEB_IMPL_KIAPI_",
        extra="ignore",
    )

    kiapi_base_url: str = "http://127.0.0.1:8500"
    timeout: float = 120.0


settings_manager = SettingsManager(KiapiWebSettings)
