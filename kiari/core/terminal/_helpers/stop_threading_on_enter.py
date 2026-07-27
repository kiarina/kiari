import asyncio
import sys
import threading
from collections.abc import Iterator
from contextlib import contextmanager


@contextmanager
def stop_threading_on_enter() -> Iterator[threading.Event]:
    stop_event = threading.Event()
    loop = asyncio.get_running_loop()
    fileno = sys.stdin.fileno()
    reader_registered = False

    def stop() -> None:
        sys.stdin.readline()
        stop_event.set()

    try:
        loop.add_reader(fileno, stop)
        reader_registered = True
    except (NotImplementedError, OSError, ValueError):
        pass

    try:
        yield stop_event
    finally:
        if reader_registered:
            try:
                loop.remove_reader(fileno)
            except (NotImplementedError, OSError, ValueError):
                pass
