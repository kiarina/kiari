from typing import Any

from .._models.rtdb_watcher import RTDBWatcher
from .._settings import RTDBWatcherSettings, settings_manager


def create_rtdb_watcher(**kwargs: Any) -> RTDBWatcher:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = RTDBWatcherSettings.model_validate({**settings.model_dump(), **kwargs})

    return RTDBWatcher(settings)
