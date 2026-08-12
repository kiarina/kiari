from collections.abc import Callable
from typing import Any

from .._models.firebase_storage_history_repository import FirebaseStorageHistoryRepository
from .._settings import FirebaseStorageHistoryRepositorySettings, settings_manager


def create_firebase_storage_history_repository(
    *,
    token_provider: Callable[[], str] | None = None,
    **kwargs: Any,
) -> FirebaseStorageHistoryRepository:
    settings = settings_manager.get_settings()
    if kwargs:
        settings = FirebaseStorageHistoryRepositorySettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )
    return FirebaseStorageHistoryRepository(settings, token_provider=token_provider)
