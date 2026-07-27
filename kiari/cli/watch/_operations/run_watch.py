import asyncio
import logging

from kiarina.agi.agent import run_agent

from kiari.cli import graceful_shutdown
from kiari.core.profile import ProfileName, RunOptions
from kiari.core.rich import console_registry
from kiari.lib.watcher import Watcher, WatchEvent, watcher_registry

from ..watch_handler import WatchHandler, watch_handler_registry

logger = logging.getLogger(__name__)

type WatchEventQueue = asyncio.Queue[WatchEvent | None]


async def run_watch(profile_name: ProfileName, run_options: RunOptions) -> None:
    if not run_options.watchers:
        raise ValueError("Watch mode requires at least one watcher.")

    watch_handler = watch_handler_registry.resolve(
        run_options.watch_handler,
        profile_name=profile_name,
        run_options=run_options,
    )

    watchers = [watcher_registry.resolve(watcher) for watcher in run_options.watchers]

    pending_queue: WatchEventQueue = asyncio.Queue(maxsize=run_options.watch_queue_size)

    workers = [
        asyncio.create_task(_worker(watch_handler, pending_queue))
        for _ in range(run_options.watch_max_concurrent)
    ]

    with graceful_shutdown() as stop_event:
        watcher_tasks = [
            asyncio.create_task(
                _watcher_loop(
                    watcher,
                    watch_handler,
                    pending_queue,
                    stop_event,
                    run_options,
                )
            )
            for watcher in watchers
        ]

        await asyncio.gather(*watcher_tasks, return_exceptions=True)

        if pending_queue.qsize() > 0:
            console_registry.get().print(
                f"[blue]Waiting for {pending_queue.qsize()} pending events to complete...[/blue]"
            )
            await pending_queue.join()

        for _ in workers:
            await pending_queue.put(None)

        await asyncio.gather(*workers, return_exceptions=True)


async def _worker(
    watch_handler: WatchHandler,
    pending_queue: WatchEventQueue,
) -> None:
    while True:
        watch_event = await pending_queue.get()

        if watch_event is None:
            pending_queue.task_done()
            break

        try:
            async with watch_handler.handle_event(watch_event) as session:
                async for event in run_agent(**session.as_run_agent_kwargs()):
                    await watch_handler.on_agent_event(session, event)
                    session.last_event = event

        finally:
            pending_queue.task_done()


async def _watcher_loop(
    watcher: Watcher,
    watch_handler: WatchHandler,
    pending_queue: WatchEventQueue,
    stop_event: asyncio.Event,
    run_options: RunOptions,
) -> None:
    try:
        async for watch_event in watcher.watch(stop_event):
            if stop_event.is_set():
                break

            logger.debug(f"Received watch event: {watch_event}")

            try:
                await asyncio.wait_for(
                    pending_queue.put(watch_event),
                    timeout=run_options.watch_queue_put_timeout,
                )

            except TimeoutError:
                await watch_handler.on_queue_full(watch_event)

    except Exception as e:
        logger.error(f"Watcher loop error: {e}", exc_info=True)
