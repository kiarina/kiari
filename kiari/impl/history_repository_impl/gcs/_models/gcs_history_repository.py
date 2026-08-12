import asyncio
import json

import google.cloud.exceptions
from google.cloud.storage import Blob, Client  # type: ignore
from kiarina.agi.history import History
from kiarina.agi.run_context import RunContext
from kiarina.lib.google import get_cloud_options

from kiari.lib.history_repository import BaseHistoryRepository

from .._settings import GCSHistoryRepositorySettings


class GCSHistoryRepository(BaseHistoryRepository):
    def __init__(
        self,
        settings: GCSHistoryRepositorySettings,
        *,
        client: Client | None = None,
    ) -> None:
        super().__init__()
        self.settings = settings
        self._client = client

    @property
    def client(self) -> Client:
        if self._client is None:
            options = get_cloud_options(self.settings.google_auth_settings_key)
            self._client = Client(**options)
        return self._client

    async def _load(self, run_context: RunContext) -> History | None:
        blob = self._blob(run_context)
        try:
            raw_data = await asyncio.to_thread(blob.download_as_bytes)
        except google.cloud.exceptions.NotFound:
            return None
        value = json.loads(raw_data)
        if not isinstance(value, dict):
            raise ValueError("Stored History must be a JSON object")
        return History.model_validate(value)

    async def _save(self, history: History, run_context: RunContext) -> None:
        raw_data = json.dumps(
            history.model_dump(mode="json"), ensure_ascii=False, separators=(",", ":")
        ).encode("utf-8")
        await asyncio.to_thread(
            self._blob(run_context).upload_from_string,
            raw_data,
            content_type="application/json",
        )

    async def _delete(self, run_context: RunContext) -> None:
        try:
            await asyncio.to_thread(self._blob(run_context).delete)
        except google.cloud.exceptions.NotFound:
            pass

    def _blob(self, run_context: RunContext) -> Blob:
        object_name = self.settings.object_name_template.format(
            organization_id=run_context.organization_id,
            user_id=run_context.user_id,
            agent_id=run_context.agent_id,
        )
        return self.client.bucket(self.settings.bucket_name).blob(object_name)
