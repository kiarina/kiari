import pytest
from kiarina.agi.message import AIMessage, ToolCall, ToolMessage
from rich.console import Console

from kiari.cli.console.console_handler import ConsoleSession
from kiari.cli.console.slash_command_impl.tool import ToolSlashCommand


class FakeQuestion:
    def __init__(self, selected):
        self.selected = selected

    async def ask_async(self):
        return self.selected


@pytest.fixture
def command(run_options):
    command = ToolSlashCommand("default", run_options)
    command.name = "tool"
    return command


def test_get_description(
    console: Console,
    session: ConsoleSession,
    command: ToolSlashCommand,
) -> None:
    console.print(command.get_description(session))
    output = console.export_text()
    assert len(output.strip()) > 0


async def test_help(
    session: ConsoleSession,
    command: ToolSlashCommand,
) -> None:
    state = await command.run(session, [], "")
    assert state == "user"


async def test_empty(
    session: ConsoleSession,
    command: ToolSlashCommand,
) -> None:
    state = await command.run(session, ["list"], "")
    assert state == "user"


async def test_list(
    console: Console,
    session: ConsoleSession,
    command: ToolSlashCommand,
) -> None:
    await command.run(session, ["add", "hello", "wait"], "")
    console.export_text(clear=True)

    state = await command.run(session, ["list"], "")
    output = console.export_text()

    assert state == "user"
    assert "0: hello" in output
    assert "1: wait" in output


async def test_add_select_cancel(
    monkeypatch: pytest.MonkeyPatch,
    session: ConsoleSession,
    command: ToolSlashCommand,
) -> None:
    def fake_checkbox(*args, **kwargs):
        return FakeQuestion(None)

    monkeypatch.setattr("questionary.checkbox", fake_checkbox)

    state = await command.run(session, ["add"], "")

    assert state == "user"
    assert session.tool_options.get("tools") is None


async def test_add_select(
    monkeypatch: pytest.MonkeyPatch,
    session: ConsoleSession,
    command: ToolSlashCommand,
) -> None:
    def fake_checkbox(*args, **kwargs):
        return FakeQuestion(["hello", "wait"])

    monkeypatch.setattr("questionary.checkbox", fake_checkbox)

    state = await command.run(session, ["add"], "")

    tools = session.tool_options.get("tools") or []
    assert state == "user"
    assert len(tools) == 2


async def test_add(
    console: Console,
    session: ConsoleSession,
    command: ToolSlashCommand,
) -> None:
    state = await command.run(session, ["add", "hello"], "wait")

    assert state == "user"
    assert len(session.tool_options.get("tools") or []) == 2


async def test_remove_cancel(
    monkeypatch: pytest.MonkeyPatch,
    console: Console,
    session: ConsoleSession,
    command: ToolSlashCommand,
) -> None:
    def fake_checkbox(*args, **kwargs):
        return FakeQuestion(None)

    monkeypatch.setattr("questionary.checkbox", fake_checkbox)

    await command.run(session, ["add", "hello"], "")
    console.export_text(clear=True)

    state = await command.run(session, ["remove"], "")
    assert state == "user"


async def test_remove(
    monkeypatch: pytest.MonkeyPatch,
    console: Console,
    session: ConsoleSession,
    command: ToolSlashCommand,
) -> None:
    def fake_checkbox(*args, **kwargs):
        return FakeQuestion([0])

    monkeypatch.setattr("questionary.checkbox", fake_checkbox)

    await command.run(session, ["add", "hello"], "")
    console.export_text(clear=True)

    session.history.add_message(AIMessage.create(tool_calls=[ToolCall(id="1", name="hello")]))
    session.history.add_message(ToolMessage.create("done", tool_name="hello", tool_call_id="1"))

    state = await command.run(session, ["remove"], "")

    assert state == "user"
    assert len(session.tool_options.get("tools") or []) == 0
    assert len(session.history.events) == 0
    assert session.history.tool_infos[0].state == "disabled"


async def test_unknown_subcommand(
    session: ConsoleSession,
    command: ToolSlashCommand,
) -> None:
    state = await command.run(session, ["foo"], "")
    assert state == "user"
