import json
import re

from kiarina.agi.asset_repository import AssetRepository, URIPolicy
from kiarina.agi.asset_repository_impl.gcs import create_gcs_asset_repository
from kiarina.agi.history import History
from kiarina.agi.run_context import RunContext

from kiari.lib.history_repository import BaseHistoryRepository

from .._settings import GCSHistoryRepositorySettings


class GCSHistoryRepository(BaseHistoryRepository):
    def __init__(self, settings: GCSHistoryRepositorySettings) -> None:
        super().__init__()
        self.settings = settings

    async def _load(self, run_context: RunContext) -> History | None:
        repository, uri = self._repository(run_context)
        file_blob = await repository.get(uri, ignore_cache=True)
        if file_blob is None:
            return None
        value = json.loads(file_blob.raw_text)
        if not isinstance(value, dict):
            raise ValueError("Stored History must be a JSON object")
        return History.model_validate(value)

    async def _save(self, history: History, run_context: RunContext) -> None:
        repository, uri = self._repository(run_context)
        raw_data = json.dumps(
            history.model_dump(mode="json"), ensure_ascii=False, separators=(",", ":")
        ).encode("utf-8")
        await repository.set(uri, "application/json", raw_data)

    async def _delete(self, run_context: RunContext) -> None:
        repository, uri = self._repository(run_context)
        await repository.delete(uri)

    def _repository(self, run_context: RunContext) -> tuple[AssetRepository, str]:
        uri = self.settings.object_uri_template.format(
            organization_id=run_context.organization_id,
            user_id=run_context.user_id,
            agent_id=run_context.agent_id,
        )
        repository = create_gcs_asset_repository(
            google_auth_settings_key=self.settings.google_auth_settings_key
        )
        repository.run_context = run_context
        repository.uri_policy = URIPolicy(
            data_dir_uri_template=uri,
            cache_dir_uri_template=uri,
            allowed_uri_patterns=[re.escape(uri)],
        )
        return repository, uri
