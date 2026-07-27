from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from kiarina.agi.run_context import RunContext

from kiari.core.profile import RunOptions

if TYPE_CHECKING:
    from kiari.fastapi.fastapi_handler._schemas.fastapi_request import FastAPIRequest


@runtime_checkable
class Authenticator(Protocol):
    async def authenticate(
        self,
        request: FastAPIRequest,
        run_options: RunOptions,
    ) -> RunContext: ...
