import asyncio
import logging
from contextlib import suppress

from kiarina.agi.agent import run_agent

from kiari.cli import graceful_shutdown
from kiari.cli.schedule.schedule_handler import (
    ScheduleHandler,
    ScheduleSession,
    schedule_handler_registry,
)
from kiari.core.profile import ProfileName, RunOptions
from kiari.lib.watcher import Watcher, watcher_registry

logger = logging.getLogger(__name__)


async def run_schedule(
    profile_name: ProfileName,
    run_options: RunOptions,
    *,
    stop_event: asyncio.Event | None = None,
) -> None:
    schedule_handler = schedule_handler_registry.resolve(
        run_options.schedule_handler,
        profile_name=profile_name,
        run_options=run_options,
    )

    watchers = [watcher_registry.resolve(watcher) for watcher in run_options.watchers]

    watcher_tasks: list[asyncio.Task[None]] = []

    with graceful_shutdown(stop_event) as stop_event:
        try:
            async with schedule_handler.handle_session(
                interval=run_options.interval,
                cron=run_options.cron,
            ) as session:
                watcher_tasks = [
                    asyncio.create_task(
                        _watcher_loop(watcher, schedule_handler, session, stop_event)
                    )
                    for watcher in watchers
                ]

                while not stop_event.is_set():
                    if await schedule_handler.handle_schedule(session):
                        async with schedule_handler.handle_request(session):
                            async for event in run_agent(**session.as_run_agent_kwargs()):
                                await schedule_handler.on_agent_event(session, event)
                                session.last_event = event

                    with suppress(TimeoutError):
                        await asyncio.wait_for(stop_event.wait(), timeout=1.0)

        finally:
            for watcher_task in watcher_tasks:
                watcher_task.cancel()

            if watcher_tasks:
                await asyncio.gather(*watcher_tasks, return_exceptions=True)


async def _watcher_loop(
    watcher: Watcher,
    schedule_handler: ScheduleHandler,
    session: ScheduleSession,
    stop_event: asyncio.Event,
) -> None:
    try:
        async for watch_event in watcher.watch(stop_event):
            if stop_event.is_set():
                break

            logger.debug(f"Received watch event: {watch_event}")
            await schedule_handler.handle_watch_event(watch_event, session)

    except Exception as e:
        logger.error(f"Watcher loop error: {e}", exc_info=True)
