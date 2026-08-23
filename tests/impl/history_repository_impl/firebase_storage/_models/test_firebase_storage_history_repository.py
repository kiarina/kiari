import base64
import json
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

import httpx
import pytest
from kiarina.agi.history import History
from kiarina.lib.firebase import (
    InMemoryTokenStore,
    Token,
    TokenManager,
    token_manager_registry,
)

from kiari.impl.history_repository_impl.firebase_storage import (
    create_firebase_storage_history_repository,
)

_SETTINGS_KEY = "test_storage"


def _id_token(claims: dict[str, object]) -> str:
    payload = base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip("=")
    return f"header.{payload}.signature"


@pytest.fixture
def registered_token_manager() -> Iterator[str]:
    id_token = _id_token(
        {
            "aud": "project",
            "sub": "uid",
            "exp": int((datetime.now(UTC) + timedelta(hours=1)).timestamp()),
        }
    )
    token_manager_registry.register(
        _SETTINGS_KEY,
        TokenManager(
            api_key="api-key",
            token_store=InMemoryTokenStore(Token(refresh_token="refresh-token", id_token=id_token)),
        ),
    )
    try:
        yield id_token
    finally:
        token_manager_registry.unregister(_SETTINGS_KEY)


async def test_firebase_storage_history_repository_round_trip(
    monkeypatch, run_context, registered_token_manager
) -> None:
    objects: dict[str, bytes] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        object_name = f"users/{run_context.user_id}/spirits/{run_context.agent_id}/stm.json"
        assert request.headers["Authorization"] == f"Bearer {registered_token_manager}"
        if request.method == "POST":
            assert request.url.params["name"] == object_name
            assert request.headers["Content-Type"] == "application/json"
            objects[object_name] = request.content
            return httpx.Response(200, json={"name": object_name})
        if request.method == "GET":
            if object_name not in objects:
                return httpx.Response(404)
            return httpx.Response(200, content=objects[object_name])
        if request.method == "DELETE":
            objects.pop(object_name, None)
            return httpx.Response(204)
        raise AssertionError(f"Unexpected request: {request.method}")

    transport = httpx.MockTransport(handler)
    real_async_client = httpx.AsyncClient
    monkeypatch.setattr(
        "kiari.impl.history_repository_impl.firebase_storage._models."
        "firebase_storage_history_repository.httpx.AsyncClient",
        lambda **kwargs: real_async_client(transport=transport, **kwargs),
    )
    repository = create_firebase_storage_history_repository(
        bucket_name="bucket",
        object_name_template="users/{user_id}/spirits/{agent_id}/stm.json",
        firebase_settings_key=_SETTINGS_KEY,
    )

    assert await repository.load(run_context) is None
    await repository.save(History(metadata={"current_body_id": "body-1"}), run_context)
    loaded = await repository.load(run_context)
    assert loaded is not None
    assert loaded.metadata["current_body_id"] == "body-1"
    assert json.loads(objects[next(iter(objects))])["metadata"]["current_body_id"] == "body-1"
    await repository.delete(run_context)
    assert objects == {}


async def test_firebase_storage_history_repository_can_forbid_delete(run_context) -> None:
    repository = create_firebase_storage_history_repository(
        bucket_name="bucket",
        allow_delete=False,
    )

    with pytest.raises(PermissionError):
        await repository.delete(run_context)
