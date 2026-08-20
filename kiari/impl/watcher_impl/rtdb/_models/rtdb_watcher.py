import asyncio
import logging
from collections.abc import AsyncIterator

from kiarina.lib.firebase import token_manager_registry
from kiarina.lib.firebase_rtdb import watch_data

from kiari.lib.watcher import BaseWatcher

from .._schemas.rtdb_watch_event import RTDBWatchEvent
from .._settings import RTDBWatcherSettings

logger = logging.getLogger(__name__)


class RTDBWatcher(BaseWatcher):
    def __init__(self, settings: RTDBWatcherSettings) -> None:
        super().__init__()
        self.settings: RTDBWatcherSettings = settings

    async def watch(self, stop_event: asyncio.Event) -> AsyncIterator[RTDBWatchEvent]:
        token_manager = token_manager_registry.get(self.settings.firebase_settings_key)

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
