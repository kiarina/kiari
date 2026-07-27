from collections.abc import Sequence
from typing import Protocol, runtime_checkable

from rich.console import RenderableType

from kiari.cli.console.console_handler import ConsoleSession
from kiari.cli.console.console_state import ConsoleState

from .slash_command_name import SlashCommandName


@runtime_checkable
class SlashCommand(Protocol):
    name: SlashCommandName

    def get_description(self, session: ConsoleSession) -> RenderableType: ...

    async def run(
        self,
        session: ConsoleSession,
        args: Sequence[str],
        content: str,
    ) -> ConsoleState: ...
