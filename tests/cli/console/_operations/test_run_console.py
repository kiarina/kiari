from contextlib import asynccontextmanager

from rich.console import Console

from kiari.cli.console._operations import run_console as run_console_module
from kiari.cli.console.console_handler import ConsoleSession
from kiari.core.profile import RunOptions


async def test_no_interactive_terminal_error(
    console: Console,
) -> None:
    await run_console_module.run_console("default", RunOptions())
    output = console.export_text()
    assert "No interactive" in output


async def test_unknown_command_returns_to_user_input(
    console: Console,
    monkeypatch,
    session: ConsoleSession,
) -> None:
    class Handler:
        @asynccontextmanager
        async def handle_session(self):
            yield session

        def render_ui(self, session: ConsoleSession):
            return None

    input_count = 0

    async def read_keyboard_input(*args):
        nonlocal input_count
        input_count += 1

        if input_count == 1:
            session.text = "/missing"
            return "command"

        raise KeyboardInterrupt

    monkeypatch.setattr(run_console_module, "has_interactive_tty", lambda: True)
    monkeypatch.setattr(
        run_console_module.console_handler_registry,
        "resolve",
        lambda *args, **kwargs: Handler(),
    )
    monkeypatch.setattr(run_console_module, "_read_keyboard_input", read_keyboard_input)

    await run_console_module.run_console("default", RunOptions())

    assert input_count == 2
    assert "Unknown console command: /missing" in console.export_text()
