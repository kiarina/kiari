import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import ClassVar

from .._enums.subprocess_status import SubprocessStatus
from .._settings import SubprocessSettings
from .._types.run_id import RunId
from .._utils.clean_ansi import clean_ansi


@dataclass
class SubprocessSession:
    """
    Model representing subprocess session information
    """

    Status: ClassVar[type[SubprocessStatus]] = SubprocessStatus

    # --------------------------------------------------
    # Fields
    # --------------------------------------------------

    settings: SubprocessSettings = field(default_factory=SubprocessSettings)

    run_id: RunId = field(default_factory=lambda: uuid.uuid4().hex)

    argv: list[str] = field(default_factory=list)
    """Executed argument vector (program followed by its arguments)"""

    cwd: str | None = None
    """Working directory (current directory of the caller if None)"""

    env: dict[str, str] | None = None
    """Environment variables merged onto the current environment (no merge if None)"""

    input_data: str | None = None
    """Data sent to standard input (stdin is closed immediately with EOF if None)"""

    wait_time: float = 60.0
    """Foreground wait time for commands (seconds)"""

    encoding: str = "utf-8"
    """Encoding"""

    process: asyncio.subprocess.Process | None = None
    """Process"""

    background_task: asyncio.Task[None] | None = None
    """Task that continues capturing output after foreground streaming ends"""

    buffer: bytearray = field(default_factory=bytearray)
    """Output buffer"""

    status: SubprocessStatus = SubprocessStatus.RUNNING
    """Execution status"""

    returncode: int | None = None
    """Exit code"""

    done_event: asyncio.Event = field(default_factory=asyncio.Event)
    """Completion event"""

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    """Creation time"""

    completed_at: datetime | None = None
    """Completion time"""

    cancel_requested: bool = False
    """Whether cancellation has been requested"""

    # --------------------------------------------------
    # Properties
    # --------------------------------------------------

    @property
    def completed(self) -> bool:
        return self.status in [
            SubprocessStatus.SUCCESS,
            SubprocessStatus.CANCELLED,
            SubprocessStatus.FAILURE,
        ]

    @property
    def cancelled(self) -> bool:
        return self.status == SubprocessStatus.CANCELLED

    @property
    def running(self) -> bool:
        return self.status == SubprocessStatus.RUNNING

    @property
    def duration(self) -> float:
        end_time = self.completed_at or datetime.now(UTC)
        return (end_time - self.created_at).total_seconds()

    # --------------------------------------------------
    # Methods
    # --------------------------------------------------

    def append(self, data: bytes) -> None:
        """
        Add data to the output buffer
        """
        # Add data to buffer
        self.buffer.extend(data)

        # Keep only the tail portion if buffer exceeds max size
        if len(self.buffer) > self.settings.max_buffer_size:
            self.buffer = self.buffer[-self.settings.max_buffer_size :]

    def get_output(self) -> str:
        """
        Get the output up to the current point
        """
        raw_text = bytes(self.buffer).decode(self.encoding, errors="replace")
        raw_text = clean_ansi(raw_text)
        return raw_text

    def mark_success(self, returncode: int | None = None) -> None:
        """
        Mark the session as successful
        """
        if not self.completed:
            self.status = SubprocessStatus.SUCCESS
            self.returncode = returncode
            self.completed_at = datetime.now(UTC)
            self.done_event.set()

    def mark_cancelled(self, returncode: int | None = None) -> None:
        """
        Mark the session as cancelled
        """
        if not self.completed:
            self.status = SubprocessStatus.CANCELLED
            self.returncode = returncode
            self.completed_at = datetime.now(UTC)
            self.done_event.set()

    def mark_failure(self, returncode: int | None = None) -> None:
        """
        Mark the session as failed
        """
        if not self.completed:
            self.status = SubprocessStatus.FAILURE
            self.returncode = returncode
            self.completed_at = datetime.now(UTC)
            self.done_event.set()

    async def wait_for_completion(self, timeout: float | None = None) -> bool:
        """
        Wait for the session to complete

        Returns True if the session has completed.
        """
        if self.completed:
            return True

        try:
            await asyncio.wait_for(self.done_event.wait(), timeout=timeout)
            return True
        except TimeoutError:
            return False
