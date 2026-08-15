import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime
from zoneinfo import ZoneInfo

from kiarina.agi.cost_recorder import cost_recorder_registry
from kiarina.agi.event import Event
from kiarina.agi.event_builder import build_event
from kiarina.agi.run_context import RunContext
from kiarina.utils.file import MarkdownContent

from kiari.core.file_info_source import resolve_file_info_specifiers
from kiari.core.profile import ProfileName, RunOptions
from kiari.core.runtime import create_agi_options, setup_history
from kiari.lib.history_repository import HistoryRepository, history_repository_registry
from kiari.lib.watcher import WatchEvent

from ...scheduler import Scheduler, create_scheduler
from .._schemas.schedule_session import ScheduleSession
from .._types.schedule_handler import ScheduleHandler
from .._types.schedule_handler_name import ScheduleHandlerName

logger = logging.getLogger(__name__)


class BaseScheduleHandler(ScheduleHandler):
    def __init__(self, profile_name: ProfileName, run_options: RunOptions) -> None:
        self.profile_name: ProfileName = profile_name
        self.run_options: RunOptions = run_options
        self._name: ScheduleHandlerName | None = None

    @property
    def name(self) -> ScheduleHandlerName:
        if not self._name:  # pragma: no cover
            raise AssertionError("ScheduleHandler name not set")

        return self._name

    @name.setter
    def name(self, value: ScheduleHandlerName) -> None:
        self._name = value

    @property
    def should_clear_watch_events_on_completed(self) -> bool:
        return True

    @property
    def should_clear_watch_events_on_error(self) -> bool:
        return True

    @property
    def history_repository(self) -> HistoryRepository:
        return history_repository_registry.resolve(self.run_options.history_repository)

    @asynccontextmanager
    async def handle_session(
        self,
        interval: str | None,
        cron: str | None,
    ) -> AsyncGenerator[ScheduleSession, None]:
        now = self._now()
        scheduler = create_scheduler(
            interval=interval,
            cron=cron,
            current_time=now,
        )
        scheduled_time = (
            now if scheduler.schedule_type == "interval" else scheduler.get_next_time(now)
        )
        session = await self._create_session(
            scheduler=scheduler,
            scheduled_time=scheduled_time,
            actual_time=now,
        )

        try:
            yield session

        except Exception as e:
            logger.error(f"Schedule session failed: {e}", exc_info=True)
            await self._on_session_error(session, e)
            raise

        else:
            logger.debug("Schedule session completed")
            await self._on_session_completed(session)

        finally:
            await session.cost_recorder.flush(session.run_context)
            await self._on_session_finish(session)

    async def handle_watch_event(
        self,
        watch_event: WatchEvent,
        session: ScheduleSession,
    ) -> None:
        logger.debug(
            f"Handling watch event from watcher '{watch_event.watcher_name}' in schedule handler"
        )
        await self._handle_watch_event(watch_event, session)

    async def handle_schedule(self, session: ScheduleSession) -> bool:
        now = self._now()

        if now < session.scheduled_time and not session.is_asap:
            return False

        session.is_asap = False
        session.actual_time = now
        session.scheduled_time = session.scheduler.get_next_time(now)

        if self.run_options.skip_if_no_events and not session.watch_events:
            logger.debug("Skipping schedule execution: no events are available")
            logger.info("Agent execution skipped by schedule handler")
            return False

        return True

    @asynccontextmanager
    async def handle_request(
        self,
        session: ScheduleSession,
    ) -> AsyncGenerator[None, None]:
        error: Exception | None = None
        watch_events = list(session.watch_events)

        await self._add_watch_events(session, watch_events)

        try:
            yield

        except Exception as e:
            error = e
            logger.error(f"Schedule request failed: {e}", exc_info=True)
            await self._on_request_error(session, e)

        else:
            logger.debug("Schedule request completed")
            await self._on_request_completed(session)

        finally:
            await session.cost_recorder.flush(session.run_context)
            await self._on_request_finish(session)

            if error is None:
                if self.should_clear_watch_events_on_completed:
                    session.clear_watch_events(watch_events)
            elif self.should_clear_watch_events_on_error:
                session.clear_watch_events(watch_events)

    async def on_agent_event(self, session: ScheduleSession, event: Event) -> None:
        if not event.transient:
            if not self.run_options.no_save:
                await self.history_repository.save(
                    session.history,
                    run_context=session.run_context,
                )

        await self._on_agent_event(session, event)

    # --------------------------------------------------
    # Template methods (Session)
    # --------------------------------------------------

    async def _create_session(
        self,
        scheduler: Scheduler,
        scheduled_time: datetime,
        actual_time: datetime,
    ) -> ScheduleSession:
        run_context = RunContext()

        history = await setup_history(self.run_options, run_context)

        return ScheduleSession(
            scheduler=scheduler,
            scheduled_time=scheduled_time,
            actual_time=actual_time,
            history=history,
            **create_agi_options(self.run_options),
            cost_recorder=cost_recorder_registry.resolve(),
            run_context=run_context,
        )

    def _now(self) -> datetime:
        return datetime.now(ZoneInfo(RunContext().time_zone))

    async def _on_session_completed(self, session: ScheduleSession) -> None:
        pass

    async def _on_session_error(
        self,
        session: ScheduleSession,
        error: Exception,
    ) -> None:
        pass

    async def _on_session_finish(self, session: ScheduleSession) -> None:
        pass

    # --------------------------------------------------
    # Template methods (Watcher)
    # --------------------------------------------------

    async def _handle_watch_event(
        self,
        watch_event: WatchEvent,
        session: ScheduleSession,
    ) -> None:
        session.add_watch_event(watch_event)
        session.mark_asap()

    # --------------------------------------------------
    # Template methods (Schedule)
    # --------------------------------------------------

    async def _add_watch_events(
        self,
        session: ScheduleSession,
        watch_events: list[WatchEvent],
    ) -> None:
        for watch_event in watch_events:
            markdown_content = MarkdownContent.from_text(watch_event.text)
            local_time = watch_event.created_at.astimezone(session.zone_info)
            text_parts = [f"[Event created at: {local_time.isoformat()}]"]

            if markdown_content.content:
                text_parts.append(markdown_content.content)

            text = "\n".join(text_parts)

            session.history.add_event(
                await build_event(
                    {
                        "text": text,
                        "files": await resolve_file_info_specifiers(watch_event.attachments),
                    },
                    run_context=session.run_context,
                )
            )

    async def _on_request_completed(self, session: ScheduleSession) -> None:
        pass

    async def _on_request_error(
        self,
        session: ScheduleSession,
        error: Exception,
    ) -> None:
        pass

    async def _on_request_finish(self, session: ScheduleSession) -> None:
        pass

    # --------------------------------------------------
    # Template methods (Agent)
    # --------------------------------------------------

    async def _on_agent_event(self, session: ScheduleSession, event: Event) -> None:
        pass
