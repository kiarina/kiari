from typing import Any

from .._models.local_history_repository import LocalHistoryRepository
from .._settings import LocalHistoryRepositorySettings, settings_manager


def create_local_history_repository(**kwargs: Any) -> LocalHistoryRepository:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = LocalHistoryRepositorySettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return LocalHistoryRepository(settings)
