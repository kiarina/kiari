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

from .._schemas.batch_request import BatchRequest
from .._schemas.batch_session import BatchSession
from .._types.batch_handler import BatchHandler
from .._types.batch_handler_name import BatchHandlerName

logger = logging.getLogger(__name__)


class BaseBatchHandler(BatchHandler):
    def __init__(self, profile_name: ProfileName, run_options: RunOptions) -> None:
        self.profile_name: ProfileName = profile_name
        self.run_options: RunOptions = run_options
        self._name: BatchHandlerName | None = None

    @property
    def name(self) -> BatchHandlerName:
        if not self._name:  # pragma: no cover
            raise AssertionError("BatchHandler name not set")

        return self._name

    @name.setter
    def name(self, value: BatchHandlerName) -> None:
        self._name = value

    @property
    def history_repository(self) -> HistoryRepository:
        return history_repository_registry.resolve(self.run_options.history_repository)

    @asynccontextmanager
    async def handle_request(self, request: BatchRequest) -> AsyncIterator[BatchSession]:
        session = await self._create_session(request)

        try:
            yield session

        except Exception as e:
            logger.error(
                f"Batch execution failed: {e}",
                exc_info=True,
            )
            await self._on_request_error(session, e)
            raise

        else:
            logger.debug("Batch completed")
            await self._on_request_completed(session)

        finally:
            await session.cost_recorder.flush(session.run_context)
            await self._on_request_finish(session)

    async def on_agent_event(self, session: BatchSession, event: Event) -> None:
        if not event.transient:
            if not self.run_options.no_save:
                await self.history_repository.save(session.history, run_context=session.run_context)

        await self._on_agent_event(session, event)

    # --------------------------------------------------
    # Template methods (Request)
    # --------------------------------------------------

    async def _create_session(self, request: BatchRequest) -> BatchSession:
        run_context = RunContext()

        history = await setup_history(self.run_options, run_context)

        new_event = await build_event(
            {
                "text": request.text,
                "files": await resolve_file_info_specifiers(request.attachments),
            },
            run_context=run_context,
        )

        history.add_event(new_event)

        return BatchSession(
            history=history,
            **create_agi_options(self.run_options),
            cost_recorder=cost_recorder_registry.resolve(),
            run_context=run_context,
        )

    async def _on_request_completed(self, session: BatchSession) -> None:
        pass

    async def _on_request_error(self, session: BatchSession, error: Exception) -> None:
        pass

    async def _on_request_finish(self, session: BatchSession) -> None:
        pass

    # --------------------------------------------------
    # Template methods (Agent)
    # --------------------------------------------------

    async def _on_agent_event(self, session: BatchSession, event: Event) -> None:
        pass
