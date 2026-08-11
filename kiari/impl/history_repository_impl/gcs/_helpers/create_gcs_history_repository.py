from typing import Any

from .._models.gcs_history_repository import GCSHistoryRepository
from .._settings import GCSHistoryRepositorySettings, settings_manager


def create_gcs_history_repository(**kwargs: Any) -> GCSHistoryRepository:
    settings = settings_manager.get_settings()
    if kwargs:
        settings = GCSHistoryRepositorySettings.model_validate({**settings.model_dump(), **kwargs})
    return GCSHistoryRepository(settings)
