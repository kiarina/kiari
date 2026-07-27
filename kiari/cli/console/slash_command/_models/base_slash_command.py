from collections.abc import Sequence

from rich.console import RenderableType
from rich.text import Text

from kiari.cli.console.console_handler import ConsoleSession
from kiari.cli.console.console_state import ConsoleState
from kiari.core.profile import ProfileName, RunOptions
from kiari.lib.history_repository import HistoryRepository, history_repository_registry

from .._types.slash_command import SlashCommand
from .._types.slash_command_name import SlashCommandName


class BaseSlashCommand(SlashCommand):
    def __init__(self, profile_name: ProfileName, run_options: RunOptions) -> None:
        self.profile_name: ProfileName = profile_name
        self.run_options: RunOptions = run_options
        self._name: SlashCommandName | None = None

    @property
    def name(self) -> SlashCommandName:
        if not self._name:  # pragma: no cover
            raise AssertionError("SlashCommand name not set")

        return self._name

    @name.setter
    def name(self, value: SlashCommandName) -> None:
        self._name = value

    @property
    def history_repository(self) -> HistoryRepository:
        return history_repository_registry.resolve(self.run_options.history_repository)

    @property
    def no_save(self) -> bool:
        return self.run_options.no_save

    def get_description(self, session: ConsoleSession) -> RenderableType:
        return Text()

    async def run(
        self,
        session: ConsoleSession,
        args: Sequence[str],
        content: str,
    ) -> ConsoleState:
        return "user"
