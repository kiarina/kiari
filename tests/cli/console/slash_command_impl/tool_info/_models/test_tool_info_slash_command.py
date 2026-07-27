import pytest
from kiarina.agi.tool_info import ToolInfo
from rich.console import Console

from kiari.cli.console.console_handler import ConsoleSession
from kiari.cli.console.slash_command_impl.tool_info import ToolInfoSlashCommand


class FakeQuestion:
    def __init__(self, selected):
        self.selected = selected

    async def ask_async(self):
        return self.selected


@pytest.fixture
def command(run_options):
    command = ToolInfoSlashCommand("default", run_options)
    command.name = "tool_info"
    return command


def test_get_description(
    console: Console,
    session: ConsoleSession,
    command: ToolInfoSlashCommand,
) -> None:
    console.print(command.get_description(session))
    output = console.export_text()
    assert len(output.strip()) > 0


async def test_help(
    console: Console,
    session: ConsoleSession,
    command: ToolInfoSlashCommand,
) -> None:
    state = await command.run(session, [], "")
    output = console.export_text()

    assert state == "user"
    assert "/tool_info list" in output


async def test_empty(
    session: ConsoleSession,
    command: ToolInfoSlashCommand,
) -> None:
    state = await command.run(session, ["list"], "")
    assert state == "user"


async def test_list(
    console: Console,
    command: ToolInfoSlashCommand,
    session: ConsoleSession,
) -> None:
    session.history.add_tool_info(ToolInfo(name="first", description="First tool"))
    session.history.add_tool_info(ToolInfo(name="second", description="Second tool"))

    state = await command.run(session, ["list"], "")
    output = console.export_text()

    assert state == "user"
    assert "0: active first First tool" in output
    assert "1: active second Second tool" in output


async def test_add_help(
    command: ToolInfoSlashCommand,
    session: ConsoleSession,
) -> None:
    state = await command.run(session, ["add"], "")
    assert state == "user"


async def test_add(
    command: ToolInfoSlashCommand,
    session: ConsoleSession,
) -> None:
    state = await command.run(
        session,
        ["add", '{"name": "hello", "description": "Say hello"}'],
        '{"name": "wait", "description": "Wait"}',
    )

    assert state == "user"
    assert len(session.history.tool_infos) == 2


async def test_add_replace(
    command: ToolInfoSlashCommand,
    session: ConsoleSession,
) -> None:
    session.history.add_tool_info(ToolInfo(name="hello", description="Old description"))

    state = await command.run(
        session,
        [
            "add",
            '{"name": "hello", "description": "New description", "state": "inactive"}',
        ],
        "",
    )

    assert state == "user"
    assert len(session.history.tool_infos) == 1
    assert session.history.tool_infos[0].description == "New description"
    assert session.history.tool_infos[0].state == "inactive"


async def test_remove_cancel(
    monkeypatch: pytest.MonkeyPatch,
    command: ToolInfoSlashCommand,
    session: ConsoleSession,
) -> None:
    session.history.add_tool_info(ToolInfo(name="first", description="First tool"))
    session.history.add_tool_info(ToolInfo(name="second", description="Second tool"))

    def fake_checkbox(*args, **kwargs):
        return FakeQuestion(None)

    monkeypatch.setattr("questionary.checkbox", fake_checkbox)

    state = await command.run(session, ["remove"], "")
    assert state == "user"
    assert len(session.history.tool_infos) == 2


async def test_remove(
    monkeypatch: pytest.MonkeyPatch,
    command: ToolInfoSlashCommand,
    session: ConsoleSession,
) -> None:
    session.history.add_tool_info(ToolInfo(name="first", description="First tool"))
    session.history.add_tool_info(ToolInfo(name="second", description="Second tool"))

    def fake_checkbox(*args, **kwargs):
        return FakeQuestion([0])

    monkeypatch.setattr("questionary.checkbox", fake_checkbox)

    state = await command.run(session, ["remove"], "")
    assert state == "user"
    assert len(session.history.tool_infos) == 1


async def test_show_cancel(
    monkeypatch: pytest.MonkeyPatch,
    command: ToolInfoSlashCommand,
    session: ConsoleSession,
) -> None:
    session.history.add_tool_info(ToolInfo(name="hello", description="Say hello"))

    def fake_select(*args, **kwargs):
        return FakeQuestion(None)

    monkeypatch.setattr("questionary.select", fake_select)

    state = await command.run(session, ["show"], "")
    assert state == "user"


async def test_show(
    monkeypatch: pytest.MonkeyPatch,
    command: ToolInfoSlashCommand,
    session: ConsoleSession,
) -> None:
    session.history.add_tool_info(ToolInfo(name="hello", description="Say hello"))

    def fake_select(*args, **kwargs):
        return FakeQuestion(0)

    monkeypatch.setattr("questionary.select", fake_select)

    state = await command.run(session, ["show"], "")
    assert state == "user"


async def test_edit_cancel_select(
    monkeypatch: pytest.MonkeyPatch,
    command: ToolInfoSlashCommand,
    session: ConsoleSession,
) -> None:
    session.history.add_tool_info(ToolInfo(name="hello", description="Say hello"))

    def fake_select(*args, **kwargs):
        return FakeQuestion(None)

    monkeypatch.setattr("questionary.select", fake_select)

    state = await command.run(session, ["edit"], "")
    assert state == "user"


async def test_edit_cancel_edit(
    monkeypatch: pytest.MonkeyPatch,
    command: ToolInfoSlashCommand,
    session: ConsoleSession,
) -> None:
    session.history.add_tool_info(ToolInfo(name="hello", description="Say hello"))

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
    command: ToolInfoSlashCommand,
    session: ConsoleSession,
) -> None:
    session.history.add_tool_info(ToolInfo(name="hello", description="Say hello"))

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
    command: ToolInfoSlashCommand,
    session: ConsoleSession,
) -> None:
    session.history.add_tool_info(ToolInfo(name="hello", description="Say hello"))

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
    command: ToolInfoSlashCommand,
    session: ConsoleSession,
) -> None:
    session.history.add_tool_info(ToolInfo(name="hello", description="Say hello"))

    def fake_select(*args, **kwargs):
        return FakeQuestion(0)

    async def fake_edit_text(*args, **kwargs):
        return args[0].replace("Say hello", "Edited")

    monkeypatch.setattr("questionary.select", fake_select)

    monkeypatch.setattr(
        "kiari.core.editor._helpers.edit_text_with_validation.edit_text",
        fake_edit_text,
    )

    state = await command.run(session, ["edit"], "")
    assert state == "user"
    assert session.history.tool_infos[0].description == "Edited"


async def test_arrange_cancel(
    monkeypatch: pytest.MonkeyPatch,
    command: ToolInfoSlashCommand,
    session: ConsoleSession,
) -> None:
    session.history.add_tool_info(ToolInfo(name="first", description="First tool"))
    session.history.add_tool_info(ToolInfo(name="second", description="Second tool"))

    async def fake_edit_text(*args, **kwargs):
        return None

    monkeypatch.setattr(
        "kiari.core.editor._helpers.edit_text_with_validation.edit_text",
        fake_edit_text,
    )

    state = await command.run(session, ["arrange"], "")

    assert state == "user"
    assert session.history.tool_infos[0].name == "first"
    assert session.history.tool_infos[1].name == "second"


async def test_arrange_no_change(
    monkeypatch: pytest.MonkeyPatch,
    command: ToolInfoSlashCommand,
    session: ConsoleSession,
) -> None:
    session.history.add_tool_info(ToolInfo(name="first", description="First tool"))
    session.history.add_tool_info(ToolInfo(name="second", description="Second tool"))

    async def fake_edit_text(*args, **kwargs):
        return args[0]

    monkeypatch.setattr(
        "kiari.core.editor._helpers.edit_text_with_validation.edit_text",
        fake_edit_text,
    )

    state = await command.run(session, ["arrange"], "")

    assert state == "user"
    assert session.history.tool_infos[0].name == "first"
    assert session.history.tool_infos[1].name == "second"


async def test_arrange_reorder_and_state_change(
    monkeypatch: pytest.MonkeyPatch,
    command: ToolInfoSlashCommand,
    session: ConsoleSession,
) -> None:
    session.history.add_tool_info(ToolInfo(name="first", description="First tool"))
    session.history.add_tool_info(ToolInfo(name="second", description="Second tool"))

    async def fake_edit_text(*args, **kwargs):
        return "# leading comment\n\ndisabled second\ninactive first"

    monkeypatch.setattr(
        "kiari.core.editor._helpers.edit_text_with_validation.edit_text",
        fake_edit_text,
    )

    state = await command.run(session, ["arrange"], "")

    assert state == "user"
    assert [ti.name for ti in session.history.tool_infos] == ["second", "first"]
    assert session.history.tool_infos[0].state == "disabled"
    assert session.history.tool_infos[1].state == "inactive"


@pytest.mark.parametrize(
    "edited_text",
    [
        "active\nactive second",  # invalid line (no name token)
        "bogus first\nactive second",  # invalid state
        "active unknown\nactive second",  # unknown name
        "active first\nactive first",  # duplicate name (missing 'second' also)
        "active first",  # missing 'second'
    ],
)
async def test_arrange_validation_error(
    monkeypatch: pytest.MonkeyPatch,
    setup_run_context,
    command: ToolInfoSlashCommand,
    session: ConsoleSession,
    edited_text: str,
) -> None:
    session.history.add_tool_info(ToolInfo(name="first", description="First tool"))
    session.history.add_tool_info(ToolInfo(name="second", description="Second tool"))

    def fake_select(*args, **kwargs):
        return FakeQuestion("abort")

    async def fake_edit_text(*args, **kwargs):
        return edited_text

    monkeypatch.setattr("questionary.select", fake_select)

    monkeypatch.setattr(
        "kiari.core.editor._helpers.edit_text_with_validation.edit_text",
        fake_edit_text,
    )

    state = await command.run(session, ["arrange"], "")

    assert state == "user"
    assert [ti.name for ti in session.history.tool_infos] == ["first", "second"]
    assert all(ti.state == "active" for ti in session.history.tool_infos)


async def test_unknown_command(
    command: ToolInfoSlashCommand,
    session: ConsoleSession,
) -> None:
    state = await command.run(session, ["unknown"], "")
    assert state == "user"
