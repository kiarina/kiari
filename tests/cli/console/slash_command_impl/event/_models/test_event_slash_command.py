import pytest
from kiarina.agi.message import AIMessage, HumanMessage
from rich.console import Console

from kiari.cli.console.console_handler import ConsoleSession
from kiari.cli.console.slash_command_impl.event import EventSlashCommand


class FakeQuestion:
    def __init__(self, selected):
        self.selected = selected

    async def ask_async(self):
        return self.selected


@pytest.fixture
def command(run_options):
    command = EventSlashCommand("default", run_options)
    command.name = "event"
    return command


def test_get_description(
    console: Console,
    session: ConsoleSession,
    command: EventSlashCommand,
) -> None:
    console.print(command.get_description(session))
    output = console.export_text()
    assert len(output.strip()) > 0


async def test_help(
    console: Console,
    session: ConsoleSession,
    command: EventSlashCommand,
) -> None:
    state = await command.run(session, [], "")
    output = console.export_text()

    assert state == "user"
    assert "/event list" in output


async def test_empty(
    session: ConsoleSession,
    command: EventSlashCommand,
) -> None:
    state = await command.run(session, ["list"], "")
    assert state == "user"


async def test_list(
    console: Console,
    command: EventSlashCommand,
    session: ConsoleSession,
) -> None:
    session.history.add_message(HumanMessage.create("first"))
    session.history.add_message(AIMessage.create("second"))

    state = await command.run(session, ["list"], "")
    output = console.export_text()

    assert state == "user"
    assert "0: human_message first" in output
    assert "1: ai_message second" in output


async def test_add_help(
    console: Console,
    command: EventSlashCommand,
    session: ConsoleSession,
) -> None:
    state = await command.run(session, ["add"], "")
    assert state == "user"


async def test_add(
    command: EventSlashCommand,
    session: ConsoleSession,
) -> None:
    state = await command.run(
        session,
        ["add", "hello"],
        "world",
    )

    assert state == "user"
    assert len(session.history.events) == 2


async def test_remove_cancel(
    monkeypatch: pytest.MonkeyPatch,
    command: EventSlashCommand,
    session: ConsoleSession,
) -> None:
    session.history.add_message(HumanMessage.create("first"))
    session.history.add_message(AIMessage.create("second"))

    def fake_checkbox(*args, **kwargs):
        return FakeQuestion(None)

    monkeypatch.setattr("questionary.checkbox", fake_checkbox)

    state = await command.run(session, ["remove"], "")
    assert state == "user"
    assert len(session.history.events) == 2


async def test_remove(
    monkeypatch: pytest.MonkeyPatch,
    command: EventSlashCommand,
    session: ConsoleSession,
) -> None:
    session.history.add_message(HumanMessage.create("first"))
    session.history.add_message(AIMessage.create("second"))

    def fake_checkbox(*args, **kwargs):
        return FakeQuestion([0])

    monkeypatch.setattr("questionary.checkbox", fake_checkbox)

    state = await command.run(session, ["remove"], "")
    assert state == "user"
    assert len(session.history.events) == 1


async def test_show_cancel(
    monkeypatch: pytest.MonkeyPatch,
    command: EventSlashCommand,
    session: ConsoleSession,
) -> None:
    session.history.add_message(HumanMessage.create("first"))

    def fake_select(*args, **kwargs):
        return FakeQuestion(None)

    monkeypatch.setattr("questionary.select", fake_select)

    state = await command.run(session, ["show"], "")
    assert state == "user"


async def test_show(
    monkeypatch: pytest.MonkeyPatch,
    command: EventSlashCommand,
    session: ConsoleSession,
) -> None:
    session.history.add_message(HumanMessage.create("first"))

    def fake_select(*args, **kwargs):
        return FakeQuestion(0)

    monkeypatch.setattr("questionary.select", fake_select)

    state = await command.run(session, ["show"], "")
    assert state == "user"


async def test_edit_cancel_select(
    monkeypatch: pytest.MonkeyPatch,
    command: EventSlashCommand,
    session: ConsoleSession,
) -> None:
    session.history.add_message(HumanMessage.create("first"))

    def fake_select(*args, **kwargs):
        return FakeQuestion(0)

    monkeypatch.setattr("questionary.select", fake_select)

    state = await command.run(session, ["edit"], "")
    assert state == "user"


async def test_edit_cancel_edit(
    monkeypatch: pytest.MonkeyPatch,
    command: EventSlashCommand,
    session: ConsoleSession,
) -> None:
    session.history.add_message(HumanMessage.create("first"))

    def fake_select(*args, **kwargs):
        return FakeQuestion(0)

    async def fake_edit_text(*args, **kwargs):
        return None

    monkeypatch.setattr("questionary.select", fake_select)

    monkeypatch.setattr(
        "kiari.core.editor._helpers.edit_text_with_validation.edit_text",
        fake_edit_text,
    )

    state = await command.run(session, ["edit"], "")
    assert state == "user"


async def test_edit_no_change(
    monkeypatch: pytest.MonkeyPatch,
    command: EventSlashCommand,
    session: ConsoleSession,
) -> None:
    session.history.add_message(HumanMessage.create("first"))

    def fake_select(*args, **kwargs):
        return FakeQuestion(0)

    async def fake_edit_text(*args, **kwargs):
        return args[0]

    monkeypatch.setattr("questionary.select", fake_select)

    monkeypatch.setattr(
        "kiari.core.editor._helpers.edit_text_with_validation.edit_text",
        fake_edit_text,
    )

    state = await command.run(session, ["edit"], "")
    assert state == "user"


async def test_edit_validation_error(
    monkeypatch: pytest.MonkeyPatch,
    setup_run_context,
    command: EventSlashCommand,
    session: ConsoleSession,
) -> None:
    session.history.add_message(HumanMessage.create("first"))

    count = 0

    def fake_select(*args, **kwargs):
        nonlocal count
        count += 1

        match count:
            case 1:
                return FakeQuestion(0)
            case 2:
                return FakeQuestion("abort")
            case _:
                raise AssertionError("Too many iterations in test_edit_validation_error")

    async def fake_edit_text(*args, **kwargs):
        return "invalid"

    monkeypatch.setattr("questionary.select", fake_select)

    monkeypatch.setattr(
        "kiari.core.editor._helpers.edit_text_with_validation.edit_text",
        fake_edit_text,
    )

    state = await command.run(session, ["edit"], "")
    assert state == "user"


async def test_edit(
    monkeypatch: pytest.MonkeyPatch,
    command: EventSlashCommand,
    session: ConsoleSession,
) -> None:
    session.history.add_message(HumanMessage.create("first"))

    def fake_select(*args, **kwargs):
        return FakeQuestion(0)

    async def fake_edit_text(*args, **kwargs):
        return args[0].replace("first", "edited")

    monkeypatch.setattr("questionary.select", fake_select)

    monkeypatch.setattr(
        "kiari.core.editor._helpers.edit_text_with_validation.edit_text",
        fake_edit_text,
    )

    state = await command.run(session, ["edit"], "")
    assert state == "user"
    assert "edited" in session.history.events[0].to_text()


async def test_unknown_command(
    command: EventSlashCommand,
    session: ConsoleSession,
) -> None:
    state = await command.run(session, ["unknown"], "")
    assert state == "user"
