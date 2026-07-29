from collections.abc import AsyncIterator
from contextlib import AbstractAsyncContextManager
from typing import Protocol, runtime_checkable

from kiarina.agi.event import Event

from kiari.core.profile import ProfileName, RunOptions
from kiari.lib.watcher import WatchEvent

from .._schemas.watch_session import WatchSession
from .watch_handler_name import WatchHandlerName


@runtime_checkable
class WatchHandler(Protocol):
    name: WatchHandlerName
    profile_name: ProfileName
    run_options: RunOptions

    def handle_event(
        self,
        watch_event: WatchEvent,
    ) -> AbstractAsyncContextManager[WatchSession]: ...

    def run_request(self, session: WatchSession) -> AsyncIterator[Event]: ...
    async def on_agent_event(self, session: WatchSession, event: Event) -> None: ...
    async def on_queue_full(self, watch_event: WatchEvent) -> None: ...
