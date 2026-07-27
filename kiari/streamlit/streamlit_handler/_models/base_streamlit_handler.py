import logging
import threading
from collections.abc import AsyncIterator
from typing import Any, ClassVar

from kiarina.agi.agent import run_agent
from kiarina.agi.cost_recorder import cost_recorder_registry
from kiarina.agi.event import Event, ToolMessageEvent
from kiarina.agi.event_builder import build_event
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool import tool_registry

from kiari.core.file_info_source import resolve_file_info_specifiers
from kiari.core.profile import ProfileName, RunOptions
from kiari.core.runtime import create_agi_options, setup_history
from kiari.lib.history_repository import HistoryRepository, history_repository_registry
from kiari.streamlit import StreamlitIdentity

from .._schemas.streamlit_request import StreamlitRequest
from .._schemas.streamlit_session import StreamlitSession
from .._types.streamlit_handler import StreamlitHandler
from .._types.streamlit_handler_name import StreamlitHandlerName

logger = logging.getLogger(__name__)

_SESSION_CONFIG_FIELDS = {
    "agent",
    "file_limits",
    "max_iterations",
    "until_end",
    "until_tool_calls",
    "until_tool_runs",
    "tools",
    "default_tool_state",
    "pre_hooks",
    "post_hooks",
    "workflow",
    "prompt",
    "prompt_limits",
    "system_messages",
    "chat_model",
    "tool_choice",
    "parallel_tool_calls",
    "streaming",
    "tts",
    "tts_model",
    "stt",
    "asr_model",
}


class AgentBusyError(RuntimeError):
    pass


