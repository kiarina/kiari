import pytest
from kiarina.agi.event import CustomEvent, ToolMessageEvent
from kiarina.agi.message import AIMessage, HumanMessage
from rich.console import Console

from kiari.cli.console.console_handler import ConsoleSession
from kiari.cli.console.slash_command_impl.show import ShowSlashCommand


@pytest.fixture
def command(run_options):
    command = ShowSlashCommand("default", run_options)
    command.name = "show"
    return command


@pytest.fixture
def session(session: ConsoleSession) -> ConsoleSession:
    session.history.add_message(HumanMessage.create("first human"))
    session.history.add_message(AIMessage.create("second ai"))
    session.history.add_event(
        ToolMessageEvent.create(
            "third tool",
            tool_name="search",
            tool_call_id="call-1",
        )
    )
    session.history.add_event(CustomEvent.create(type="fourth custom"))
    session.history.add_message(HumanMessage.create("fifth human"))
    return session


def test_get_description(
    console: Console,
    session: ConsoleSession,
    command: ShowSlashCommand,
) -> None:
    console.print(command.get_description(session))
    output = console.export_text()
    assert len(output.strip()) > 0


async def test_show(
    console: Console,
    session: ConsoleSession,
    command: ShowSlashCommand,
) -> None:
    state = await command.run(session, [], "")
    output = console.export_text()

    assert state == "user"
    assert "first human" in output
    assert "second ai" in output
    assert "third tool" in output
    assert "fourth custom" in output
    assert "fifth human" in output


async def test_show_target(
    console: Console,
    session: ConsoleSession,
    command: ShowSlashCommand,
) -> None:
    state = await command.run(session, ["h"], "")
    output = console.export_text()

    assert state == "user"
    assert "first human" in output
    assert "second ai" not in output
    assert "third tool" not in output
    assert "fourth custom" not in output
    assert "fifth human" in output


async def test_show_multiple_targets(
    console: Console,
    session: ConsoleSession,
    command: ShowSlashCommand,
) -> None:
    state = await command.run(session, ["ac"], "")
    output = console.export_text()

    assert state == "user"
    assert "first human" not in output
    assert "second ai" in output
    assert "third tool" not in output
    assert "fourth custom" in output
    assert "fifth human" not in output


async def test_show_invalid_target_defaults_to_all(
    console: Console,
    session: ConsoleSession,
    command: ShowSlashCommand,
) -> None:
    state = await command.run(session, ["x"], "")
    output = console.export_text()

    assert state == "user"
    assert "first human" in output
    assert "second ai" in output
    assert "third tool" in output
    assert "fourth custom" in output
    assert "fifth human" in output


async def test_show_range(
    console: Console,
    session: ConsoleSession,
    command: ShowSlashCommand,
) -> None:
    state = await command.run(session, ["h", "1:"], "")
    output = console.export_text()

    assert state == "user"
    assert "first human" not in output
    assert "second ai" not in output
    assert "third tool" not in output
    assert "fourth custom" not in output
    assert "fifth human" in output


async def test_show_invalid_range(
    console: Console,
    session: ConsoleSession,
    command: ShowSlashCommand,
) -> None:
    state = await command.run(session, ["*", "invalid"], "")
    output = console.export_text()

    assert state == "user"
    assert "Invalid range format: invalid" in output
    assert "first human" not in output


async def test_show_without_matching_events(
    console: Console,
    session: ConsoleSession,
    command: ShowSlashCommand,
) -> None:
    session.history.clear()
    session.history.add_message(HumanMessage.create("hello"))

    state = await command.run(session, ["a"], "")
    output = console.export_text()

    assert state == "user"
    assert "No matching events found" in output
    assert "hello" not in output


async def test_show_empty(
    console: Console,
    session: ConsoleSession,
    command: ShowSlashCommand,
) -> None:
    session.history.clear()
    state = await command.run(session, [], "")
    output = console.export_text()

    assert state == "user"
    assert "No history" in output
