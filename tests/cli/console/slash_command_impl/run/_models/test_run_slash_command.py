import pytest
from rich.console import Console

from kiari.cli.console.console_handler import ConsoleSession
from kiari.cli.console.slash_command_impl.run import RunSlashCommand


@pytest.fixture
def command(run_options):
    command = RunSlashCommand("default", run_options)
    command.name = "run"
    return command


def test_get_description(
    console: Console,
    session: ConsoleSession,
    command: RunSlashCommand,
) -> None:
    console.print(command.get_description(session))
    output = console.export_text()
    assert len(output.strip()) > 0


async def test_run(
    command: RunSlashCommand,
    session: ConsoleSession,
) -> None:
    state = await command.run(session, [], "hello")

    assert state == "agent"
    assert session.text == "hello"
    assert session.max_iterations is None
    assert session.until_end is None
    assert session.until_tool_calls is None
    assert session.until_tool_runs is None


async def test_set_max_iterations(
    command: RunSlashCommand,
    session: ConsoleSession,
) -> None:
    state = await command.run(session, ["10"], "")

    assert state == "agent"
    assert session.max_iterations == 10


async def test_set_until_end(
    command: RunSlashCommand,
    session: ConsoleSession,
) -> None:
    state = await command.run(session, ["--until-end"], "")

    assert state == "agent"
    assert session.until_end is True


async def test_set_until_tool_calls(
    command: RunSlashCommand,
    session: ConsoleSession,
) -> None:
    state = await command.run(
        session,
        ["--until-tool-call", "hello", "--until-tool-call", "world"],
        "",
    )

    assert state == "agent"
    assert session.until_tool_calls == ["hello", "world"]


async def test_set_until_tool_runs(
    command: RunSlashCommand,
    session: ConsoleSession,
) -> None:
    state = await command.run(
        session,
        ["--until-tool-run", "hello", "--until-tool-run", "world"],
        "",
    )

    assert state == "agent"
    assert session.until_tool_runs == ["hello", "world"]


async def test_set_complex_conditions(
    command: RunSlashCommand,
    session: ConsoleSession,
) -> None:
    state = await command.run(
        session,
        [
            "10",
            "--until-end",
            "--until-tool-call",
            "hello",
            "--until-tool-call",
            "world",
            "--until-tool-run",
            "foo",
        ],
        "hello",
    )

    assert state == "agent"
    assert session.text == "hello"
    assert session.max_iterations == 10
    assert session.until_end is True
    assert session.until_tool_calls == ["hello", "world"]
    assert session.until_tool_runs == ["foo"]


async def test_reject_invalid_args(
    command: RunSlashCommand,
    session: ConsoleSession,
) -> None:
    state = await command.run(session, ["hello"], "content")

    assert state == "user"
    assert session.text == ""
    assert session.max_iterations is None


async def test_reject_missing_value(
    command: RunSlashCommand,
    session: ConsoleSession,
) -> None:
    state = await command.run(session, ["--until-tool-call"], "")

    assert state == "user"
    assert session.until_tool_calls is None


async def test_reject_option_as_missing_value(
    command: RunSlashCommand,
    session: ConsoleSession,
) -> None:
    state = await command.run(
        session,
        ["--until-tool-run", "--until-end"],
        "",
    )

    assert state == "user"
    assert session.until_end is None
    assert session.until_tool_runs is None
