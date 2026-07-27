import pytest
from kiarina.agi.event import CustomEvent, ToolMessageEvent
from kiarina.agi.message import AIMessage, HumanMessage
from rich.console import Console

from kiari.cli.console.console_handler import ConsoleSession
from kiari.cli.console.slash_command_impl.back import BackSlashCommand


@pytest.fixture
def command(run_options):
    command = BackSlashCommand("default", run_options)
    command.name = "back"
    return command


def test_get_description(
    console: Console,
    session: ConsoleSession,
    command: BackSlashCommand,
) -> None:
    console.print(command.get_description(session))
    output = console.export_text()
    assert len(output.strip()) > 0


async def test_revert_human_message(
    command: BackSlashCommand,
    session: ConsoleSession,
) -> None:
    session.history.add_message(HumanMessage.create("first"))
    session.history.add_message(AIMessage.create("second"))
    session.history.add_message(HumanMessage.create("third"))
    session.history.add_message(AIMessage.create("fourth"))

    state = await command.run(session, [], "")

    assert state == "user"
    assert [event.to_text() for event in session.history.events] == [
        "first",
        "second",
    ]


async def test_revert_ai_message(
    command: BackSlashCommand,
    session: ConsoleSession,
) -> None:
    session.history.add_message(AIMessage.create("first"))
    session.history.add_event(
        ToolMessageEvent.create(
            "second",
            tool_name="search",
            tool_call_id="call-1",
        )
    )
    session.history.add_message(AIMessage.create("third"))
    session.history.add_event(
        ToolMessageEvent.create(
            "fourth",
            tool_name="search",
            tool_call_id="call-2",
        )
    )
    session.history.add_message(AIMessage.create("fifth"))
    session.history.add_event(
        ToolMessageEvent.create(
            "sixth",
            tool_name="search",
            tool_call_id="call-3",
        )
    )

    state = await command.run(session, [], "")

    assert state == "user"
    assert [event.to_text() for event in session.history.events] == [
        "first",
        "second",
        "third",
        "fourth",
    ]


async def test_revert_no_change(
    command: BackSlashCommand,
    session: ConsoleSession,
) -> None:
    session.history.add_event(CustomEvent.create(type="note"))

    state = await command.run(session, [], "")

    assert state == "user"
    assert [event.to_text() for event in session.history.events] == ["note"]


async def test_revert_empty(
    command: BackSlashCommand,
    session: ConsoleSession,
) -> None:
    state = await command.run(session, [], "")

    assert state == "user"
    assert session.history.events == []


async def test_delete_invalid_n(
    command: BackSlashCommand,
    session: ConsoleSession,
) -> None:
    session.history.add_message(HumanMessage.create("hello"))

    state = await command.run(session, ["hello"], "")

    assert state == "user"
    assert [event.to_text() for event in session.history.events] == ["hello"]


async def test_delete_non_positive_n(
    command: BackSlashCommand,
    session: ConsoleSession,
) -> None:
    session.history.add_message(HumanMessage.create("hello"))

    state = await command.run(session, ["0"], "")

    assert state == "user"
    assert [event.to_text() for event in session.history.events] == ["hello"]


async def test_delete_all(
    command: BackSlashCommand,
    session: ConsoleSession,
) -> None:
    session.history.add_message(HumanMessage.create("first"))
    session.history.add_message(AIMessage.create("second"))

    state = await command.run(session, ["2"], "")

    assert state == "user"
    assert session.history.events == []


async def test_delete(
    command: BackSlashCommand,
    session: ConsoleSession,
) -> None:
    session.history.add_message(HumanMessage.create("first"))
    session.history.add_message(AIMessage.create("second"))
    session.history.add_message(HumanMessage.create("third"))

    state = await command.run(session, ["2"], "")

    assert state == "user"
    assert [event.to_text() for event in session.history.events] == ["first"]
