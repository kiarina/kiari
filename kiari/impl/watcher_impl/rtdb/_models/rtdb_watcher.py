import asyncio
import logging
from collections.abc import AsyncIterator

from kiarina.lib.firebase import TokenManager, settings_manager as firebase_auth_settings_manager
from kiarina.lib.firebase_rtdb import watch_data

from kiari.lib.watcher import BaseWatcher

from .._schemas.rtdb_watch_event import RTDBWatchEvent
from .._services.file_token_cache import FileTokenCache
from .._settings import RTDBWatcherSettings

logger = logging.getLogger(__name__)


class RTDBWatcher(BaseWatcher):
    def __init__(self, settings: RTDBWatcherSettings) -> None:
        super().__init__()
        self.settings: RTDBWatcherSettings = settings

    async def watch(self, stop_event: asyncio.Event) -> AsyncIterator[RTDBWatchEvent]:
        firebase_auth_settings = firebase_auth_settings_manager.get_settings(
            self.settings.firebase_settings_key
        )

        token_manager = TokenManager(
            api_key=firebase_auth_settings.api_key.get_secret_value(),
            token_data_cache=FileTokenCache(self.settings.token_data_file_path),
        )

        logger.info(f"Connected to Firebase RTDB: {self.settings.database_url}{self.settings.path}")

        async for event in watch_data(
            database_url=self.settings.database_url,
            path=self.settings.path,
            token_manager=token_manager,
            stop_event=stop_event,
        ):
            yield RTDBWatchEvent.create(
                watcher_name=self.name,
                event_type=event.event_type,
                path=event.path,
                data=event.data,
            )

            logger.debug(f"Data changed at path: {event.path}")
