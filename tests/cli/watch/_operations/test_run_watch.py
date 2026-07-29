import asyncio
import re
import signal
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock

import pytest

from kiari.cli.watch._operations.run_watch import _worker, run_watch
from kiari.core.profile import RunOptions
from kiari.lib.watcher import BaseWatcher, DiscardWatchEvent, WatchEvent, watcher_registry


class OneShotWatcher(BaseWatcher):
    async def watch(self, stop_event: asyncio.Event) -> AsyncIterator[WatchEvent]:
        yield WatchEvent(watcher_name=self.name, text="hello")
        stop_event.set()


class ContinuousWatcher(BaseWatcher):
    async def watch(self, stop_event: asyncio.Event) -> AsyncIterator[WatchEvent]:
        while not stop_event.is_set():
            yield WatchEvent(watcher_name=self.name, text="hello")
            await asyncio.sleep(0.1)


@pytest.fixture(autouse=True)
def cleanup():
    watcher_registry.register("one_shot", OneShotWatcher)
    watcher_registry.register("continuous", ContinuousWatcher)
    yield
    watcher_registry.unregister("one_shot")
    watcher_registry.unregister("continuous")


async def test_run_watch_requires_watcher() -> None:
    with pytest.raises(
        ValueError,
        match=re.escape("Watch mode requires at least one watcher."),
    ):
        await run_watch("default", RunOptions())


async def test_run_watch() -> None:
    await run_watch(
        "default",
        RunOptions(
            watchers=["one_shot"],
            chat_model="mock",
            no_save=True,
            watch_queue_size=1,
            watch_max_concurrent=1,
        ),
    )


async def test_permanently_invalid_event_is_acknowledged() -> None:
    event = WatchEvent(watcher_name="one_shot", text="invalid")
    acknowledge = AsyncMock()
    release = AsyncMock()
    event.set_acknowledgement_callbacks(acknowledge=acknowledge, release=release)

    class DiscardingHandler:
        @asynccontextmanager
        async def handle_event(self, watch_event: WatchEvent):
            raise DiscardWatchEvent("invalid contract")
            yield  # pragma: no cover

    queue: asyncio.Queue[WatchEvent | None] = asyncio.Queue()
    await queue.put(event)
    await queue.put(None)

    await _worker(DiscardingHandler(), queue)  # type: ignore[arg-type]

    acknowledge.assert_awaited_once()
    release.assert_not_awaited()


async def test_graceful_shutdown() -> None:
    task = asyncio.create_task(
        run_watch(
            "default",
            RunOptions(
                watchers=["continuous"],
                chat_model="mock",
                no_save=True,
                watch_queue_size=2,
                watch_max_concurrent=1,
            ),
        )
    )

    await asyncio.sleep(0.2)

    signal_handler = signal.getsignal(signal.SIGINT)

    if callable(signal_handler):
        signal_handler(signal.SIGINT, None)

    await task


async def test_force_shutdown() -> None:
    task = asyncio.create_task(
        run_watch(
            "default",
            RunOptions(
                watchers=["continuous"],
                chat_model="mock",
                no_save=True,
                watch_queue_size=2,
                watch_max_concurrent=1,
            ),
        )
    )

    await asyncio.sleep(0.2)

    signal_handler = signal.getsignal(signal.SIGINT)

    if callable(signal_handler):
        signal_handler(signal.SIGINT, None)

    await asyncio.sleep(0.1)

    with pytest.raises(KeyboardInterrupt):
        if callable(signal_handler):
            signal_handler(signal.SIGINT, None)

    task.cancel()

    try:
        await task
    except asyncio.CancelledError:
        pass
