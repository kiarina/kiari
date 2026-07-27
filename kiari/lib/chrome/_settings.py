from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class ChromeSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARI_CHROME_",
        extra="ignore",
    )

    host: Literal["127.0.0.1", "localhost", "::1"] = "127.0.0.1"
    """Loopback host used by Chrome Bridge."""

    port: int = Field(default=8765, ge=1, le=65535)
    """Chrome Bridge Direct API port."""

    startup_timeout: float = Field(default=45, gt=0)
    """Seconds to wait for the managed server and extension."""

    session_idle_ttl: float = Field(default=120, gt=0)
    """Server-side idle lifetime for an exclusive SDK session."""

    session_max_lifetime: float = Field(default=600, gt=0)
    """Maximum server-side lifetime for an exclusive SDK session."""

    session_wait_timeout: float | None = Field(default=None, gt=0)
    """Seconds to wait for an exclusive session, or no deadline when None."""


settings_manager = SettingsManager(ChromeSettings)
