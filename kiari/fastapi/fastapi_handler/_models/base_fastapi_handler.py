import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import HTTPException, status
from kiarina.agi.cost_recorder import cost_recorder_registry
from kiarina.agi.event import CustomEvent, Event
from kiarina.agi.event_builder import build_event
from kiarina.agi.run_context import RunContext
from pydantic import TypeAdapter, ValidationError

from kiari.core.file_info_source import resolve_file_info_specifiers
from kiari.core.profile import ProfileName, RunOptions
from kiari.core.runtime import create_agi_options, setup_history
from kiari.fastapi._schemas.fastapi_session import FastAPISession
from kiari.fastapi.authenticator import authenticator_registry
from kiari.lib.history_repository import HistoryRepository, history_repository_registry

from .._schemas.fastapi_request import FastAPIRequest
from .._types.fastapi_handler import FastAPIHandler
from .._types.fastapi_handler_name import FastAPIHandlerName

logger = logging.getLogger(__name__)

_event_adapter: TypeAdapter[Event] = TypeAdapter(Event)

_REQUEST_CONFIG_FIELDS = {
    # History Repository
    "history_repository",
    "no_load",
    "no_save",
    "allow_active_missing_tools",
    # History
    "events",
    "file_infos",
    "tool_infos",
    "default_tool_state",
    # Agent
    "agent",
    "file_limits",
    "max_iterations",
    "until_end",
    "until_tool_calls",
    "until_tool_runs",
    # Tool
    "tools",
    "pre_hooks",
    "post_hooks",
    # Workflow
    "workflow",
    # Prompt
    "prompt",
    "prompt_limits",
    "system_messages",
    # Chat
    "chat_model",
    "tool_choice",
    "parallel_tool_calls",
    "streaming",
    # Cost Recorder
    "cost_recorder",
}

_RESERVED_RUN_KWARGS = {
    "history",
    "chat_options",
    "prompt_options",
    "workflow_options",
    "tool_options",
    "agent_options",
    "cost_recorder",
    "run_context",
    "stop_event",
}


class BaseFastAPIHandler(FastAPIHandler):
    def __init__(
        self,
        profile_name: ProfileName,
        run_options: RunOptions,
        **kwargs: Any,
    ) -> None:
        self.profile_name = profile_name
        self.run_options = run_options
        self.init_kwargs = kwargs
        self._name: FastAPIHandlerName | None = None

    @property
    def name(self) -> FastAPIHandlerName:
        if not self._name:  # pragma: no cover
            raise AssertionError("FastAPIHandler name not set")

        return self._name

    @name.setter
    def name(self, value: FastAPIHandlerName) -> None:
        self._name = value

    def get_history_repository(self, run_options: RunOptions) -> HistoryRepository:
        return history_repository_registry.resolve(run_options.history_repository)

    @asynccontextmanager
    async def handle_request(
        self,
        request: FastAPIRequest,
    ) -> AsyncGenerator[FastAPISession, None]:
        session = await self._create_session(request)

        try:
            yield session

        except Exception as e:
            session.error = e
            logger.error(f"FastAPI request failed: {e}", exc_info=True)
            await self._on_request_error(session, e)
            raise

        else:
            if session.error is None:
                await self._on_request_completed(session)
            else:
                await self._on_request_error(session, session.error)

        finally:
            await session.cost_recorder.flush(session.run_context)
            await self._on_request_finish(session)

    async def on_agent_event(
        self,
        session: FastAPISession,
        event: Event,
    ) -> Event | None:
        if not event.transient and not session.run_options.no_save:
            await self.get_history_repository(session.run_options).save(
                session.history,
                run_context=session.run_context,
            )

        return await self._on_agent_event(session, event)

    async def on_agent_completed(
        self,
        session: FastAPISession,
        final_event: Event,
    ) -> Event | None:
        return await self._on_agent_completed(session, final_event)

    async def on_agent_error(
        self,
        session: FastAPISession,
        error: Exception,
    ) -> Event | None:
        session.error = error
        logger.error(f"Agent execution failed in FastAPI mode: {error}", exc_info=True)
        return await self._on_agent_error(session, error)

    # --------------------------------------------------
    # Template methods (Request)
    # --------------------------------------------------

    async def _create_session(self, request: FastAPIRequest) -> FastAPISession:
        request_run_options = self._create_request_run_options(request)
        self._validate_run_kwargs(request.body.run_kwargs)
        events = self._parse_events(request.body.events)
        run_context = await self._authenticate(request)
        history = await setup_history(request_run_options, run_context)

        for event in events:
            history.add_event(event)

        if request.body.text or request.body.files:
            history.add_event(
                await build_event(
                    {
                        "text": request.body.text,
                        "files": await resolve_file_info_specifiers(request.body.files),
                    },
                    run_context=run_context,
                )
            )

        return FastAPISession(
            request_body=request.body,
            request_headers=request.headers,
            run_options=request_run_options,
            history=history,
            **create_agi_options(request_run_options),
            cost_recorder=cost_recorder_registry.resolve(request_run_options.cost_recorder),
            run_context=run_context,
            run_kwargs=request.body.run_kwargs,
        )

    def _create_request_run_options(self, request: FastAPIRequest) -> RunOptions:
        disallowed_fields = sorted(set(request.body.config) - _REQUEST_CONFIG_FIELDS)

        if disallowed_fields:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail={
                    "message": "Request config contains fields that cannot be overridden",
                    "fields": disallowed_fields,
                },
            )

        try:
            return RunOptions.model_validate(
                {
                    **self.run_options.model_dump(),
                    **request.body.config,
                }
            )
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=e.errors(),
            ) from e

    async def _authenticate(self, request: FastAPIRequest) -> RunContext:
        authenticator = authenticator_registry.resolve(self.run_options.fastapi_authenticator)
        return await authenticator.authenticate(request, self.run_options)

    def _validate_run_kwargs(self, run_kwargs: dict[str, Any]) -> None:
        reserved_fields = sorted(set(run_kwargs) & _RESERVED_RUN_KWARGS)

        if reserved_fields:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail={
                    "message": "run_kwargs contains reserved fields",
                    "fields": reserved_fields,
                },
            )

    def _parse_events(self, event_data: list[dict[str, Any]]) -> list[Event]:
        try:
            return [_event_adapter.validate_python(event) for event in event_data]
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=e.errors(),
            ) from e

    async def _on_request_completed(self, session: FastAPISession) -> None:
        pass

    async def _on_request_error(
        self,
        session: FastAPISession,
        error: Exception,
    ) -> None:
        pass

    async def _on_request_finish(self, session: FastAPISession) -> None:
        pass

    # --------------------------------------------------
    # Template methods (Agent)
    # --------------------------------------------------

    async def _on_agent_event(
        self,
        session: FastAPISession,
        event: Event,
    ) -> Event | None:
        return event

    async def _on_agent_completed(
        self,
        session: FastAPISession,
        final_event: Event,
    ) -> Event | None:
        return None

    async def _on_agent_error(
        self,
        session: FastAPISession,
        error: Exception,
    ) -> Event | None:
        return CustomEvent.create(
            type="error",
            message=str(error),
            error_type=type(error).__name__,
        )
