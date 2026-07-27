import asyncio
import os
import signal
from typing import TYPE_CHECKING

from .._models.subprocess_session import SubprocessSession
from .._types.cancel_options import CancelOptions

# Import Windows-specific constants only during type checking
if TYPE_CHECKING or os.name == "nt":
    try:
        # Only available in Windows environment
        CTRL_BREAK_EVENT = signal.CTRL_BREAK_EVENT  # type: ignore
    except AttributeError:
        # Set a dummy value for Unix environments where it doesn't exist
        CTRL_BREAK_EVENT = 1


async def cancel_subprocess(
    session: SubprocessSession,
    *,
    options: CancelOptions | None = None,
) -> None:
    """
    Terminate a running process and its child processes.

    By targeting the entire process group, child processes are also reliably terminated.
    On Windows, the process is launched with CREATE_NEW_PROCESS_GROUP, and handled in the
    following order: graceful shutdown via CTRL_BREAK_EVENT → taskkill /T /F on timeout.
    """
    options = options or {}

    force = options.get("force", False)
    timeout = options.get("timeout", 3.0)

    if not session.process or session.completed:
        return

    # Double-check if the process has already terminated
    if session.process.returncode is not None:
        if session.process.returncode == 0:
            session.mark_success(session.process.returncode)
        else:
            session.mark_failure(session.process.returncode)
        return

    # Set the cancellation request flag
    session.cancel_requested = True

    try:
        pid = session.process.pid

        if os.name == "nt":
            # Windows: CTRL_BREAK_EVENT → wait → taskkill /T /F
            await _cancel_windows(session, force=force, timeout=timeout)
        else:
            # Unix: Target the entire process group
            if force:
                # Force termination: Send SIGKILL to the entire process group
                await _kill_process_group(pid, signal.SIGKILL)
            else:
                # Normal termination: First send SIGTERM
                await _kill_process_group(pid, signal.SIGTERM)

                try:
                    # Wait for normal termination within the specified time
                    await asyncio.wait_for(session.process.wait(), timeout=timeout)
                except TimeoutError:
                    # Force termination on timeout
                    await _kill_process_group(pid, signal.SIGKILL)

            # Ensure the process termination is awaited
            await session.process.wait()

    except Exception:
        # Even if an error occurs, attempt to terminate the process
        try:
            session.process.kill()
            await session.process.wait()
        except Exception:
            pass

    finally:
        # Finalize the state
        if not session.completed:
            session.mark_cancelled(session.process.returncode)


async def _kill_process_group(pid: int, sig: int) -> None:
    """
    Send a signal to the entire process group.

    Args:
        pid: Process ID
        sig: Signal to send
    """
    try:
        # Send signal to the entire process group
        # By specifying a negative PID, target the process group
        os.killpg(os.getpgid(pid), sig)
    except (OSError, ProcessLookupError):
        # If the process group doesn't exist, target the individual process
        try:
            os.kill(pid, sig)
        except (OSError, ProcessLookupError):
            # If the process itself doesn't exist, do nothing
            pass


async def _cancel_windows(
    session: SubprocessSession,
    *,
    force: bool,
    timeout: float,
) -> None:
    """
    Cancellation process for Windows.

    - graceful shutdown: Send CTRL_BREAK_EVENT (assumes CREATE_NEW_PROCESS_GROUP)
    - On wait timeout/failure: Force terminate with taskkill /T /F including child processes
    """
    proc = session.process
    if not proc:
        return

    pid = proc.pid

    if force:
        await _taskkill_tree(pid, force=True)
        return

    # First, attempt graceful shutdown by sending CTRL_BREAK_EVENT
    sent = False
    try:
        proc.send_signal(CTRL_BREAK_EVENT)
        sent = True
    except Exception:
        # Cases where signal cannot be sent (no console/insufficient permissions, etc.)
        sent = False

    if sent:
        try:
            await asyncio.wait_for(proc.wait(), timeout=timeout)
            return
        except TimeoutError:
            # Force termination on timeout
            pass

    # If CTRL_BREAK_EVENT cannot be sent or doesn't complete in time, force terminate including child processes
    await _taskkill_tree(pid, force=True)


async def _taskkill_tree(pid: int, *, force: bool) -> None:
    """
    Terminate a process tree using taskkill (Windows only).
    """
    args = ["taskkill", "/PID", str(pid), "/T"]
    if force:
        args.append("/F")

    try:
        p = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await p.wait()
    except Exception:
        # If taskkill is not available, do nothing
        # (Individual process kill() is handled by the caller)
        pass
