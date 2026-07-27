import pytest
from kiarina.agi.event import AIMessageEvent

from kiari.cli.watch.watch_handler import BaseWatchHandler
from kiari.core.profile import RunOptions
from kiari.lib.watcher import WatchEvent


class ExampleWatchHandler(BaseWatchHandler):
    pass


def test_base_watch_handler() -> None:
    handler = ExampleWatchHandler("test_profile", RunOptions())
    handler.name = "example"

    assert handler.name == "example"
    assert str(handler.history_repository) == "NullHistoryRepository"


async def test_handle_event(text_file_path: str) -> None:
    handler = ExampleWatchHandler("test_profile", RunOptions(no_save=True))
    handler.name = "example"
    watch_event = WatchEvent(
        watcher_name="test",
        text="hello",
        attachments=[text_file_path],
    )

    async with handler.handle_event(watch_event) as session:
        assert session.watch_event == watch_event
        assert session.history.events
        await handler.on_agent_event(session, AIMessageEvent.create("hello"))

    await handler.on_queue_full(watch_event)

    with pytest.raises(Exception, match="Test error"):
        async with handler.handle_event(watch_event):
            raise Exception("Test error")
