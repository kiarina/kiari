import pytest
from kiarina.agi.chat_model import chat_model_registry
from rich.console import Console

from kiari.cli.console.console_handler import ConsoleSession
from kiari.cli.console.slash_command_impl.chat_model import ChatModelSlashCommand


class FakeQuestion:
    def __init__(self, selected):
        self.selected = selected

    async def ask_async(self):
        return self.selected


@pytest.fixture
def command(run_options):
    command = ChatModelSlashCommand("default", run_options)
    command.name = "chat_model"
    return command


def test_get_description(
    console: Console,
    session: ConsoleSession,
    command: ChatModelSlashCommand,
) -> None:
    console.print(command.get_description(session))
    output = console.export_text()
    assert len(output.strip()) > 0


async def test_select(
    command: ChatModelSlashCommand,
    session: ConsoleSession,
    monkeypatch,
) -> None:
    model_name = next(
        name
        for name in chat_model_registry.list_names()
        if chat_model_registry.get_config(name).visible
    )

    def fake_select(*args, **kwargs):
        assert kwargs["default"] == model_name
        return FakeQuestion(model_name)

    monkeypatch.setattr("questionary.select", fake_select)
    session.chat_options["chat_model"] = f"{model_name}?max_output_tokens=128"

    state = await command.run(session, [], "")

    assert state == "user"
    assert session.chat_options.get("chat_model") == model_name


async def test_direct(
    command: ChatModelSlashCommand,
    session: ConsoleSession,
) -> None:
    state = await command.run(session, ["mock?max_output_tokens=128"], "")

    assert state == "user"
    assert session.chat_options.get("chat_model") == "mock?max_output_tokens=128"
