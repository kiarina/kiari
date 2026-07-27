from collections.abc import AsyncIterator
from typing import Protocol, runtime_checkable

from kiarina.agi.event import Event

from kiari.core.profile import ProfileName, RunOptions
from kiari.streamlit import StreamlitIdentity

from .._schemas.streamlit_request import StreamlitRequest
from .._schemas.streamlit_session import StreamlitSession
from .streamlit_handler_name import StreamlitHandlerName


@runtime_checkable
class StreamlitHandler(Protocol):
    name: StreamlitHandlerName
    profile_name: ProfileName
    run_options: RunOptions

    async def create_session(
        self, identity: StreamlitIdentity, agent_id: str
    ) -> StreamlitSession: ...

    async def has_history(self, identity: StreamlitIdentity, agent_id: str) -> bool: ...

    async def delete_history(self, session: StreamlitSession) -> None: ...

    def run_request(
        self, session: StreamlitSession, request: StreamlitRequest
    ) -> AsyncIterator[Event]: ...

    async def apply_config(self, session: StreamlitSession, updates: dict[str, object]) -> None: ...

    async def back(self, session: StreamlitSession) -> bool: ...

    async def clear(self, session: StreamlitSession) -> None: ...
