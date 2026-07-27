from collections.abc import Sequence

import questionary
from kiarina.agi.chat_model import ChatModel, chat_model_registry
from kiarina.i18n import get_i18n
from rich.console import RenderableType
from rich.text import Text

from kiari.cli.console.console_handler import ConsoleSession
from kiari.cli.console.console_state import ConsoleState
from kiari.cli.console.slash_command import BaseSlashCommand
from kiari.core.rich import console_registry
from kiari.core.terminal import create_prompt_toolkit_io

from .._i18n import ChatModelSlashCommandI18n


class ChatModelSlashCommand(BaseSlashCommand):
    def get_description(self, session: ConsoleSession) -> RenderableType:
        t = get_i18n(ChatModelSlashCommandI18n, session.run_context.language)
        return Text.from_markup(t.description)

    async def run(
        self,
        session: ConsoleSession,
        args: Sequence[str],
        content: str,
    ) -> ConsoleState:
        if not args:
            return await _handle_select(session)

        return await _handle_direct(session, args[0])


async def _handle_select(session: ConsoleSession) -> ConsoleState:
    t = get_i18n(ChatModelSlashCommandI18n, session.run_context.language)
    console = console_registry.get()

    model_names = _get_visible_model_names()

    if not model_names:
        console.print(t.no_available_models, style="yellow")
        return "user"

    current = _get_current_model_name(session)

    selected = await questionary.select(
        t.select_prompt,
        choices=model_names,
        default=current if current in model_names else None,
        use_search_filter=True,
        use_jk_keys=False,
        **create_prompt_toolkit_io(),
    ).ask_async()

    if selected is None:
        console.print(t.selection_cancelled, style="yellow")
        return "user"

    _apply_model(session, selected)
    console.print(t.model_updated.format(model_name=selected), style="blue")

    return "user"


async def _handle_direct(session: ConsoleSession, specifier: str) -> ConsoleState:
    t = get_i18n(ChatModelSlashCommandI18n, session.run_context.language)
    console = console_registry.get()

    name_or_alias, _, _ = specifier.partition("?")
    aliases = chat_model_registry.get_aliases()
    resolved_name = aliases.get(name_or_alias, name_or_alias)

    if resolved_name not in chat_model_registry.list_names():
        console.print(t.model_not_found.format(model_name=name_or_alias), style="yellow")
        return "user"

    _apply_model(session, specifier)
    console.print(t.model_updated.format(model_name=specifier), style="blue")

    return "user"


def _get_visible_model_names() -> list[str]:
    return sorted(
        name
        for name in chat_model_registry.list_names()
        if chat_model_registry.get_config(name).visible
    )


def _get_current_model_name(session: ConsoleSession) -> str | None:
    chat_model = session.chat_options.get("chat_model")

    if chat_model is None:
        return chat_model_registry.get_default()

    if isinstance(chat_model, ChatModel):
        return chat_model.name

    model_name, _, _ = chat_model.partition("?")
    return model_name


def _apply_model(session: ConsoleSession, model_name: str) -> None:
    session.chat_options["chat_model"] = model_name
