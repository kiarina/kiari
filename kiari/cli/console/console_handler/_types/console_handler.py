from contextlib import AbstractAsyncContextManager
from typing import Protocol, runtime_checkable

from kiarina.agi.event import Event
from rich.console import RenderableType

from kiari.core.profile import ProfileName, RunOptions

from .._schemas.console_request import ConsoleRequest
from .._schemas.console_session import ConsoleSession
from .console_handler_name import ConsoleHandlerName


@runtime_checkable
class ConsoleHandler(Protocol):
    name: ConsoleHandlerName
    profile_name: ProfileName
    run_options: RunOptions

    def handle_session(self) -> AbstractAsyncContextManager[ConsoleSession]: ...

    def handle_request(
        self,
        session: ConsoleSession,
        request: ConsoleRequest,
    ) -> AbstractAsyncContextManager[None]: ...

    def render_ui(self, session: ConsoleSession) -> RenderableType | None: ...

    async def on_agent_event(
        self,
        session: ConsoleSession,
        event: Event,
    ) -> None: ...
