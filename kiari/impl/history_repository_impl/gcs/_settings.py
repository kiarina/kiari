from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class GCSHistoryRepositorySettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARI_HISTORY_REPOSITORY_IMPL_GCS_",
        extra="ignore",
    )

    bucket_name: str = Field(
        default="invalid",
        title="Bucket Name",
        description="GCS bucket containing History objects.",
    )
    object_name_template: str = Field(
        default="{organization_id}/{user_id}/{agent_id}/history.json",
        title="Object Name Template",
        description="GCS object name template used to store one History per agent.",
    )
    google_auth_settings_key: str | None = Field(
        default=None,
        title="Google Authentication Settings Key",
        description="Key used to resolve Google authentication settings.",
    )


settings_manager = SettingsManager(GCSHistoryRepositorySettings)
