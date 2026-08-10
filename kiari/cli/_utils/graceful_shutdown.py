import asyncio
import signal
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from types import FrameType
from typing import Any

from kiari.core.rich import console_registry

type SignalHandler = Callable[[int, FrameType | None], Any] | int | None


@contextmanager
def graceful_shutdown(stop_event: asyncio.Event | None = None) -> Iterator[asyncio.Event]:
    stop_event = stop_event if stop_event is not None else asyncio.Event()
    previous_sigint_handler: SignalHandler = signal.getsignal(signal.SIGINT)

    def signal_handler(signum: int, frame: FrameType | None) -> None:
        if not stop_event.is_set():
            stop_event.set()
            console_registry.get().print(
                "\n[yellow]Graceful shutdown requested. "
                "Waiting for current tasks to complete...[/yellow]"
            )
        else:
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            console_registry.get().print("\n[red]Force shutdown...[/red]")
            raise KeyboardInterrupt

    signal.signal(signal.SIGINT, signal_handler)

    try:
        yield stop_event
    finally:
        signal.signal(signal.SIGINT, previous_sigint_handler)
