from collections.abc import Sequence

from kiarina.i18n import get_i18n
from rich.console import RenderableType
from rich.table import Table
from rich.text import Text

from kiari.cli.console.console_handler import ConsoleSession
from kiari.cli.console.console_state import ConsoleState
from kiari.cli.console.slash_command import BaseSlashCommand, slash_command_registry
from kiari.cli.console.slash_command._settings import settings_manager
from kiari.core.rich import console_registry

from .._i18n import HelpSlashCommandI18n


class HelpSlashCommand(BaseSlashCommand):
    def get_description(self, session: ConsoleSession) -> RenderableType:
        t = get_i18n(HelpSlashCommandI18n, session.run_context.language)
        return Text.from_markup(t.description)

    async def run(
        self,
        session: ConsoleSession,
        args: Sequence[str],
        content: str,
    ) -> ConsoleState:
        t = get_i18n(HelpSlashCommandI18n, session.run_context.language)
        console = console_registry.get()
        aliases_by_name = _create_aliases_by_name()

        table = Table(
            title=t.table_title,
            show_header=True,
            show_edge=True,
            show_lines=True,
            padding=(0, 1),
            border_style="blue",
        )
        table.add_column(t.column_command, style="bold cyan", vertical="top")
        table.add_column(t.column_description, style="white", vertical="top")

        for command_name in _list_command_names(args):
            command = slash_command_registry.resolve(
                command_name, self.profile_name, self.run_options
            )

            command_labels = [f"/{command_name}"]
            for alias in sorted(aliases_by_name.get(command_name, [])):
                command_labels.append(f"/{alias}")

            description = command.get_description(session)

            if isinstance(description, Text) and not description.plain.strip():
                description = Text(t.no_description, style="dim")

            table.add_row("\n".join(command_labels), description)

        console.print(table)

        return "user"


def _create_aliases_by_name() -> dict[str, list[str]]:
    aliases_by_name: dict[str, list[str]] = {}

    for alias, name in settings_manager.settings.aliases.items():
        aliases_by_name.setdefault(name, []).append(alias)

    return aliases_by_name


def _list_command_names(args: Sequence[str]) -> list[str]:
    if not args:
        return slash_command_registry.list_names()

    aliases = slash_command_registry.get_aliases()
    command_names: list[str] = []
    seen: set[str] = set()

    for arg in args:
        command_name = aliases.get(arg, arg)

        if command_name in seen:
            continue

        command_names.append(command_name)
        seen.add(command_name)

    return command_names