class BaseStreamlitHandler(StreamlitHandler):
    _agent_locks: ClassVar[dict[str, threading.Lock]] = {}
    _agent_locks_guard: ClassVar[threading.Lock] = threading.Lock()

    def __init__(
        self,
        profile_name: ProfileName,
        run_options: RunOptions,
        **kwargs: Any,
    ) -> None:
        self.profile_name = profile_name
        self.run_options = run_options
        self.init_kwargs = kwargs
        self._name: StreamlitHandlerName | None = None

    @property
    def name(self) -> StreamlitHandlerName:
        if self._name is None:  # pragma: no cover
            raise AssertionError("StreamlitHandler name not set")
        return self._name

    @name.setter
    def name(self, value: StreamlitHandlerName) -> None:
        self._name = value

    def get_history_repository(self, run_options: RunOptions) -> HistoryRepository:
        return history_repository_registry.resolve(run_options.history_repository)

    async def create_session(
        self,
        identity: StreamlitIdentity,
        agent_id: str,
    ) -> StreamlitSession:
        run_context = RunContext(
            organization_id=self.run_options.organization_id,
            user_id=identity.user_id,
            agent_id=agent_id,
        )
        history = await setup_history(self.run_options, run_context)
        return StreamlitSession(
            run_options=self.run_options.model_copy(deep=True),
            history=history,
            **create_agi_options(self.run_options),
            cost_recorder=cost_recorder_registry.resolve(self.run_options.cost_recorder),
            run_context=run_context,
        )

    async def has_history(self, identity: StreamlitIdentity, agent_id: str) -> bool:
        context = RunContext(
            organization_id=self.run_options.organization_id,
            user_id=identity.user_id,
            agent_id=agent_id,
        )
        return await self.get_history_repository(self.run_options).load(context) is not None

    async def delete_history(self, session: StreamlitSession) -> None:
        lock = self._get_agent_lock(session.run_context.agent_id)
        if not lock.acquire(blocking=False):
            raise AgentBusyError("This agent is already running in another session")
        try:
            await self.get_history_repository(session.run_options).delete(session.run_context)
        finally:
            lock.release()

    async def refresh_history(self, session: StreamlitSession) -> None:
        if not session.run_options.no_load:
            session.history = await setup_history(session.run_options, session.run_context)

    async def run_request(
        self,
        session: StreamlitSession,
        request: StreamlitRequest,
    ) -> AsyncIterator[Event]:
        lock = self._get_agent_lock(session.run_context.agent_id)
        if not lock.acquire(blocking=False):
            raise AgentBusyError("This agent is already running in another session")

        try:
            await self.refresh_history(session)
            await self._add_request(session, request)
            session.last_event = None
            session.error = None

            try:
                async for event in run_agent(**session.as_run_agent_kwargs()):
                    if not event.transient and not session.run_options.no_save:
                        await self.get_history_repository(session.run_options).save(
                            session.history,
                            session.run_context,
                        )
                    await self._on_agent_event(session, event)
                    session.last_event = event
                    yield event
                if session.last_event is None:
                    raise RuntimeError("Agent completed without generating any events")
            except Exception as e:
                session.error = e
                logger.error("Streamlit agent request failed: %s", e, exc_info=True)
                await self._on_agent_error(session, e)
                raise
            finally:
                await session.cost_recorder.flush(session.run_context)
        finally:
            lock.release()

    async def apply_config(
        self,
        session: StreamlitSession,
        updates: dict[str, object],
    ) -> None:
        disallowed = sorted(set(updates) - _SESSION_CONFIG_FIELDS)
        if disallowed:
            raise ValueError(f"Run options cannot be changed in Streamlit: {', '.join(disallowed)}")

        new_run_options = RunOptions.model_validate({**session.run_options.model_dump(), **updates})
        old_tool_names = {_tool_name(value) for value in session.run_options.tools}
        new_tool_names = {_tool_name(value) for value in new_run_options.tools}

        for tool_info in session.history.tool_infos:
            if tool_info.name in old_tool_names - new_tool_names and tool_info.state == "active":
                tool_info.state = "disabled"
        for specifier in new_run_options.tools:
            name = _tool_name(specifier)
            if session.history.get_tool_info(name) is None:
                tool = tool_registry.resolve(specifier)
                tool_info = tool.to_tool_info(session.run_context.language)
                tool_info.state = new_run_options.default_tool_state
                session.history.add_tool_info(tool_info)

        session.run_options = new_run_options
        options = create_agi_options(new_run_options)
        session.chat_options = options["chat_options"]
        session.prompt_options = options["prompt_options"]
        session.workflow_options = options["workflow_options"]
        session.tool_options = options["tool_options"]
        session.agent_options = options["agent_options"]

        if not new_run_options.no_save:
            await self.get_history_repository(new_run_options).save(
                session.history,
                session.run_context,
            )

    async def back(self, session: StreamlitSession) -> bool:
        lock = self._get_agent_lock(session.run_context.agent_id)
        if not lock.acquire(blocking=False):
            raise AgentBusyError("This agent is already running in another session")
        try:
            await self.refresh_history(session)
            for index in range(len(session.history.events) - 1, -1, -1):
                if session.history.events[index].type == "human_message":
                    del session.history.events[index:]
                    if not session.run_options.no_save:
                        await self.get_history_repository(session.run_options).save(
                            session.history,
                            session.run_context,
                        )
                    return True
            return False
        finally:
            lock.release()

    async def clear(self, session: StreamlitSession) -> None:
        lock = self._get_agent_lock(session.run_context.agent_id)
        if not lock.acquire(blocking=False):
            raise AgentBusyError("This agent is already running in another session")
        try:
            session.history.events.clear()
            session.history.file_infos.clear()
            session.history.tool_infos.clear()
            session.history.metadata.clear()
            session.last_event = None
            if not session.run_options.no_save:
                await self.get_history_repository(session.run_options).delete(session.run_context)
        finally:
            lock.release()

    async def _add_request(
        self,
        session: StreamlitSession,
        request: StreamlitRequest,
    ) -> None:
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

    async def _on_agent_event(self, session: StreamlitSession, event: Event) -> None:
        pass

    async def _on_agent_error(self, session: StreamlitSession, error: Exception) -> None:
        pass

    @classmethod
    def _get_agent_lock(cls, agent_id: str) -> threading.Lock:
        with cls._agent_locks_guard:
            return cls._agent_locks.setdefault(agent_id, threading.Lock())


def _tool_name(specifier: str) -> str:
    return specifier.split("?", 1)[0]
