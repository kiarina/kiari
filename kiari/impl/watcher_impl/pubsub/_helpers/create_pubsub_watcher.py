from typing import Any

from .._models.pubsub_watcher import PubsubWatcher
from .._settings import PubsubWatcherSettings, settings_manager


def create_pubsub_watcher(**kwargs: Any) -> PubsubWatcher:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = PubsubWatcherSettings.model_validate({**settings.model_dump(), **kwargs})

    return PubsubWatcher(settings)
