import json
from collections.abc import Sequence
from typing import Any

import questionary
from kiarina.i18n import get_i18n
from rich.console import RenderableType
from rich.syntax import Syntax
from rich.text import Text

from kiari.cli.console.console_handler import ConsoleSession
from kiari.cli.console.console_state import ConsoleState
from kiari.cli.console.slash_command import BaseSlashCommand
from kiari.core.editor import ValidationResult, edit_text_with_validation
from kiari.core.rich import console_registry
from kiari.core.terminal import create_prompt_toolkit_io

from .._i18n import MetadataSlashCommandI18n

_COMMANDS_REQUIRING_METADATA: frozenset[str] = frozenset({"list", "delete", "show", "edit"})


class MetadataSlashCommand(BaseSlashCommand):
    def get_description(self, session: ConsoleSession) -> RenderableType:
        t = get_i18n(MetadataSlashCommandI18n, session.run_context.language)
        return Text.from_markup(t.description)

    async def run(
        self,
        session: ConsoleSession,
        args: Sequence[str],
        content: str,
    ) -> ConsoleState:
        t = get_i18n(MetadataSlashCommandI18n, session.run_context.language)
        console = console_registry.get()

        if not args:
            return self._handle_help(session)

        command, *rest = args

        if command in _COMMANDS_REQUIRING_METADATA and not session.history.metadata:
            console.print(t.no_metadata, style="yellow")
            return "user"

        if command == "list":
            return self._handle_list(session)

        if command == "set":
            return await self._handle_set(session, rest, content)

        if command == "delete":
            return await self._handle_delete(session)

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
        t = get_i18n(MetadataSlashCommandI18n, session.run_context.language)
        console = console_registry.get()
        console.print(Text.from_markup(t.description))
        return "user"

    def _handle_list(self, session: ConsoleSession) -> ConsoleState:
        console = console_registry.get()

        for key in sorted(session.history.metadata):
            value = session.history.metadata[key]
            console.print(_format_metadata(key, value), style="blue")

        return "user"

    async def _handle_set(
        self,
        session: ConsoleSession,
        rest: Sequence[str],
        content: str,
    ) -> ConsoleState:
        t = get_i18n(MetadataSlashCommandI18n, session.run_context.language)
        console = console_registry.get()

        if not rest:
            console.print(Text.from_markup(t.set_examples))
            return "user"

        key = rest[0]

        if not content.strip():
            console.print(t.value_required, style="yellow")
            return "user"

        try:
            value = json.loads(content)
        except json.JSONDecodeError as e:
            console.print(t.invalid_json.format(error=str(e)), style="red")
            return "user"

        is_overwrite = key in session.history.metadata
        session.history.metadata[key] = value

        if not self.no_save:
            await self.history_repository.save(
                session.history,
                run_context=session.run_context,
            )

        if is_overwrite:
            console.print(t.metadata_overwritten.format(key=key), style="blue")
        else:
            console.print(t.metadata_set.format(key=key), style="blue")

        return "user"

    async def _handle_delete(self, session: ConsoleSession) -> ConsoleState:
        t = get_i18n(MetadataSlashCommandI18n, session.run_context.language)
        console = console_registry.get()

        choices = [
            questionary.Choice(
                title=_format_metadata(key, session.history.metadata[key]),
                value=key,
            )
            for key in sorted(session.history.metadata)
        ]

        selected = await questionary.checkbox(
            t.select_keys_to_delete,
            choices=choices,
            use_search_filter=True,
            use_jk_keys=False,
            **create_prompt_toolkit_io(),
        ).ask_async()

        if not selected:
            return "user"

        for key in selected:
            session.history.metadata.pop(key, None)

        if not self.no_save:
            await self.history_repository.save(
                session.history,
                run_context=session.run_context,
            )

        console.print(t.deleted_n_metadata.format(n=len(selected)), style="blue")

        return "user"

    async def _handle_show(self, session: ConsoleSession) -> ConsoleState:
        t = get_i18n(MetadataSlashCommandI18n, session.run_context.language)
        console = console_registry.get()

        key = await self._select_metadata_key(session, prompt=t.select_key_to_show)

        if key is None:
            return "user"

        value = session.history.metadata[key]
        console.print(Syntax(_dump_value(value), "json"))

        return "user"

    async def _handle_edit(self, session: ConsoleSession) -> ConsoleState:
        t = get_i18n(MetadataSlashCommandI18n, session.run_context.language)
        console = console_registry.get()

        key = await self._select_metadata_key(session, prompt=t.select_key_to_edit)

        if key is None:
            return "user"

        value = session.history.metadata[key]
        original_text = _dump_value(value)

        def validator(candidate: str) -> ValidationResult:
            try:
                json.loads(candidate)
            except json.JSONDecodeError as e:
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
            extension=".json",
            editing_mode=self.run_options.editing_mode,
        )

        if edited is None:
            console.print(t.edit_cancelled, style="yellow")
            return "user"

        if edited == original_text:
            console.print(t.edit_no_change, style="yellow")
            return "user"

        new_value = json.loads(edited)
        session.history.metadata[key] = new_value

        if not self.no_save:
            await self.history_repository.save(
                session.history,
                run_context=session.run_context,
            )

        console.print(t.metadata_updated.format(key=key), style="blue")
        return "user"

    async def _select_metadata_key(
        self,
        session: ConsoleSession,
        *,
        prompt: str,
    ) -> str | None:
        choices = [
            questionary.Choice(
                title=_format_metadata(key, session.history.metadata[key]),
                value=key,
            )
            for key in sorted(session.history.metadata)
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

        return str(selected)


def _format_metadata(key: str, value: Any) -> str:
    preview = json.dumps(value, ensure_ascii=False).replace("\n", " ")
    return f"{key}: {_shorten(preview, 120)}"


def _shorten(text: str, max_length: int) -> str:
    if len(text) <= max_length:
        return text

    return text[: max_length - 3] + "..."


def _dump_value(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)
