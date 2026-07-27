from contextlib import AbstractAsyncContextManager
from typing import Protocol, runtime_checkable

from kiarina.agi.event import Event

from kiari.core.profile import ProfileName, RunOptions
from kiari.lib.watcher import WatchEvent

from .._schemas.schedule_session import ScheduleSession
from .schedule_handler_name import ScheduleHandlerName


@runtime_checkable
class ScheduleHandler(Protocol):
    name: ScheduleHandlerName
    profile_name: ProfileName
    run_options: RunOptions

    def handle_session(
        self,
        interval: str | None,
        cron: str | None,
    ) -> AbstractAsyncContextManager[ScheduleSession]: ...

    async def handle_watch_event(
        self,
        watch_event: WatchEvent,
        session: ScheduleSession,
    ) -> None: ...

    async def handle_schedule(self, session: ScheduleSession) -> bool: ...

    def handle_request(
        self,
        session: ScheduleSession,
    ) -> AbstractAsyncContextManager[None]: ...

    async def on_agent_event(
        self,
        session: ScheduleSession,
        event: Event,
    ) -> None: ...
