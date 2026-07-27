from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class GitHubSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARI_GITHUB_",
        extra="ignore",
    )
    access_token: SecretStr | None = None
    ignore_cache: bool = False
    trusted_usernames: list[str] = Field(default_factory=list)
    skip_trust_verification: bool = False


settings_manager = SettingsManager(GitHubSettings)
