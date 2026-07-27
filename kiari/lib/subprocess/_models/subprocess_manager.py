import asyncio
import logging
from collections.abc import AsyncIterator
from datetime import UTC, datetime

from .._operations.cancel_subprocess import cancel_subprocess
from .._operations.run_subprocess import run_subprocess
from .._settings import SubprocessSettings
from .._types.cancel_options import CancelOptions
from .._types.run_id import RunId
from .._types.subprocess_event import SubprocessEvent
from .subprocess_session import SubprocessSession

logger = logging.getLogger(__name__)


class SubprocessManager:
    def __init__(self, settings: SubprocessSettings):
        self.settings: SubprocessSettings = settings
        self._sessions: dict[RunId, SubprocessSession] = {}
        self._cleanup_task: asyncio.Task[None] | None = None

    # --------------------------------------------------
    # Properties
    # --------------------------------------------------

    @property
    def sessions(self) -> dict[RunId, SubprocessSession]:
        return self._sessions.copy()

    # --------------------------------------------------
    # Methods (run)
    # --------------------------------------------------

    async def run(
        self,
        argv: list[str],
        *,
        cwd: str | None = None,
        env: dict[str, str] | None = None,
        input_data: str | None = None,
        wait_time: float | None = None,
    ) -> AsyncIterator[SubprocessEvent]:
        """
        Execute the given argument vector and stream its events.

        The process runs in the foreground (streaming) until ``wait_time`` seconds
        elapse, then moves to the background. Pass ``wait_time=0.0`` to run it in
        the background from the start.
        """
        session = self._create_session(
            argv=argv,
            cwd=cwd,
            env=env,
            input_data=input_data,
            wait_time=wait_time,
        )

        async for event in self._run_subprocess(session):
            yield event

    # --------------------------------------------------
    # Methods (session management)
    # --------------------------------------------------

    def get_session(self, run_id: RunId) -> SubprocessSession | None:
        return self._sessions.get(run_id)

    async def cancel_run(
        self,
        run_id: str,
        *,
        options: CancelOptions | None = None,
    ) -> None:
        session = self.get_session(run_id)

        if session is not None:
            await cancel_subprocess(session, options=options)

    def cleanup_completed_sessions(self) -> None:
        current_time = datetime.now(UTC)
        cleanup_threshold = self.settings.cleanup_completed_sessions_after

        to_remove: list[RunId] = []

        for run_id, session in self._sessions.items():
            if (
                session.completed
                and session.completed_at
                and (current_time - session.completed_at).total_seconds() > cleanup_threshold
            ):
                to_remove.append(run_id)

        for run_id in to_remove:
            del self._sessions[run_id]

        if to_remove:
            logger.info(f"🗑️ Cleaned up completed sessions: {len(to_remove)}")

    def terminate_all_sessions(self) -> None:
        """
        Terminate all sessions

        This method only synchronously kills processes and does not wait for complete termination.
        This design prioritizes speed during application shutdown.
        Complete process termination and resource cleanup are delegated to the OS.
        If you need to guarantee complete termination, use cancel_run() individually.
        """
        if not self._sessions:
            return

        logger.info(f"🛑 Terminating all sessions: {len(self._sessions)}")

        # Cancel running sessions
        # Note: Do not wait() after kill(), delegate resource cleanup to the OS
        for session in self._sessions.values():
            if not session.completed and session.process:
                try:
                    session.process.kill()
                    session.mark_cancelled()
                except Exception:
                    pass

        self._sessions.clear()

        # Stop cleanup task
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()

    # --------------------------------------------------
    # Private Methods
    # --------------------------------------------------

    def _create_session(
        self,
        argv: list[str],
        *,
        cwd: str | None = None,
        env: dict[str, str] | None = None,
        input_data: str | None = None,
        wait_time: float | None = None,
    ) -> SubprocessSession:
        if wait_time is None:
            wait_time = self.settings.wait_time

        session = SubprocessSession(
            settings=self.settings,
            argv=argv,
            cwd=cwd,
            env=env,
            input_data=input_data,
            wait_time=wait_time,
            encoding=self.settings.encoding,
        )

        return session

    async def _run_subprocess(
        self,
        session: SubprocessSession,
    ) -> AsyncIterator[SubprocessEvent]:
        self._sessions[session.run_id] = session

        self._ensure_cleanup_task()

        async for result in run_subprocess(session):
            yield result

    def _ensure_cleanup_task(self) -> None:
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def _cleanup_loop(self) -> None:
        try:
            while True:
                await asyncio.sleep(self.settings.cleanup_loop_interval)
                self.cleanup_completed_sessions()
        except asyncio.CancelledError:
            pass
