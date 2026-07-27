from collections.abc import Sequence
from typing import cast

import questionary
from kiarina.agi.tool_info import ToolChoice
from kiarina.i18n import get_i18n
from rich.console import RenderableType
from rich.text import Text

from kiari.cli.console.console_handler import ConsoleSession
from kiari.cli.console.console_state import ConsoleState
from kiari.cli.console.slash_command import BaseSlashCommand
from kiari.core.rich import console_registry
from kiari.core.terminal import create_prompt_toolkit_io

from .._i18n import ToolChoiceSlashCommandI18n


class ToolChoiceSlashCommand(BaseSlashCommand):
    def get_description(self, session: ConsoleSession) -> RenderableType:
        t = get_i18n(ToolChoiceSlashCommandI18n, session.run_context.language)
        return Text.from_markup(t.description)

    async def run(
        self,
        session: ConsoleSession,
        args: Sequence[str],
        content: str,
    ) -> ConsoleState:
        t = get_i18n(ToolChoiceSlashCommandI18n, session.run_context.language)
        console = console_registry.get()

        if not args:
            selected = await questionary.select(
                t.select_tool_choice,
                choices=_list_tool_choices(session),
                default=_get_current_tool_choice(session),
                use_jk_keys=False,
                **create_prompt_toolkit_io(),
            ).ask_async()

            if selected is None:
                return "user"

            tool_choice = cast(ToolChoice, selected)
        else:
            tool_choice = args[0]

        session.chat_options["tool_choice"] = tool_choice

        console.print(
            t.tool_choice_updated.format(tool_choice=tool_choice),
            style="blue",
        )

        return "user"


def _list_tool_choices(session: ConsoleSession) -> list[str]:
    tool_choices = ["auto", "any"]

    for tool_info in session.history.tool_infos:
        if tool_info.name not in tool_choices:
            tool_choices.append(tool_info.name)

    return tool_choices


def _get_current_tool_choice(session: ConsoleSession) -> str:
    tool_choices = _list_tool_choices(session)
    tool_choice = session.chat_options.get("tool_choice") or "auto"

    if tool_choice in tool_choices:
        return tool_choice

    return "auto"
