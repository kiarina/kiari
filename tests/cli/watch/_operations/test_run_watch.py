import asyncio
import re
import signal
from collections.abc import AsyncIterator
from typing import ClassVar

import pytest
from kiarina.agi.event import Event

from kiari.cli.watch._operations.run_watch import run_watch
from kiari.cli.watch.watch_handler import BaseWatchHandler, WatchSession, watch_handler_registry
from kiari.core.profile import RunOptions
from kiari.lib.watcher import BaseWatcher, WatchEvent, watcher_registry


class OneShotWatcher(BaseWatcher):
    async def watch(self, stop_event: asyncio.Event) -> AsyncIterator[WatchEvent]:
        yield WatchEvent(watcher_name=self.name, text="hello")
        stop_event.set()


class ContinuousWatcher(BaseWatcher):
    async def watch(self, stop_event: asyncio.Event) -> AsyncIterator[WatchEvent]:
        while not stop_event.is_set():
            yield WatchEvent(watcher_name=self.name, text="hello")
            await asyncio.sleep(0.1)


class CustomWatchHandler(BaseWatchHandler):
    calls: ClassVar[int] = 0

    async def run_request(self, session: WatchSession) -> AsyncIterator[Event]:
        self.__class__.calls += 1
        if False:
            yield session.history.events[-1]


@pytest.fixture(autouse=True)
def cleanup():
    watcher_registry.register("one_shot", OneShotWatcher)
    watcher_registry.register("continuous", ContinuousWatcher)
    watch_handler_registry.register("custom", CustomWatchHandler)
    CustomWatchHandler.calls = 0
    yield
    watcher_registry.unregister("one_shot")
    watcher_registry.unregister("continuous")
    watch_handler_registry.unregister("custom")


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


async def test_run_watch_delegates_request_to_handler() -> None:
    await run_watch(
        "default",
        RunOptions(
            watchers=["one_shot"],
            watch_handler="custom",
            no_save=True,
            watch_queue_size=1,
            watch_max_concurrent=1,
        ),
    )

    assert CustomWatchHandler.calls == 1


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
