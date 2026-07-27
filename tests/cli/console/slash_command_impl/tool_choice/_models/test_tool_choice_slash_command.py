import pytest
from kiarina.agi.tool_info import ToolInfo
from rich.console import Console

from kiari.cli.console.console_handler import ConsoleSession
from kiari.cli.console.slash_command_impl.tool_choice import ToolChoiceSlashCommand


class FakeQuestion:
    def __init__(self, selected):
        self.selected = selected

    async def ask_async(self):
        return self.selected


@pytest.fixture
def command(run_options):
    command = ToolChoiceSlashCommand("default", run_options)
    command.name = "tool_choice"
    return command


@pytest.fixture
def session(session: ConsoleSession) -> ConsoleSession:
    session.history.add_tool_info(ToolInfo(name="hello", description="Say hello"))
    session.history.add_tool_info(ToolInfo(name="wait", description="Wait"))
    return session


def test_get_description(
    console: Console,
    session: ConsoleSession,
    command: ToolChoiceSlashCommand,
) -> None:
    console.print(command.get_description(session))
    output = console.export_text()
    assert len(output.strip()) > 0


async def test_select(
    command: ToolChoiceSlashCommand,
    session: ConsoleSession,
    monkeypatch,
) -> None:
    def fake_select(*args, **kwargs):
        assert kwargs["choices"] == ["auto", "any", "hello", "wait"]
        assert kwargs["default"] == "auto"
        return FakeQuestion("hello")

    monkeypatch.setattr("questionary.select", fake_select)

    state = await command.run(session, [], "")

    assert state == "user"
    assert session.chat_options.get("tool_choice") == "hello"


async def test_select_cancelled(
    command: ToolChoiceSlashCommand,
    session: ConsoleSession,
    monkeypatch,
) -> None:
    def fake_select(*args, **kwargs):
        return FakeQuestion(None)

    monkeypatch.setattr("questionary.select", fake_select)
    session.chat_options["tool_choice"] = "hello"

    state = await command.run(session, [], "")

    assert state == "user"
    assert session.chat_options.get("tool_choice") == "hello"


async def test_direct_auto(
    command: ToolChoiceSlashCommand,
    session: ConsoleSession,
) -> None:
    state = await command.run(session, ["auto"], "")

    assert state == "user"
    assert session.chat_options.get("tool_choice") == "auto"
