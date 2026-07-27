import pytest
from kiarina.agi.event import CustomEvent
from kiarina.agi.message import AIMessage, HumanMessage
from rich.console import Console

from kiari.cli.console.console_handler import ConsoleSession
from kiari.cli.console.slash_command_impl.copy import CopySlashCommand


@pytest.fixture
def command(run_options):
    command = CopySlashCommand("default", run_options)
    command.name = "copy"
    return command


@pytest.fixture
def copied(monkeypatch) -> list[str]:
    copied: list[str] = []
    monkeypatch.setattr("pyperclip.copy", copied.append)
    return copied


@pytest.fixture
def session(session: ConsoleSession) -> ConsoleSession:
    session.history.add_message(HumanMessage.create("first"))
    session.history.add_message(AIMessage.create("second"))
    session.history.add_message(HumanMessage.create("third"))
    session.history.add_event(CustomEvent.create(type="note"))
    return session


def test_get_description(
    console: Console,
    session: ConsoleSession,
    command: CopySlashCommand,
) -> None:
    console.print(command.get_description(session))
    output = console.export_text()
    assert len(output.strip()) > 0


async def test_copy_empty(
    session: ConsoleSession,
    command: CopySlashCommand,
    copied: list[str],
) -> None:
    session.history.clear()
    state = await command.run(session, [], "")

    assert state == "user"
    assert copied == []


async def test_copy(
    session: ConsoleSession,
    command: CopySlashCommand,
    copied: list[str],
) -> None:
    state = await command.run(session, [], "")

    assert state == "user"
    assert len(copied) == 1
    assert "HUMAN MESSAGE" in copied[0]
    assert "first" in copied[0]
    assert "AI MESSAGE" in copied[0]
    assert "second" in copied[0]
    assert "CUSTOM EVENT" in copied[0]
    assert "note" in copied[0]


async def test_copy_target_and_range(
    session: ConsoleSession,
    command: CopySlashCommand,
    copied: list[str],
) -> None:
    state = await command.run(session, ["h", "1:"], "")

    assert state == "user"
    assert len(copied) == 1
    assert "first" not in copied[0]
    assert "second" not in copied[0]
    assert "third" in copied[0]
    assert "CUSTOM EVENT" not in copied[0]


async def test_copy_invalid_range(
    session: ConsoleSession,
    command: CopySlashCommand,
    copied: list[str],
) -> None:
    state = await command.run(session, ["*", "invalid"], "")

    assert state == "user"
    assert copied == []


async def test_copy_without_matching_events(
    session: ConsoleSession,
    command: CopySlashCommand,
    copied: list[str],
) -> None:
    session.history.clear()
    session.history.add_message(HumanMessage.create("hello"))

    state = await command.run(session, ["a"], "")

    assert state == "user"
    assert copied == []
