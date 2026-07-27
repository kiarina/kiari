from collections.abc import Sequence
from typing import Any

import questionary
import yaml
from kiarina.agi.file_info import FileInfo
from kiarina.agi.file_info_loader import load_file_infos
from kiarina.i18n import get_i18n
from kiarina.utils.file import MarkdownContent
from pydantic import TypeAdapter, ValidationError
from rich.console import RenderableType
from rich.syntax import Syntax
from rich.text import Text

from kiari.cli.console.console_handler import ConsoleSession
from kiari.cli.console.console_state import ConsoleState
from kiari.cli.console.slash_command import BaseSlashCommand
from kiari.core.editor import ValidationResult, edit_text_with_validation
from kiari.core.file_info_source import resolve_file_info_specifiers
from kiari.core.rich import console_registry
from kiari.core.terminal import create_prompt_toolkit_io

from .._i18n import FileInfoSlashCommandI18n

_file_info_adapter: TypeAdapter[FileInfo] = TypeAdapter(FileInfo)

_COMMANDS_REQUIRING_FILE_INFOS: frozenset[str] = frozenset({"list", "remove", "show", "edit"})


class FileInfoSlashCommand(BaseSlashCommand):
    def get_description(self, session: ConsoleSession) -> RenderableType:
        t = get_i18n(FileInfoSlashCommandI18n, session.run_context.language)
        return Text.from_markup(t.description)

    async def run(
        self,
        session: ConsoleSession,
        args: Sequence[str],
        content: str,
    ) -> ConsoleState:
        t = get_i18n(FileInfoSlashCommandI18n, session.run_context.language)
        console = console_registry.get()

        if not args:
            return self._handle_help(session)

        command, *rest = args

        if command in _COMMANDS_REQUIRING_FILE_INFOS and not session.history.file_infos:
            console.print(t.no_file_infos, style="yellow")
            return "user"

        if command == "list":
            return self._handle_list(session)

        if command == "add":
            if content:
                rest.append(content)

            return await self._handle_add(session, rest)

        if command == "remove":
            return await self._handle_remove(session)

        if command == "show":
            return await self._handle_show(session)

        if command == "edit":
            return await self._handle_edit(session)

        console.print(
            t.unknown_subcommand.format(command=command),
            style="yellow",
        )
        return "user"

    def _handle_help(self, session: ConsoleSession) -> ConsoleState:
        t = get_i18n(FileInfoSlashCommandI18n, session.run_context.language)
        console = console_registry.get()
        console.print(Text.from_markup(t.description))
        return "user"

    def _handle_list(self, session: ConsoleSession) -> ConsoleState:
        console = console_registry.get()

        for index, file_info in enumerate(session.history.file_infos):
            console.print(_format_file_info(file_info, index), style="blue")

        return "user"

    async def _handle_add(
        self,
        session: ConsoleSession,
        args: Sequence[str],
    ) -> ConsoleState:
        t = get_i18n(FileInfoSlashCommandI18n, session.run_context.language)
        console = console_registry.get()

        if not args:
            console.print(Text.from_markup(t.add_examples))
            return "user"

        file_info_specifiers = await resolve_file_info_specifiers(list(args))

        file_infos = await load_file_infos(
            file_info_specifiers,
            run_context=session.run_context,
        )

        if not file_infos:
            console.print(t.no_files_found, style="yellow")
            return "user"

        for file_info in file_infos:
            session.history.add_file_info(file_info)

        if not self.no_save:
            await self.history_repository.save(
                session.history,
                run_context=session.run_context,
            )

        console.print(t.added_n_file_infos.format(n=len(file_infos)), style="blue")

        return "user"

    async def _handle_remove(self, session: ConsoleSession) -> ConsoleState:
        t = get_i18n(FileInfoSlashCommandI18n, session.run_context.language)
        console = console_registry.get()

        choices = [
            questionary.Choice(title=_format_file_info(file_info, index), value=index)
            for index, file_info in enumerate(session.history.file_infos)
        ]

        selected = await questionary.checkbox(
            t.select_file_infos_to_delete,
            choices=choices,
            use_search_filter=True,
            use_jk_keys=False,
            **create_prompt_toolkit_io(),
        ).ask_async()

        if not selected:
            return "user"

        selected_indexes = set(selected)

        session.history.file_infos = [
            file_info
            for index, file_info in enumerate(session.history.file_infos)
            if index not in selected_indexes
        ]

        if not self.no_save:
            await self.history_repository.save(
                session.history,
                run_context=session.run_context,
            )

        console.print(t.deleted_n_file_infos.format(n=len(selected_indexes)), style="blue")

        return "user"

    async def _handle_show(self, session: ConsoleSession) -> ConsoleState:
        t = get_i18n(FileInfoSlashCommandI18n, session.run_context.language)
        console = console_registry.get()

        index = await self._select_file_info_index(session, prompt=t.select_file_info_to_show)

        if index is None:
            return "user"

        file_info = session.history.file_infos[index]
        console.print(Syntax(_serialize_for_edit(file_info), "markdown"))

        return "user"

    async def _handle_edit(self, session: ConsoleSession) -> ConsoleState:
        t = get_i18n(FileInfoSlashCommandI18n, session.run_context.language)
        console = console_registry.get()

        index = await self._select_file_info_index(session, prompt=t.select_file_info_to_edit)

        if index is None:
            return "user"

        file_info = session.history.file_infos[index]
        original_text = _serialize_for_edit(file_info)

        def validator(candidate: str) -> ValidationResult:
            try:
                _file_info_adapter.validate_python(_parse_edited(candidate))
            except ValidationError as e:
                return ValidationResult(
                    valid=False,
                    message=Text(
                        t.validation_error.format(error=str(e)),
                        style="red",
                    ),
                )

            return ValidationResult(valid=True)

        edited = await edit_text_with_validation(
            original_text,
            validator=validator,
            extension=".md",
            editing_mode=self.run_options.editing_mode,
        )

        if edited is None:
            console.print(t.edit_cancelled, style="yellow")
            return "user"

        if edited == original_text:
            console.print(t.edit_no_change, style="yellow")
            return "user"

        new_file_info = _file_info_adapter.validate_python(_parse_edited(edited))
        session.history.file_infos[index] = new_file_info

        if not self.no_save:
            await self.history_repository.save(
                session.history,
                run_context=session.run_context,
            )

        console.print(t.file_info_updated.format(index=index), style="blue")
        return "user"

    async def _select_file_info_index(
        self,
        session: ConsoleSession,
        *,
        prompt: str,
    ) -> int | None:
        choices = [
            questionary.Choice(title=_format_file_info(file_info, i), value=i)
            for i, file_info in enumerate(session.history.file_infos)
        ]

        selected = await questionary.select(
            prompt,
            choices=choices,
            use_search_filter=True,
            use_jk_keys=False,
            **create_prompt_toolkit_io(),
        ).ask_async()

        if selected is None:
            return None

        return int(selected)


def _format_file_info(file_info: FileInfo, index: int) -> str:
    uri_or_file_path = file_info.uri_or_file_path.replace("\n", " ")
    return f"{index}: {file_info.type} {_shorten(uri_or_file_path, 120)}"


def _shorten(text: str, max_length: int) -> str:
    if len(text) <= max_length:
        return text

    return text[: max_length - 3] + "..."


def _serialize_for_edit(file_info: FileInfo) -> str:
    data: dict[str, Any] = file_info.model_dump(mode="json")

    if file_info.type == "text":
        raw_text = data.pop("raw_text", None)
        body = "" if raw_text is None else raw_text
    else:
        body = ""

    yaml_text = yaml.safe_dump(data, allow_unicode=True, sort_keys=False)
    return f"---\n{yaml_text}---\n{body}"


def _parse_edited(text: str) -> dict[str, Any]:
    markdown_content = MarkdownContent.from_text(text)
    parsed = dict(markdown_content.metadata)

    if parsed.get("type") == "text":
        if raw_text := markdown_content.content.strip():
            parsed["raw_text"] = raw_text

    return parsed
