from typing import cast

import google.cloud.exceptions
from google.cloud.storage import Client  # type: ignore
from kiarina.agi.history import History

from kiari.impl.history_repository_impl.gcs import create_gcs_history_repository


class MemoryBlob:
    def __init__(self, name: str, objects: dict[str, bytes]) -> None:
        self.name = name
        self.objects = objects

    def download_as_bytes(self) -> bytes:
        try:
            return self.objects[self.name]
        except KeyError as error:
            raise google.cloud.exceptions.NotFound("missing") from error

    def upload_from_string(self, raw_data: bytes, *, content_type: str) -> None:
        assert content_type == "application/json"
        self.objects[self.name] = raw_data

    def delete(self) -> None:
        if self.name not in self.objects:
            raise google.cloud.exceptions.NotFound("missing")
        del self.objects[self.name]


class MemoryBucket:
    def __init__(self, objects: dict[str, bytes]) -> None:
        self.objects = objects

    def blob(self, name: str) -> MemoryBlob:
        return MemoryBlob(name, self.objects)


class MemoryClient:
    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}
        self.bucket_names: list[str] = []

    def bucket(self, name: str) -> MemoryBucket:
        self.bucket_names.append(name)
        return MemoryBucket(self.objects)


async def test_gcs_history_repository_uses_agent_scoped_object(run_context) -> None:
    client = MemoryClient()
    repository = create_gcs_history_repository(
        bucket_name="bucket",
        object_name_template="users/{user_id}/spirits/{agent_id}/stm.json",
    )
    repository._client = cast(Client, client)
    object_name = f"users/{run_context.user_id}/spirits/{run_context.agent_id}/stm.json"

    assert await repository.load(run_context) is None
    await repository.save(History(metadata={"current_body_id": "body-1"}), run_context)
    assert object_name in client.objects
    assert client.bucket_names == ["bucket", "bucket"]
    loaded = await repository.load(run_context)
    assert loaded is not None
    assert loaded.metadata["current_body_id"] == "body-1"
    await repository.delete(run_context)
    assert object_name not in client.objects
    await repository.delete(run_context)
