import pytest
from rich.console import Console

from kiari.cli.console.console_handler import ConsoleSession
from kiari.cli.console.slash_command_impl.attach import AttachSlashCommand


class FakeQuestion:
    def __init__(self, selected):
        self.selected = selected

    async def ask_async(self):
        return self.selected


@pytest.fixture
def command(run_options):
    command = AttachSlashCommand("default", run_options)
    command.name = "attach"
    return command


def test_get_description(
    console: Console,
    session: ConsoleSession,
    command: AttachSlashCommand,
) -> None:
    console.print(command.get_description(session))
    output = console.export_text()
    assert len(output.strip()) > 0


async def test_help(
    session: ConsoleSession,
    command: AttachSlashCommand,
) -> None:
    state = await command.run(session, [], "")
    assert state == "user"


async def test_empty(
    session: ConsoleSession,
    command: AttachSlashCommand,
) -> None:
    state = await command.run(session, ["list"], "")
    assert state == "user"


async def test_list(
    console: Console,
    session: ConsoleSession,
    command: AttachSlashCommand,
) -> None:
    session.attachments = ["README.md", "CHANGELOG.md"]

    state = await command.run(session, ["list"], "")

    output = console.export_text()

    assert state == "user"
    assert "0: README.md" in output
    assert "1: CHANGELOG.md" in output


async def test_add_help(
    session: ConsoleSession,
    command: AttachSlashCommand,
) -> None:
    state = await command.run(session, ["add"], "")
    assert state == "user"


async def test_add_no_files(
    session: ConsoleSession,
    command: AttachSlashCommand,
) -> None:
    state = await command.run(session, ["add", "non_existent_file.txt"], "")
    assert state == "user"


async def test_add(
    text_file_path: str,
    image_file_path: str,
    session: ConsoleSession,
    command: AttachSlashCommand,
) -> None:
    session.attachments = [text_file_path]

    state = await command.run(
        session,
        ["add", text_file_path],
        image_file_path,
    )

    assert state == "user"
    assert session.attachments == [text_file_path, image_file_path]
    assert session.text == ""


async def test_remove_cancel(
    monkeypatch: pytest.MonkeyPatch,
    session: ConsoleSession,
    command: AttachSlashCommand,
) -> None:
    def fake_checkbox(*args, **kwargs):
        return FakeQuestion(None)

    monkeypatch.setattr("questionary.checkbox", fake_checkbox)

    session.attachments = ["README.md"]

    state = await command.run(session, ["remove"], "")

    assert state == "user"
    assert session.attachments == ["README.md"]


async def test_remove(
    monkeypatch: pytest.MonkeyPatch,
    session: ConsoleSession,
    command: AttachSlashCommand,
) -> None:
    def fake_checkbox(*args, **kwargs):
        return FakeQuestion([0])

    monkeypatch.setattr("questionary.checkbox", fake_checkbox)

    session.attachments = ["README.md", "CHANGELOG.md"]

    state = await command.run(session, ["remove"], "")

    assert state == "user"
    assert session.attachments == ["CHANGELOG.md"]


async def test_attach_no_files(
    session: ConsoleSession,
    command: AttachSlashCommand,
) -> None:
    state = await command.run(session, ["non_existent_file.txt"], "")
    assert state == "user"


async def test_attach_user(
    text_file_path: str,
    session: ConsoleSession,
    command: AttachSlashCommand,
) -> None:
    state = await command.run(session, [text_file_path], "")

    assert state == "user"
    assert session.attachments == [text_file_path]
    assert session.text == ""


async def test_attach_agent(
    text_file_path: str,
    session: ConsoleSession,
    command: AttachSlashCommand,
) -> None:
    state = await command.run(session, [text_file_path], "hello")

    assert state == "agent"
    assert session.attachments == [text_file_path]
    assert session.text == "hello"
