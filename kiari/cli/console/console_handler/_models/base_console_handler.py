import asyncio
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from kiarina.agi.cost_recorder import cost_recorder_registry
from kiarina.agi.event import Event, ToolMessageEvent
from kiarina.agi.event_builder import build_event
from kiarina.agi.run_context import RunContext
from rich.console import RenderableType
from rich.text import Text

from kiari.cli.console.console_renderer import (
    render_console_hint,
    render_console_status,
)
from kiari.core.file_info_source import resolve_file_info_specifiers
from kiari.core.profile import ProfileName, RunOptions
from kiari.core.rich import join_renderables
from kiari.core.runtime import create_agi_options, setup_history
from kiari.lib.history_repository import HistoryRepository, history_repository_registry

from .._schemas.console_request import ConsoleRequest
from .._schemas.console_session import ConsoleSession
from .._types.console_handler import ConsoleHandler
from .._types.console_handler_name import ConsoleHandlerName

logger = logging.getLogger(__name__)


class BaseConsoleHandler(ConsoleHandler):
    def __init__(self, profile_name: ProfileName, run_options: RunOptions) -> None:
        self.profile_name: ProfileName = profile_name
        self.run_options: RunOptions = run_options
        self._name: ConsoleHandlerName | None = None

    @property
    def name(self) -> ConsoleHandlerName:
        if not self._name:  # pragma: no cover
            raise AssertionError("ConsoleHandler name not set")

        return self._name

    @name.setter
    def name(self, value: ConsoleHandlerName) -> None:
        self._name = value

    @property
    def history_repository(self) -> HistoryRepository:
        return history_repository_registry.resolve(self.run_options.history_repository)

    @asynccontextmanager
    async def handle_session(self) -> AsyncGenerator[ConsoleSession, None]:
        session = await self._create_session()

        try:
            yield session

        except Exception as e:
            logger.error(f"Console session failed: {e}", exc_info=True)
            await self._on_session_error(session, e)
            raise

        else:
            logger.debug("Console session completed")
            await self._on_session_completed(session)

        finally:
            await session.cost_recorder.flush(session.run_context)
            await self._on_session_finish(session)

    @asynccontextmanager
    async def handle_request(
        self,
        session: ConsoleSession,
        request: ConsoleRequest,
    ) -> AsyncGenerator[None, None]:
        await self._update_session(session, request)

        try:
            yield

        except asyncio.CancelledError as e:
            logger.warning(f"Console request cancelled: {e}", exc_info=True)
            await self._on_agent_cancelled(session)
            raise

        except Exception as e:
            logger.error(f"Console request failed: {e}", exc_info=True)
            await self._on_request_error(session, e)
            raise

        else:
            logger.debug("Console request completed")
            await self._on_request_completed(session)

        finally:
            session.clear_buffer()
            await session.cost_recorder.flush(session.run_context)
            await self._on_request_finish(session)

    def render_ui(self, session: ConsoleSession) -> RenderableType | None:
        return join_renderables(
            [
                self._render_status(session),
                self._render_hint(),
            ],
            separator=Text(),
        )

    async def on_agent_event(self, session: ConsoleSession, event: Event) -> None:
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

    async def _create_session(self) -> ConsoleSession:
        run_context = RunContext()

        history = await setup_history(self.run_options, run_context)

        return ConsoleSession(
            history=history,
            **create_agi_options(self.run_options),
            cost_recorder=cost_recorder_registry.resolve(),
            run_context=run_context,
            tts_enabled=self.run_options.tts,
            stt_enabled=self.run_options.stt,
        )

    async def _on_session_completed(self, session: ConsoleSession) -> None:
        pass

    async def _on_session_error(self, session: ConsoleSession, error: Exception) -> None:
        pass

    async def _on_session_finish(self, session: ConsoleSession) -> None:
        pass

    # --------------------------------------------------
    # Template methods (Request)
    # --------------------------------------------------

    async def _update_session(
        self,
        session: ConsoleSession,
        request: ConsoleRequest,
    ) -> None:
        if not request.text and not request.attachments:
            return

        for tool_call in session.history.get_pending_tool_calls():
            session.history.add_event(
                ToolMessageEvent.create(
                    f"The tool call was rejected by the user: {tool_call.name}",
                    tool_call_id=tool_call.id,
                    tool_name=tool_call.name,
                )
            )

        session.history.add_event(
            await build_event(
                {
                    "text": request.text,
                    "files": await resolve_file_info_specifiers(request.attachments),
                },
                run_context=session.run_context,
            )
        )

    async def _on_request_completed(self, session: ConsoleSession) -> None:
        pass

    async def _on_request_error(
        self,
        session: ConsoleSession,
        error: Exception,
    ) -> None:
        pass

    async def _on_request_finish(self, session: ConsoleSession) -> None:
        pass

    # --------------------------------------------------
    # Template methods (Render UI)
    # --------------------------------------------------

    def _render_status(self, session: ConsoleSession) -> RenderableType | None:
        return render_console_status(
            session,
            profile_name=self.profile_name,
            run_options=self.run_options,
        )

    def _render_hint(self) -> RenderableType | None:
        return render_console_hint(self.run_options)

    # --------------------------------------------------
    # Template methods (Agent)
    # --------------------------------------------------

    async def _on_agent_event(self, session: ConsoleSession, event: Event) -> None:
        pass

    async def _on_agent_cancelled(self, session: ConsoleSession) -> None:
        pass
