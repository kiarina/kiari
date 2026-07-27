from pathlib import Path

import pytest
from rich.console import Console

from kiari.cli.console.console_handler import ConsoleSession
from kiari.cli.console.slash_command_impl.file_info import FileInfoSlashCommand


class FakeQuestion:
    def __init__(self, selected):
        self.selected = selected

    async def ask_async(self):
        return self.selected


@pytest.fixture
def command(run_options):
    command = FileInfoSlashCommand("default", run_options)
    command.name = "file_info"
    return command


def test_get_description(
    console: Console,
    session: ConsoleSession,
    command: FileInfoSlashCommand,
) -> None:
    console.print(command.get_description(session))
    output = console.export_text()
    assert len(output.strip()) > 0


async def test_help(
    console: Console,
    session: ConsoleSession,
    command: FileInfoSlashCommand,
) -> None:
    state = await command.run(session, [], "")
    output = console.export_text()

    assert state == "user"
    assert "/file_info list" in output


async def test_empty(
    session: ConsoleSession,
    command: FileInfoSlashCommand,
) -> None:
    state = await command.run(session, ["list"], "")
    assert state == "user"


async def test_list(
    console: Console,
    command: FileInfoSlashCommand,
    session: ConsoleSession,
    text_file_info,
    image_file_info,
) -> None:
    session.history.add_file_info(text_file_info)
    session.history.add_file_info(image_file_info)

    state = await command.run(session, ["list"], "")
    output = console.export_text()

    assert state == "user"
    assert "0: text" in output
    assert "1: image" in output


async def test_add_help(
    command: FileInfoSlashCommand,
    session: ConsoleSession,
) -> None:
    state = await command.run(session, ["add"], "")
    assert state == "user"


async def test_add(
    command: FileInfoSlashCommand,
    session: ConsoleSession,
    text_file_path: str,
    image_file_path: str,
) -> None:
    state = await command.run(
        session,
        ["add", text_file_path],
        image_file_path,
    )

    assert state == "user"
    assert len(session.history.file_infos) == 2


async def test_add_with_pattern(
    command: FileInfoSlashCommand,
    session: ConsoleSession,
    tmp_path: Path,
) -> None:
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.txt").write_text("b")
    (tmp_path / "c.log").write_text("c")

    state = await command.run(
        session,
        ["add", str(tmp_path) + "?include=*.txt"],
        "",
    )

    assert state == "user"
    assert [Path(file_info.uri_or_file_path).name for file_info in session.history.file_infos] == [
        "a.txt",
        "b.txt",
    ]


async def test_remove_cancel(
    monkeypatch: pytest.MonkeyPatch,
    command: FileInfoSlashCommand,
    session: ConsoleSession,
    text_file_info,
    image_file_info,
) -> None:
    session.history.add_file_info(text_file_info)
    session.history.add_file_info(image_file_info)

    def fake_checkbox(*args, **kwargs):
        return FakeQuestion(None)

    monkeypatch.setattr("questionary.checkbox", fake_checkbox)

    state = await command.run(session, ["remove"], "")
    assert state == "user"
    assert len(session.history.file_infos) == 2


async def test_remove(
    monkeypatch: pytest.MonkeyPatch,
    command: FileInfoSlashCommand,
    session: ConsoleSession,
    text_file_info,
    image_file_info,
) -> None:
    session.history.add_file_info(text_file_info)
    session.history.add_file_info(image_file_info)

    def fake_checkbox(*args, **kwargs):
        return FakeQuestion([0])

    monkeypatch.setattr("questionary.checkbox", fake_checkbox)

    state = await command.run(session, ["remove"], "")
    assert state == "user"
    assert len(session.history.file_infos) == 1


async def test_show_cancel(
    monkeypatch: pytest.MonkeyPatch,
    command: FileInfoSlashCommand,
    session: ConsoleSession,
    text_file_info,
) -> None:
    session.history.add_file_info(text_file_info)

    def fake_select(*args, **kwargs):
        return FakeQuestion(None)

    monkeypatch.setattr("questionary.select", fake_select)

    state = await command.run(session, ["show"], "")
    assert state == "user"


async def test_show(
    monkeypatch: pytest.MonkeyPatch,
    command: FileInfoSlashCommand,
    session: ConsoleSession,
    text_file_info,
) -> None:
    session.history.add_file_info(text_file_info)

    def fake_select(*args, **kwargs):
        return FakeQuestion(0)

    monkeypatch.setattr("questionary.select", fake_select)

    state = await command.run(session, ["show"], "")
    assert state == "user"


async def test_edit_cancel_select(
    monkeypatch: pytest.MonkeyPatch,
    command: FileInfoSlashCommand,
    session: ConsoleSession,
    text_file_info,
) -> None:
    session.history.add_file_info(text_file_info)

    def fake_select(*args, **kwargs):
        return FakeQuestion(0)

    monkeypatch.setattr("questionary.select", fake_select)

    state = await command.run(session, ["edit"], "")
    assert state == "user"


async def test_edit_cancel_edit(
    monkeypatch: pytest.MonkeyPatch,
    command: FileInfoSlashCommand,
    session: ConsoleSession,
    text_file_info,
) -> None:
    session.history.add_file_info(text_file_info)

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
    command: FileInfoSlashCommand,
    session: ConsoleSession,
    text_file_info,
) -> None:
    session.history.add_file_info(text_file_info)

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
    command: FileInfoSlashCommand,
    session: ConsoleSession,
    text_file_info,
) -> None:
    session.history.add_file_info(text_file_info)

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
    command: FileInfoSlashCommand,
    session: ConsoleSession,
    text_file_info,
) -> None:
    session.history.add_file_info(text_file_info)

    def fake_select(*args, **kwargs):
        return FakeQuestion(0)

    async def fake_edit_text(*args, **kwargs):
        # Replace the body (raw_text) so multi-line edits are exercised
        original = args[0]
        before_body, _, _ = original.rpartition("---\n")
        return before_body + "---\nline 1\nline 2\n"

    monkeypatch.setattr("questionary.select", fake_select)

    monkeypatch.setattr(
        "kiari.core.editor._helpers.edit_text_with_validation.edit_text",
        fake_edit_text,
    )

    state = await command.run(session, ["edit"], "")
    assert state == "user"

    updated = session.history.file_infos[0]
    assert updated.type == "text"
    assert updated.raw_text == "line 1\nline 2"


async def test_unknown_command(
    command: FileInfoSlashCommand,
    session: ConsoleSession,
) -> None:
    state = await command.run(session, ["unknown"], "")
    assert state == "user"
