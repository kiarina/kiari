from contextlib import AbstractAsyncContextManager
from typing import Protocol, runtime_checkable

from kiarina.agi.event import Event

from kiari.core.profile import ProfileName, RunOptions

from .._schemas.batch_request import BatchRequest
from .._schemas.batch_session import BatchSession
from .._types.batch_handler_name import BatchHandlerName


@runtime_checkable
class BatchHandler(Protocol):
    name: BatchHandlerName
    profile_name: ProfileName
    run_options: RunOptions

    def handle_request(
        self,
        request: BatchRequest,
    ) -> AbstractAsyncContextManager[BatchSession]: ...

    async def on_agent_event(self, session: BatchSession, event: Event) -> None: ...
