import json
from collections.abc import Callable
from urllib.parse import quote

import httpx
from kiarina.agi.history import History
from kiarina.agi.run_context import RunContext

from kiari.lib.history_repository import BaseHistoryRepository

from .._settings import FirebaseStorageHistoryRepositorySettings


class FirebaseStorageHistoryRepository(BaseHistoryRepository):
    def __init__(
        self,
        settings: FirebaseStorageHistoryRepositorySettings,
        *,
        token_provider: Callable[[], str] | None = None,
    ) -> None:
        super().__init__()
        self.settings = settings
        self._token_provider = token_provider

    async def _load(self, run_context: RunContext) -> History | None:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                self._object_url(run_context),
                params={"alt": "media"},
                headers=self._headers(),
            )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return History.model_validate_json(response.content)

    async def _save(self, history: History, run_context: RunContext) -> None:
        raw_data = json.dumps(
            history.model_dump(mode="json"), ensure_ascii=False, separators=(",", ":")
        ).encode("utf-8")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self._collection_url(),
                params={"uploadType": "media", "name": self._object_name(run_context)},
                headers={**self._headers(), "Content-Type": "application/json"},
                content=raw_data,
            )
        response.raise_for_status()

    async def _delete(self, run_context: RunContext) -> None:
        if not self.settings.allow_delete:
            raise PermissionError("History deletion is disabled for this Firebase Storage client")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.delete(
                self._object_url(run_context),
                headers=self._headers(),
            )
        if response.status_code != 404:
            response.raise_for_status()

    def _headers(self) -> dict[str, str]:
        token = (
            self._token_provider()
            if self._token_provider is not None
            else self.settings.id_token.get_secret_value()
            if self.settings.id_token is not None
            else None
        )
        if token is None:
            raise ValueError("Firebase ID token or token provider is required")
        return {"Authorization": f"Bearer {token}"}

    def _collection_url(self) -> str:
        return f"https://firebasestorage.googleapis.com/v0/b/{self.settings.bucket_name}/o"

    def _object_url(self, run_context: RunContext) -> str:
        return f"{self._collection_url()}/{quote(self._object_name(run_context), safe='')}"

    def _object_name(self, run_context: RunContext) -> str:
        return self.settings.object_name_template.format(
            organization_id=run_context.organization_id,
            user_id=run_context.user_id,
            agent_id=run_context.agent_id,
        )
