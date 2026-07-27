import asyncio
from collections.abc import AsyncIterator

from kiari.lib.watcher import BaseWatcher, WatchEvent


class ExampleWatcher(BaseWatcher):
    async def watch(self, stop_event: asyncio.Event) -> AsyncIterator[WatchEvent]:
        if not stop_event.is_set():
            yield WatchEvent(watcher_name=self.name, text="hello")


async def test_base_watcher() -> None:
    watcher = ExampleWatcher(answer=42)
    watcher.name = "example"

    assert watcher.name == "example"
    assert watcher.init_kwargs == {"answer": 42}
    assert str(watcher) == "ExampleWatcher"

    events = [event async for event in watcher.watch(asyncio.Event())]
    assert len(events) == 1
    assert events[0].watcher_name == "example"
    assert events[0].text == "hello"
