import pytest
from rich.console import Console

from kiari.cli.console.console_handler import ConsoleSession
from kiari.cli.console.slash_command_impl.help import HelpSlashCommand


@pytest.fixture
def command(run_options):
    command = HelpSlashCommand("default", run_options)
    command.name = "help"
    return command


def test_get_description(
    console: Console,
    session: ConsoleSession,
    command: HelpSlashCommand,
) -> None:
    console.print(command.get_description(session))
    output = console.export_text()
    assert len(output.strip()) > 0


async def test_no_filter(
    console: Console,
    session: ConsoleSession,
    command: HelpSlashCommand,
) -> None:
    state = await command.run(session, [], "")
    output = console.export_text()

    assert state == "user"
    assert "/clear" in output
    assert "/help" in output


async def test_filter(
    console: Console,
    session: ConsoleSession,
    command: HelpSlashCommand,
) -> None:
    state = await command.run(session, ["clear"], "")
    output = console.export_text()

    assert state == "user"
    assert "/clear" in output
    assert "/help" not in output
