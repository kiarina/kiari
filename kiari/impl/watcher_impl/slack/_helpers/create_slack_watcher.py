from typing import Any

from .._models.slack_watcher import SlackWatcher
from .._settings import SlackWatcherSettings, settings_manager


def create_slack_watcher(**kwargs: Any) -> SlackWatcher:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = SlackWatcherSettings.model_validate({**settings.model_dump(), **kwargs})

    return SlackWatcher(settings)
