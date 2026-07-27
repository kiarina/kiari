from kiari.impl.watcher_impl.slack import SlackWatcher, create_slack_watcher


def test_create_slack_watcher() -> None:
    watcher = create_slack_watcher(channel_ids=["C123"], max_file_size_mb=1.5)

    assert isinstance(watcher, SlackWatcher)
    assert watcher.settings.channel_ids == ["C123"]
    assert watcher.settings.max_file_size_mb == 1.5


def test_from_string_list() -> None:
    watcher = create_slack_watcher(channel_ids="C123,C456")

    assert watcher.settings.channel_ids == ["C123", "C456"]
