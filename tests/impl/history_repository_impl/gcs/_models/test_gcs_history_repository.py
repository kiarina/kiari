from pathlib import Path
from typing import ClassVar, cast

from kiarina.agi.asset_repository import AssetRepository, BaseAssetRepository
from kiarina.agi.history import History
from kiarina.utils.file import FileBlob
from kiarina.utils.mime import MIMEBlob

from kiari.impl.history_repository_impl.gcs import create_gcs_history_repository


class MemoryAssetRepository(BaseAssetRepository):
    objects: ClassVar[dict[str, bytes]] = {}

    async def _get(self, uri: str) -> MIMEBlob | None:
        raw_data = self.objects.get(uri)
        if raw_data is None:
            return None
        return FileBlob(
            Path("history.json"), mime_type="application/json", raw_data=raw_data
        ).mime_blob

    async def _set(self, uri: str, mime_type: str, raw_data: bytes) -> None:
        del mime_type
        self.objects[uri] = raw_data

    async def _delete(self, uri: str) -> None:
        self.objects.pop(uri, None)


async def test_gcs_history_repository_uses_agent_scoped_object(monkeypatch, run_context) -> None:
    asset_repository = MemoryAssetRepository()
    monkeypatch.setattr(
        "kiari.impl.history_repository_impl.gcs._models.gcs_history_repository."
        "create_gcs_asset_repository",
        lambda **_: cast(AssetRepository, asset_repository),
    )
    repository = create_gcs_history_repository(
        object_uri_template="gs://bucket/users/{user_id}/spirits/{agent_id}/stm.json"
    )
    uri = f"gs://bucket/users/{run_context.user_id}/spirits/{run_context.agent_id}/stm.json"
    MemoryAssetRepository.objects.clear()

    assert await repository.load(run_context) is None
    await repository.save(History(metadata={"current_body_id": "body-1"}), run_context)
    assert uri in MemoryAssetRepository.objects
    loaded = await repository.load(run_context)
    assert loaded is not None
    assert loaded.metadata["current_body_id"] == "body-1"
    await repository.delete(run_context)
    assert uri not in MemoryAssetRepository.objects
