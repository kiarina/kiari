import threading
from collections.abc import Callable

import kiari.core.terminal._helpers.stop_threading_on_enter as stop_threading_module
from kiari.core.terminal import stop_threading_on_enter


class FakeLoop:
    def __init__(self) -> None:
        self.callback: Callable[[], None] | None = None
        self.added_fd = None
        self.removed_fd = None

    def add_reader(self, fd, callback: Callable[[], None]) -> None:
        self.added_fd = fd
        self.callback = callback

    def remove_reader(self, fd) -> None:
        self.removed_fd = fd


class FakeStdin:
    def __init__(self) -> None:
        self.read = False

    def fileno(self) -> int:
        return 10

    def readline(self) -> str:
        self.read = True
        return "\n"


def test_stop_threading_on_enter_creates_threading_event(monkeypatch) -> None:
    loop = FakeLoop()
    stdin = FakeStdin()

    monkeypatch.setattr(
        stop_threading_module.asyncio,
        "get_running_loop",
        lambda: loop,
    )
    monkeypatch.setattr(stop_threading_module.sys, "stdin", stdin)

    with stop_threading_on_enter() as stop_event:
        assert isinstance(stop_event, threading.Event)
        assert loop.added_fd == 10

        assert loop.callback is not None
        loop.callback()

        assert stdin.read is True
        assert stop_event.is_set()

    assert loop.removed_fd == 10
