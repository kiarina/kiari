from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class FirebaseStorageHistoryRepositorySettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARI_HISTORY_REPOSITORY_IMPL_FIREBASE_STORAGE_",
        extra="ignore",
    )

    bucket_name: str = Field(
        default="invalid",
        title="Bucket Name",
        description="Firebase Storage bucket containing History objects.",
    )
    object_name_template: str = Field(
        default="{organization_id}/{user_id}/{agent_id}/history.json",
        title="Object Name Template",
        description="Firebase Storage object name template used to store one History per agent.",
    )
    id_token: SecretStr | None = Field(
        default=None,
        title="Firebase ID Token",
        description="Static Firebase ID token. Inject a token provider for refreshable clients.",
    )
    allow_delete: bool = Field(
        default=True,
        title="Allow Delete",
        description="Whether this client may delete History objects.",
    )


settings_manager = SettingsManager(FirebaseStorageHistoryRepositorySettings)
