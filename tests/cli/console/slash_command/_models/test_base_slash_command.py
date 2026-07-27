from rich.console import Console, ConsoleRenderable
from rich.text import Text

from kiari.cli.console.console_handler import ConsoleSession
from kiari.cli.console.slash_command import BaseSlashCommand
from kiari.core.profile import RunOptions


class ExampleSlashCommand(BaseSlashCommand):
    def get_description(self, session: ConsoleSession) -> ConsoleRenderable:
        return Text("example description")


async def test_base_slash_command(
    console: Console, run_options: RunOptions, session: ConsoleSession
) -> None:
    command = ExampleSlashCommand("default", run_options)
    command.name = "example"

    print(f"name: {command.name}")
    print(f"history_repository: {command.history_repository}")
    print(f"no_save: {command.no_save}")

    console.print(command.get_description(session))

    assert await command.run(session, [], "") == "user"
