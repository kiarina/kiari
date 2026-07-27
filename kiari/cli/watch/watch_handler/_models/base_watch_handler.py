import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from kiarina.agi.cost_recorder import cost_recorder_registry
from kiarina.agi.event import Event
from kiarina.agi.event_builder import build_event
from kiarina.agi.run_context import RunContext

from kiari.core.file_info_source import resolve_file_info_specifiers
from kiari.core.profile import ProfileName, RunOptions
from kiari.core.runtime import create_agi_options, setup_history
from kiari.lib.history_repository import HistoryRepository, history_repository_registry
from kiari.lib.watcher import WatchEvent

from .._schemas.watch_session import WatchSession
from .._types.watch_handler import WatchHandler
from .._types.watch_handler_name import WatchHandlerName

logger = logging.getLogger(__name__)


class BaseWatchHandler(WatchHandler):
    def __init__(self, profile_name: ProfileName, run_options: RunOptions) -> None:
        self.profile_name: ProfileName = profile_name
        self.run_options: RunOptions = run_options
        self._name: WatchHandlerName | None = None

    @property
    def name(self) -> WatchHandlerName:
        if not self._name:  # pragma: no cover
            raise AssertionError("WatchHandler name not set")

        return self._name

    @name.setter
    def name(self, value: WatchHandlerName) -> None:
        self._name = value

    @property
    def history_repository(self) -> HistoryRepository:
        return history_repository_registry.resolve(self.run_options.history_repository)

    @asynccontextmanager
    async def handle_event(
        self,
        watch_event: WatchEvent,
    ) -> AsyncIterator[WatchSession]:
        session = await self._create_session(watch_event)

        try:
            yield session

        except Exception as e:
            logger.error(f"Watch event failed: {e}", exc_info=True)
            await self._on_event_error(session, e)
            raise

        else:
            logger.debug("Watch event completed")
            await self._on_event_completed(session)

        finally:
            await session.cost_recorder.flush(session.run_context)
            await self._on_event_finish(session)

    async def on_agent_event(self, session: WatchSession, event: Event) -> None:
        if not event.transient:
            if not self.run_options.no_save:
                await self.history_repository.save(
                    session.history,
                    run_context=session.run_context,
                )

        await self._on_agent_event(session, event)

    async def on_queue_full(self, watch_event: WatchEvent) -> None:
        logger.warning(
            f"Watch queue is full. Dropping event from watcher '{watch_event.watcher_name}'"
        )
        await self._on_queue_full(watch_event)

    # --------------------------------------------------
    # Template methods (Event)
    # --------------------------------------------------

    async def _create_session(self, watch_event: WatchEvent) -> WatchSession:
        run_context = self._create_run_context(watch_event)
        history = await setup_history(self.run_options, run_context)

        if watch_event.text or watch_event.attachments:
            history.add_event(
                await build_event(
                    {
                        "text": watch_event.text,
                        "files": await resolve_file_info_specifiers(watch_event.attachments),
                    },
                    run_context=run_context,
                )
            )

        return WatchSession(
            watch_event=watch_event,
            history=history,
            **create_agi_options(self.run_options),
            cost_recorder=cost_recorder_registry.resolve(),
            run_context=run_context,
        )

    def _create_run_context(self, watch_event: WatchEvent) -> RunContext:
        return RunContext()

    async def _on_event_completed(self, session: WatchSession) -> None:
        pass

    async def _on_event_error(self, session: WatchSession, error: Exception) -> None:
        pass

    async def _on_event_finish(self, session: WatchSession) -> None:
        pass

    # --------------------------------------------------
    # Template methods (Agent)
    # --------------------------------------------------

    async def _on_agent_event(self, session: WatchSession, event: Event) -> None:
        pass

    # --------------------------------------------------
    # Template methods (Queue)
    # --------------------------------------------------

    async def _on_queue_full(self, watch_event: WatchEvent) -> None:
        pass
