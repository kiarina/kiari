from collections.abc import Sequence

import questionary
from kiarina.i18n import get_i18n
from rich.console import RenderableType
from rich.text import Text

from kiari.cli.console.console_handler import ConsoleSession
from kiari.cli.console.console_state import ConsoleState
from kiari.cli.console.slash_command import BaseSlashCommand
from kiari.core.file_info_source import FileInfoSource, resolve_file_info_specifiers
from kiari.core.rich import console_registry
from kiari.core.terminal import create_prompt_toolkit_io

from .._i18n import AttachSlashCommandI18n

_COMMANDS_REQUIRING_ATTACHMENTS: frozenset[str] = frozenset({"list", "remove"})


class AttachSlashCommand(BaseSlashCommand):
    def get_description(self, session: ConsoleSession) -> RenderableType:
        t = get_i18n(AttachSlashCommandI18n, session.run_context.language)
        return Text.from_markup(t.description)

    async def run(
        self,
        session: ConsoleSession,
        args: Sequence[str],
        content: str,
    ) -> ConsoleState:
        t = get_i18n(AttachSlashCommandI18n, session.run_context.language)
        console = console_registry.get()

        if not args:
            return self._handle_help(session)

        command, *rest = args

        if command in _COMMANDS_REQUIRING_ATTACHMENTS and not session.attachments:
            console.print(t.no_attached_files, style="yellow")
            return "user"

        if command == "list":
            return self._handle_list(session)

        if command == "add":
            if content:
                rest.append(content)

            return await self._handle_add(session, rest)

        if command == "remove":
            return await self._handle_remove(session)

        # Verb shortcut: /attach <source>...
        return await self._handle_attach(session, list(args), content)

    def _handle_help(self, session: ConsoleSession) -> ConsoleState:
        t = get_i18n(AttachSlashCommandI18n, session.run_context.language)
        console = console_registry.get()
        console.print(Text.from_markup(t.description))
        return "user"

    def _handle_list(self, session: ConsoleSession) -> ConsoleState:
        console = console_registry.get()

        for index, attachment in enumerate(session.attachments):
            console.print(_format_attachment(attachment, index), style="blue")

        return "user"

    async def _handle_add(
        self,
        session: ConsoleSession,
        args: Sequence[str],
    ) -> ConsoleState:
        t = get_i18n(AttachSlashCommandI18n, session.run_context.language)
        console = console_registry.get()

        if not args:
            console.print(Text.from_markup(t.add_examples))
            return "user"

        resolved = await resolve_file_info_specifiers(list(args))

        if not resolved:
            console.print(t.no_files_found, style="yellow")
            return "user"

        new_entries = _dedupe(session.attachments, resolved)
        session.attachments = session.attachments + new_entries

        console.print(
            t.added_n_attached_files.format(n=len(new_entries)),
            style="blue",
        )

        return "user"

    async def _handle_remove(self, session: ConsoleSession) -> ConsoleState:
        t = get_i18n(AttachSlashCommandI18n, session.run_context.language)
        console = console_registry.get()

        choices = [
            questionary.Choice(title=_format_attachment(attachment, index), value=index)
            for index, attachment in enumerate(session.attachments)
        ]

        selected = await questionary.checkbox(
            t.select_files_to_delete,
            choices=choices,
            use_search_filter=True,
            use_jk_keys=False,
            **create_prompt_toolkit_io(),
        ).ask_async()

        if not selected:
            return "user"

        selected_indexes = set(selected)

        session.attachments = [
            attachment
            for index, attachment in enumerate(session.attachments)
            if index not in selected_indexes
        ]

        console.print(
            t.deleted_n_attached_files.format(n=len(selected_indexes)),
            style="blue",
        )

        return "user"

    async def _handle_attach(
        self,
        session: ConsoleSession,
        args: list[FileInfoSource],
        content: str,
    ) -> ConsoleState:
        t = get_i18n(AttachSlashCommandI18n, session.run_context.language)
        console = console_registry.get()

        resolved = await resolve_file_info_specifiers(args)

        if not resolved:
            console.print(t.no_files_found, style="yellow")
            return "user"

        new_entries = _dedupe(session.attachments, resolved)
        session.attachments = session.attachments + new_entries

        console.print(
            t.added_n_attached_files.format(n=len(new_entries)),
            style="blue",
        )

        if content:
            session.text = content
            return "agent"

        return "user"


def _dedupe(
    existing: list[FileInfoSource],
    resolved: list[FileInfoSource],
) -> list[FileInfoSource]:
    seen = set(existing)
    new_entries: list[FileInfoSource] = []

    for entry in resolved:
        if entry in seen:
            continue

        seen.add(entry)
        new_entries.append(entry)

    return new_entries


def _format_attachment(attachment: FileInfoSource, index: int) -> str:
    return f"  {index}: {attachment}"
