from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class GCSHistoryRepositorySettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARI_HISTORY_REPOSITORY_IMPL_GCS_",
        extra="ignore",
    )

    object_uri_template: str = Field(
        default="gs://invalid/{organization_id}/{user_id}/{agent_id}/history.json",
        title="Object URI Template",
        description="GCS object URI template used to store one History per agent.",
    )
    google_auth_settings_key: str | None = Field(
        default=None,
        title="Google Authentication Settings Key",
        description="Key used to resolve Google authentication settings.",
    )


settings_manager = SettingsManager(GCSHistoryRepositorySettings)
