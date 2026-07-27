import pytest
from kiarina.agi.file_info import FileInfo
from kiarina.agi.message import HumanMessage
from kiarina.agi.tool_info import ToolInfo
from rich.console import Console

from kiari.cli.console.console_handler import ConsoleSession
from kiari.cli.console.slash_command_impl.clear import ClearSlashCommand


@pytest.fixture
def command(run_options):
    command = ClearSlashCommand("default", run_options)
    command.name = "clear"
    return command


@pytest.fixture
def terminal_commands(monkeypatch) -> list[str]:
    called: list[str] = []

    def fake_system(command: str) -> int:
        called.append(command)
        return 0

    monkeypatch.setattr("os.system", fake_system)
    return called


@pytest.fixture
def session(session: ConsoleSession, text_file_info: FileInfo) -> ConsoleSession:
    session.history.add_message(HumanMessage.create("hello"))
    session.history.add_file_info(text_file_info)
    session.history.add_tool_info(ToolInfo(name="search", description="Search files."))
    session.history.metadata["key"] = "value"
    session.attachments.append("README.md")
    session.text = "hello"
    session.last_event = session.history.events[-1]
    return session


def test_get_description(
    console: Console,
    session: ConsoleSession,
    command: ClearSlashCommand,
) -> None:
    console.print(command.get_description(session))
    output = console.export_text()
    assert len(output.strip()) > 0


async def test_clear_all(
    command: ClearSlashCommand,
    session: ConsoleSession,
    terminal_commands: list[str],
) -> None:
    state = await command.run(session, [], "")

    assert state == "user"
    assert session.history.events == []
    assert session.history.file_infos == []
    assert session.history.tool_infos == []
    assert session.history.metadata == {}
    assert session.attachments == []
    assert session.text == ""
    assert session.last_event is None
    assert terminal_commands == ["clear"]


async def test_clear_targets(
    command: ClearSlashCommand,
    session: ConsoleSession,
    terminal_commands: list[str],
) -> None:
    file_info = session.history.file_infos[0]

    state = await command.run(session, ["em"], "")

    assert state == "user"
    assert session.history.events == []
    assert session.history.file_infos == [file_info]
    assert len(session.history.tool_infos) == 1
    assert session.history.metadata == {}
    assert session.attachments == []
    assert session.text == ""
    assert session.last_event is None
    assert terminal_commands == ["clear"]


async def test_clear_invalid_targets(
    command: ClearSlashCommand,
    session: ConsoleSession,
    terminal_commands: list[str],
) -> None:
    file_info = session.history.file_infos[0]

    state = await command.run(session, ["ex"], "")

    assert state == "user"
    assert len(session.history.events) == 1
    assert session.history.file_infos == [file_info]
    assert len(session.history.tool_infos) == 1
    assert session.history.metadata == {"key": "value"}
    assert session.attachments == ["README.md"]
    assert session.text == "hello"
    assert session.last_event is session.history.events[-1]
    assert terminal_commands == []
