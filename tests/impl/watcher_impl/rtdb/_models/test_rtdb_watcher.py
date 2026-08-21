import asyncio
from collections.abc import AsyncIterator
from typing import Any

from kiarina.lib.firebase import (
    InMemoryTokenStore,
    Token,
    TokenManager,
    token_manager_registry,
)

from kiari.impl.watcher_impl.rtdb import RTDBWatcher, RTDBWatcherSettings
from kiari.impl.watcher_impl.rtdb._models import rtdb_watcher as rtdb_watcher_module


async def test_watch_uses_the_token_manager_of_the_firebase_settings_key(monkeypatch) -> None:
    token_manager = TokenManager(
        api_key="api-key",
        token_store=InMemoryTokenStore(Token(refresh_token="refresh-token", id_token="id-token")),
    )
    token_manager_registry.register("test_watcher", token_manager)

    captured: dict[str, Any] = {}

    async def watch_data(**kwargs: Any) -> AsyncIterator[Any]:
        captured.update(kwargs)
        return
        yield  # pragma: no cover

    monkeypatch.setattr(rtdb_watcher_module, "watch_data", watch_data)

    watcher = RTDBWatcher(
        RTDBWatcherSettings(
            firebase_settings_key="test_watcher",
            database_url="https://example.test",
            path="/events",
        )
    )
    watcher.name = "rtdb"

    try:
        assert [event async for event in watcher.watch(asyncio.Event())] == []
    finally:
        token_manager_registry.unregister("test_watcher")

    assert captured["token_manager"] is token_manager
    assert captured["database_url"] == "https://example.test"
    assert captured["path"] == "/events"
