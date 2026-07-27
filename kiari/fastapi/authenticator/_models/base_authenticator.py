from __future__ import annotations

from typing import TYPE_CHECKING, Any

from kiarina.agi.run_context import RunContext

from kiari.core.profile import RunOptions

if TYPE_CHECKING:
    from kiari.fastapi.fastapi_handler._schemas.fastapi_request import FastAPIRequest

from .._types.authenticator import Authenticator


class BaseAuthenticator(Authenticator):
    def __init__(self, **kwargs: Any) -> None:
        self.init_kwargs = kwargs

    async def authenticate(
        self,
        request: FastAPIRequest,
        run_options: RunOptions,
    ) -> RunContext:
        return RunContext()
