from kiari.impl.watcher_impl.rtdb import RTDBWatcher, create_rtdb_watcher


def test_create_rtdb_watcher() -> None:
    watcher = create_rtdb_watcher(database_url="https://example.test", path="/events")

    assert isinstance(watcher, RTDBWatcher)
    assert watcher.settings.database_url == "https://example.test"
    assert watcher.settings.path == "/events"
