import secrets
from typing import Any

from fastapi import HTTPException, status
from kiarina.agi.run_context import RunContext

from kiari.core.profile import RunOptions
from kiari.fastapi.authenticator import BaseAuthenticator
from kiari.fastapi.fastapi_handler import FastAPIRequest

from .._settings import BearerAuthenticatorSettings, settings_manager


class BearerAuthenticator(BaseAuthenticator):
    def __init__(
        self,
        settings: BearerAuthenticatorSettings | None = None,
        **kwargs: Any,
    ) -> None:
        base_settings = settings or settings_manager.settings
        self.settings = BearerAuthenticatorSettings.model_validate(
            {
                **base_settings.model_dump(),
                **kwargs,
            }
        )

    async def authenticate(
        self,
        request: FastAPIRequest,
        run_options: RunOptions,
    ) -> RunContext:
        if self.settings.api_key is None:
            raise RuntimeError("API key is not configured for Bearer authentication")

        authorization = request.headers.get("authorization")

        if not authorization:
            raise self._unauthorized("Authorization header is required")

        parts = authorization.split()

        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise self._unauthorized(
                "Invalid authorization header format. Expected: Bearer {token}"
            )

        if not secrets.compare_digest(
            parts[1],
            self.settings.api_key.get_secret_value(),
        ):
            raise self._unauthorized("Invalid API key")

        return RunContext()

    def _unauthorized(self, detail: str) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )
