import pytest
from rich.console import Console

from kiari.cli.console.console_handler import ConsoleSession
from kiari.cli.console.slash_command_impl.metadata import MetadataSlashCommand


class FakeQuestion:
    def __init__(self, selected):
        self.selected = selected

    async def ask_async(self):
        return self.selected


@pytest.fixture
def command(run_options):
    command = MetadataSlashCommand("default", run_options)
    command.name = "metadata"
    return command


def test_get_description(
    console: Console,
    session: ConsoleSession,
    command: MetadataSlashCommand,
) -> None:
    console.print(command.get_description(session))
    output = console.export_text()
    assert len(output.strip()) > 0


async def test_help(
    console: Console,
    session: ConsoleSession,
    command: MetadataSlashCommand,
) -> None:
    state = await command.run(session, [], "")
    output = console.export_text()

    assert state == "user"
    assert "/metadata list" in output


async def test_empty(
    session: ConsoleSession,
    command: MetadataSlashCommand,
) -> None:
    state = await command.run(session, ["list"], "")
    assert state == "user"


async def test_list(
    console: Console,
    command: MetadataSlashCommand,
    session: ConsoleSession,
) -> None:
    session.history.metadata["beta"] = "second"
    session.history.metadata["alpha"] = 1

    state = await command.run(session, ["list"], "")
    output = console.export_text()

    assert state == "user"
    # alphabetical order: alpha precedes beta in the output
    assert output.index("alpha:") < output.index("beta:")
    assert "alpha: 1" in output
    assert 'beta: "second"' in output


async def test_list_long_preview_truncated(
    console: Console,
    command: MetadataSlashCommand,
    session: ConsoleSession,
) -> None:
    long_value = "x" * 200
    session.history.metadata["long"] = long_value

    state = await command.run(session, ["list"], "")
    output = console.export_text()

    assert state == "user"
    assert "..." in output
    # full value is 202 chars (with quotes) so it must be truncated to <=120
    assert long_value not in output


async def test_set_examples(
    console: Console,
    command: MetadataSlashCommand,
    session: ConsoleSession,
) -> None:
    state = await command.run(session, ["set"], "")
    output = console.export_text()

    assert state == "user"
    assert "Examples" in output


async def test_set_value_required(
    console: Console,
    command: MetadataSlashCommand,
    session: ConsoleSession,
) -> None:
    state = await command.run(session, ["set", "hello"], "   ")
    output = console.export_text()

    assert state == "user"
    assert "hello" not in session.history.metadata
    assert "Value" in output


async def test_set_invalid_json(
    console: Console,
    command: MetadataSlashCommand,
    session: ConsoleSession,
) -> None:
    state = await command.run(session, ["set", "hello"], "fire")
    output = console.export_text()

    assert state == "user"
    assert "hello" not in session.history.metadata
    assert "Invalid JSON" in output


async def test_set_new(
    console: Console,
    command: MetadataSlashCommand,
    session: ConsoleSession,
) -> None:
    state = await command.run(session, ["set", "hello"], '"fire"')
    output = console.export_text()

    assert state == "user"
    assert session.history.metadata == {"hello": "fire"}
    assert "Set metadata" in output


async def test_set_various_json_types(
    command: MetadataSlashCommand,
    session: ConsoleSession,
) -> None:
    cases: list[tuple[str, str, object]] = [
        ("flag", "true", True),
        ("count", "42", 42),
        ("ratio", "1.5", 1.5),
        ("nothing", "null", None),
        ("tags", '["a", "b", "c"]', ["a", "b", "c"]),
        (
            "config",
            '{"host": "localhost", "port": 8080}',
            {"host": "localhost", "port": 8080},
        ),
    ]

    for key, content, expected in cases:
        state = await command.run(session, ["set", key], content)
        assert state == "user"
        assert session.history.metadata[key] == expected


async def test_set_overwrite(
    console: Console,
    command: MetadataSlashCommand,
    session: ConsoleSession,
) -> None:
    session.history.metadata["hello"] = "old"

    state = await command.run(session, ["set", "hello"], '"new"')
    output = console.export_text()

    assert state == "user"
    assert session.history.metadata == {"hello": "new"}
    assert "Overwrote" in output


async def test_delete_cancel(
    monkeypatch: pytest.MonkeyPatch,
    command: MetadataSlashCommand,
    session: ConsoleSession,
) -> None:
    session.history.metadata["alpha"] = 1
    session.history.metadata["beta"] = 2

    def fake_checkbox(*args, **kwargs):
        return FakeQuestion(None)

    monkeypatch.setattr("questionary.checkbox", fake_checkbox)

    state = await command.run(session, ["delete"], "")
    assert state == "user"
    assert session.history.metadata == {"alpha": 1, "beta": 2}


async def test_delete(
    monkeypatch: pytest.MonkeyPatch,
    command: MetadataSlashCommand,
    session: ConsoleSession,
) -> None:
    session.history.metadata["alpha"] = 1
    session.history.metadata["beta"] = 2
    session.history.metadata["gamma"] = 3

    def fake_checkbox(*args, **kwargs):
        return FakeQuestion(["alpha", "gamma"])

    monkeypatch.setattr("questionary.checkbox", fake_checkbox)

    state = await command.run(session, ["delete"], "")
    assert state == "user"
    assert session.history.metadata == {"beta": 2}


async def test_show_cancel(
    monkeypatch: pytest.MonkeyPatch,
    command: MetadataSlashCommand,
    session: ConsoleSession,
) -> None:
    session.history.metadata["hello"] = "fire"

    def fake_select(*args, **kwargs):
        return FakeQuestion(None)

    monkeypatch.setattr("questionary.select", fake_select)

    state = await command.run(session, ["show"], "")
    assert state == "user"


async def test_show(
    monkeypatch: pytest.MonkeyPatch,
    command: MetadataSlashCommand,
    session: ConsoleSession,
) -> None:
    session.history.metadata["hello"] = {"nested": [1, 2, 3]}

    def fake_select(*args, **kwargs):
        return FakeQuestion("hello")

    monkeypatch.setattr("questionary.select", fake_select)

    state = await command.run(session, ["show"], "")
    assert state == "user"


async def test_edit_cancel_select(
    monkeypatch: pytest.MonkeyPatch,
    command: MetadataSlashCommand,
    session: ConsoleSession,
) -> None:
    session.history.metadata["hello"] = "fire"

    def fake_select(*args, **kwargs):
        return FakeQuestion(None)

    monkeypatch.setattr("questionary.select", fake_select)

    state = await command.run(session, ["edit"], "")
    assert state == "user"


async def test_edit_cancel_edit(
    monkeypatch: pytest.MonkeyPatch,
    command: MetadataSlashCommand,
    session: ConsoleSession,
) -> None:
    session.history.metadata["hello"] = "fire"

    def fake_select(*args, **kwargs):
        return FakeQuestion("hello")

    async def fake_edit_text(*args, **kwargs):
        return None

    monkeypatch.setattr("questionary.select", fake_select)

    monkeypatch.setattr(
        "kiari.core.editor._helpers.edit_text_with_validation.edit_text",
        fake_edit_text,
    )

    state = await command.run(session, ["edit"], "")
    assert state == "user"
    assert session.history.metadata == {"hello": "fire"}


async def test_edit_no_change(
    monkeypatch: pytest.MonkeyPatch,
    command: MetadataSlashCommand,
    session: ConsoleSession,
) -> None:
    session.history.metadata["hello"] = "fire"

    def fake_select(*args, **kwargs):
        return FakeQuestion("hello")

    async def fake_edit_text(*args, **kwargs):
        return args[0]

    monkeypatch.setattr("questionary.select", fake_select)

    monkeypatch.setattr(
        "kiari.core.editor._helpers.edit_text_with_validation.edit_text",
        fake_edit_text,
    )

    state = await command.run(session, ["edit"], "")
    assert state == "user"
    assert session.history.metadata == {"hello": "fire"}


async def test_edit_validation_error(
    monkeypatch: pytest.MonkeyPatch,
    setup_run_context,
    command: MetadataSlashCommand,
    session: ConsoleSession,
) -> None:
    session.history.metadata["hello"] = "fire"

    count = 0

    def fake_select(*args, **kwargs):
        nonlocal count
        count += 1

        match count:
            case 1:
                return FakeQuestion("hello")
            case 2:
                return FakeQuestion("abort")
            case _:
                raise AssertionError("Too many iterations in test_edit_validation_error")

    async def fake_edit_text(*args, **kwargs):
        return "not valid json"

    monkeypatch.setattr("questionary.select", fake_select)

    monkeypatch.setattr(
        "kiari.core.editor._helpers.edit_text_with_validation.edit_text",
        fake_edit_text,
    )

    state = await command.run(session, ["edit"], "")
    assert state == "user"


async def test_edit(
    monkeypatch: pytest.MonkeyPatch,
    command: MetadataSlashCommand,
    session: ConsoleSession,
) -> None:
    session.history.metadata["hello"] = "fire"

    def fake_select(*args, **kwargs):
        return FakeQuestion("hello")

    async def fake_edit_text(*args, **kwargs):
        return args[0].replace("fire", "water")

    monkeypatch.setattr("questionary.select", fake_select)

    monkeypatch.setattr(
        "kiari.core.editor._helpers.edit_text_with_validation.edit_text",
        fake_edit_text,
    )

    state = await command.run(session, ["edit"], "")
    assert state == "user"
    assert session.history.metadata == {"hello": "water"}


async def test_unknown_command(
    command: MetadataSlashCommand,
    session: ConsoleSession,
) -> None:
    state = await command.run(session, ["unknown"], "")
    assert state == "user"
