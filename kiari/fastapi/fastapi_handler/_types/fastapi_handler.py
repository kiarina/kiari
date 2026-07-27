from contextlib import AbstractAsyncContextManager
from typing import Protocol, runtime_checkable

from kiarina.agi.event import Event

from kiari.core.profile import ProfileName, RunOptions

from ..._schemas.fastapi_session import FastAPISession
from .._schemas.fastapi_request import FastAPIRequest
from .fastapi_handler_name import FastAPIHandlerName


@runtime_checkable
class FastAPIHandler(Protocol):
    name: FastAPIHandlerName
    profile_name: ProfileName
    run_options: RunOptions

    def handle_request(
        self,
        request: FastAPIRequest,
    ) -> AbstractAsyncContextManager[FastAPISession]: ...

    async def on_agent_event(
        self,
        session: FastAPISession,
        event: Event,
    ) -> Event | None: ...

    async def on_agent_completed(
        self,
        session: FastAPISession,
        final_event: Event,
    ) -> Event | None: ...

    async def on_agent_error(
        self,
        session: FastAPISession,
        error: Exception,
    ) -> Event | None: ...
