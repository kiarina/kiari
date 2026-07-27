from datetime import timedelta

import pytest

from kiari.cli.schedule.schedule_handler import BaseScheduleHandler, ScheduleSession
from kiari.core.profile import RunOptions
from kiari.lib.watcher import WatchEvent


class ReraisingScheduleHandler(BaseScheduleHandler):
    async def _on_request_error(
        self,
        session: ScheduleSession,
        error: Exception,
    ) -> None:
        raise error


async def test_handle_watch_event_marks_asap() -> None:
    handler = BaseScheduleHandler("default", RunOptions(no_load=True))

    async with handler.handle_session(interval="1h", cron=None) as session:
        await handler.handle_watch_event(WatchEvent(watcher_name="test", text="hello"), session)

        assert session.is_asap is True
        assert len(session.watch_events) == 1


async def test_handle_session_creates_scheduler() -> None:
    handler = BaseScheduleHandler("default", RunOptions(no_load=True))

    async with handler.handle_session(interval="1h", cron=None) as session:
        assert session.scheduler.schedule_type == "interval"
        assert session.schedule_type == "interval"
        assert session.scheduled_time == session.actual_time


async def test_handle_schedule_skip_if_no_events() -> None:
    handler = BaseScheduleHandler(
        "default",
        RunOptions(skip_if_no_events=True, no_load=True),
    )

    async with handler.handle_session(interval="1h", cron=None) as session:
        scheduled_time = session.scheduled_time

        assert await handler.handle_schedule(session) is False
        assert session.scheduled_time > scheduled_time


async def test_handle_schedule_returns_true_when_due() -> None:
    handler = BaseScheduleHandler("default", RunOptions(no_load=True))

    async with handler.handle_session(interval="1h", cron=None) as session:
        scheduled_time = session.scheduled_time

        assert await handler.handle_schedule(session) is True
        assert session.scheduled_time > scheduled_time


async def test_handle_schedule_returns_false_when_not_due() -> None:
    handler = BaseScheduleHandler("default", RunOptions(no_load=True))

    async with handler.handle_session(interval="1h", cron=None) as session:
        session.scheduled_time = session.actual_time + timedelta(hours=1)

        assert await handler.handle_schedule(session) is False


async def test_handle_request_adds_watch_events() -> None:
    handler = BaseScheduleHandler("default", RunOptions(no_load=True))

    async with handler.handle_session(interval="1h", cron=None) as session:
        session.add_watch_event(WatchEvent(watcher_name="test", text="hello"))

        async with handler.handle_request(session):
            assert session.history.events[-1].to_text().endswith("hello")

        assert session.watch_events == []


async def test_handle_request_keeps_events_added_during_request() -> None:
    handler = BaseScheduleHandler("default", RunOptions(no_load=True))

    async with handler.handle_session(interval="1h", cron=None) as session:
        session.add_watch_event(WatchEvent(watcher_name="test", text="before"))

        async with handler.handle_request(session):
            session.add_watch_event(WatchEvent(watcher_name="test", text="during"))

        assert [event.text for event in session.watch_events] == ["during"]


async def test_handle_request_suppresses_errors() -> None:
    handler = BaseScheduleHandler("default", RunOptions(no_load=True))

    async with handler.handle_session(interval="1h", cron=None) as session:
        session.add_watch_event(WatchEvent(watcher_name="test", text="before"))

        async with handler.handle_request(session):
            raise RuntimeError("boom")

        assert session.watch_events == []


async def test_handle_request_error_hook_can_reraise() -> None:
    handler = ReraisingScheduleHandler("default", RunOptions(no_load=True))

    async with handler.handle_session(interval="1h", cron=None) as session:
        with pytest.raises(RuntimeError, match="boom"):
            async with handler.handle_request(session):
                raise RuntimeError("boom")
