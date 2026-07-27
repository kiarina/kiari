import asyncio
import os
import subprocess
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any

from .._models.subprocess_session import SubprocessSession
from .._types.subprocess_event import SubprocessEvent
from .._views.background_event import BackgroundEvent
from .._views.finish_event import FinishEvent
from .._views.stream_event import StreamEvent

# Import Windows-specific constants only during type checking
if TYPE_CHECKING or os.name == "nt":
    try:
        # Available only in Windows environment
        CREATE_NEW_PROCESS_GROUP = subprocess.CREATE_NEW_PROCESS_GROUP  # type: ignore
    except AttributeError:
        # Set a dummy value for Unix environments where it doesn't exist
        CREATE_NEW_PROCESS_GROUP = 0


async def run_subprocess(session: SubprocessSession) -> AsyncIterator[SubprocessEvent]:
    # Start the process (create a new process group/session for each OS)
    extra_popen_kwargs: dict[str, Any] = {}

    if os.name == "nt":
        # Windows: Create a new process group (to send CTRL_BREAK_EVENT)
        extra_popen_kwargs["creationflags"] = CREATE_NEW_PROCESS_GROUP
    else:
        # Unix: Create a new session/PG (equivalent to setsid)
        extra_popen_kwargs["start_new_session"] = True
        extra_popen_kwargs["restore_signals"] = True

    # Merge the requested environment variables onto the current environment
    if session.env is not None:
        extra_popen_kwargs["env"] = {**os.environ, **session.env}

    program, *args = session.argv

    session.process = await asyncio.create_subprocess_exec(
        program,
        *args,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        cwd=session.cwd,
        **extra_popen_kwargs,
    )

    # Write data to stdin (close immediately with EOF if no input is provided)
    assert session.process.stdin is not None

    if session.input_data is not None:
        session.process.stdin.write(session.input_data.encode(session.encoding))

        try:
            await session.process.stdin.drain()
        except Exception:
            pass  # Continue even if drain fails

    session.process.stdin.close()

    # Foreground (streaming) loop
    loop = asyncio.get_running_loop()
    deadline = loop.time() + session.wait_time
    assert session.process.stdout is not None

    while True:
        # Check timeout
        remaining = deadline - loop.time()

        if remaining <= 0:
            # Move to background
            session.background_task = asyncio.create_task(_background_capture(session))
            yield BackgroundEvent(run_id=session.run_id)
            return

        # Read line (max 0.5 seconds or remaining timeout)
        read_timeout = min(0.5, max(0.0, remaining))
        line = await _read_with_timeout(session, read_timeout)

        if line:
            session.append(line)
            yield StreamEvent(
                run_id=session.run_id,
                output=line.decode(session.encoding, errors="replace"),
            )

        # Check for EOF / process termination
        if line == b"" and session.process.stdout.at_eof():
            await session.process.wait()

            if session.cancel_requested:
                session.mark_cancelled(session.process.returncode)
            elif session.process.returncode == 0:
                session.mark_success(session.process.returncode)
            else:
                session.mark_failure(session.process.returncode)

            yield FinishEvent(
                run_id=session.run_id,
                status=session.status,
                returncode=session.returncode,
            )
            return


async def _background_capture(session: SubprocessSession) -> None:
    """
    Continue reading output in the background and wait for process completion
    """
    try:
        if not session.process or not session.process.stdout:
            return

        while True:
            line = await session.process.stdout.readline()

            if not line:
                # This state also occurs when cancelled
                break

            session.append(line)

    except Exception:
        # Mark as failed if an error occurs
        session.mark_failure()

    finally:
        if session.process:
            # Wait for process termination
            await session.process.wait()

            if session.cancel_requested:
                session.mark_cancelled(session.process.returncode)
            elif session.process.returncode == 0:
                session.mark_success(session.process.returncode)
            else:
                session.mark_failure(session.process.returncode)


async def _read_with_timeout(
    session: SubprocessSession,
    timeout: float,
) -> bytes:
    """
    Read output with timeout
    """
    if not session.process or not session.process.stdout:
        return b""

    try:
        line = await asyncio.wait_for(session.process.stdout.readline(), timeout=timeout)
        return line

    except TimeoutError:
        return b""
