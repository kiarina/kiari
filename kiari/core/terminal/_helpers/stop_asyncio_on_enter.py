import asyncio
import sys
from collections.abc import Iterator
from contextlib import contextmanager


@contextmanager
def stop_asyncio_on_enter() -> Iterator[asyncio.Event]:
    stop_event = asyncio.Event()
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
