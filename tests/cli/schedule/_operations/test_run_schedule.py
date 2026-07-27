import asyncio
import signal
from collections.abc import AsyncIterator
from datetime import UTC, datetime

import pytest

from kiari.cli.schedule._operations.run_schedule import run_schedule
from kiari.cli.schedule.scheduler import create_scheduler, parse_duration
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


@pytest.fixture(autouse=True)
def cleanup():
    watcher_registry.register("one_shot", OneShotWatcher)
    watcher_registry.register("continuous", ContinuousWatcher)
    yield
    watcher_registry.unregister("one_shot")
    watcher_registry.unregister("continuous")


def test_parse_duration() -> None:
    assert parse_duration("5s") == 5
    assert parse_duration("5m") == 300
    assert parse_duration("1h") == 3600
    assert parse_duration("1d") == 86400
    assert parse_duration("7") == 7


def test_create_scheduler_requires_trigger() -> None:
    with pytest.raises(ValueError, match="requires --interval or --cron"):
        create_scheduler(
            interval=None,
            cron=None,
            current_time=datetime.now(UTC),
        )


def test_create_scheduler_rejects_multiple_triggers() -> None:
    with pytest.raises(ValueError, match="either --interval or --cron"):
        create_scheduler(
            interval="5m",
            cron="0 * * * *",
            current_time=datetime.now(UTC),
        )


async def test_run_schedule() -> None:
    await run_schedule(
        "default",
        RunOptions(
            interval="1h",
            watchers=["one_shot"],
            chat_model="mock",
            no_save=True,
            skip_if_no_events=True,
        ),
    )


async def test_graceful_shutdown() -> None:
    task = asyncio.create_task(
        run_schedule(
            "default",
            RunOptions(
                interval="1h",
                watchers=["continuous"],
                chat_model="mock",
                no_save=True,
                skip_if_no_events=True,
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
        run_schedule(
            "default",
            RunOptions(
                interval="1h",
                watchers=["continuous"],
                chat_model="mock",
                no_save=True,
                skip_if_no_events=True,
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
