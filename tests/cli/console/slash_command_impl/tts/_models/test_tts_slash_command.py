import pytest
from rich.console import Console

from kiari.cli.console.console_handler import ConsoleSession
from kiari.cli.console.slash_command_impl.tts import TTSSlashCommand


@pytest.fixture
def command(run_options):
    command = TTSSlashCommand("default", run_options)
    command.name = "tts"
    return command


def test_get_description(
    console: Console,
    session: ConsoleSession,
    command: TTSSlashCommand,
) -> None:
    console.print(command.get_description(session))
    output = console.export_text()
    assert len(output.strip()) > 0


async def test_toggle(
    command: TTSSlashCommand,
    session: ConsoleSession,
) -> None:
    state = await command.run(session, [], "")
    assert state == "user"
    assert session.tts_enabled is True

    state = await command.run(session, [], "")
    assert state == "user"
    assert session.tts_enabled is False


async def test_turn_on(
    command: TTSSlashCommand,
    session: ConsoleSession,
) -> None:
    state = await command.run(session, ["on"], "")

    assert state == "user"
    assert session.tts_enabled is True


async def test_turn_off(
    command: TTSSlashCommand,
    session: ConsoleSession,
) -> None:
    session.tts_enabled = True

    state = await command.run(session, ["off"], "")

    assert state == "user"
    assert session.tts_enabled is False
