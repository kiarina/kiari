import pytest
from rich.console import Console

from kiari.cli.console.console_handler import ConsoleSession
from kiari.cli.console.slash_command_impl.stt import STTSlashCommand


@pytest.fixture
def command(run_options):
    command = STTSlashCommand("default", run_options)
    command.name = "stt"
    return command


def test_get_description(
    console: Console,
    session: ConsoleSession,
    command: STTSlashCommand,
) -> None:
    console.print(command.get_description(session))
    output = console.export_text()
    assert len(output.strip()) > 0


async def test_toggle(
    command: STTSlashCommand,
    session: ConsoleSession,
) -> None:
    state = await command.run(session, [], "")

    assert state == "user"
    assert session.stt_enabled is True

    state = await command.run(session, [], "")

    assert state == "user"
    assert session.stt_enabled is False


async def test_turn_on(
    command: STTSlashCommand,
    session: ConsoleSession,
) -> None:
    state = await command.run(session, ["on"], "")

    assert state == "user"
    assert session.stt_enabled is True


async def test_turn_off(
    command: STTSlashCommand,
    session: ConsoleSession,
) -> None:
    session.stt_enabled = True

    state = await command.run(session, ["off"], "")

    assert state == "user"
    assert session.stt_enabled is False
