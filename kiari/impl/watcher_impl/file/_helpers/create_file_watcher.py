from typing import Any

from .._models.file_watcher import FileWatcher
from .._settings import FileWatcherSettings, settings_manager


def create_file_watcher(**kwargs: Any) -> FileWatcher:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = FileWatcherSettings.model_validate({**settings.model_dump(), **kwargs})

    return FileWatcher(settings)
