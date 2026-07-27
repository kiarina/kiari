from collections.abc import Sequence

import questionary
from kiarina.agi.tool_info import ToolInfo
from kiarina.agi.tool_info_builder import resolve_tool_info
from kiarina.i18n import get_i18n
from pydantic import TypeAdapter, ValidationError
from rich.console import RenderableType
from rich.syntax import Syntax
from rich.text import Text

from kiari.cli.console.console_handler import ConsoleSession
from kiari.cli.console.console_state import ConsoleState
from kiari.cli.console.slash_command import BaseSlashCommand
from kiari.core.editor import ValidationResult, edit_text_with_validation
from kiari.core.rich import console_registry
from kiari.core.terminal import create_prompt_toolkit_io

from .._i18n import ToolInfoSlashCommandI18n

_tool_info_adapter: TypeAdapter[ToolInfo] = TypeAdapter(ToolInfo)

_COMMANDS_REQUIRING_TOOL_INFOS: frozenset[str] = frozenset(
    {"list", "remove", "show", "edit", "arrange"}
)

_VALID_STATES: frozenset[str] = frozenset({"active", "inactive", "disabled"})


class ToolInfoSlashCommand(BaseSlashCommand):
    def get_description(self, session: ConsoleSession) -> RenderableType:
        t = get_i18n(ToolInfoSlashCommandI18n, session.run_context.language)
        return Text.from_markup(t.description)

    async def run(
        self,
        session: ConsoleSession,
        args: Sequence[str],
        content: str,
    ) -> ConsoleState:
        t = get_i18n(ToolInfoSlashCommandI18n, session.run_context.language)
        console = console_registry.get()

        if not args:
            return self._handle_help(session)

        command, *rest = args

        if command in _COMMANDS_REQUIRING_TOOL_INFOS and not session.history.tool_infos:
            console.print(t.no_tool_infos, style="yellow")
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

        if command == "arrange":
            return await self._handle_arrange(session)

        console.print(
            t.unknown_subcommand.format(command=command),
            style="yellow",
        )
        return "user"

    def _handle_help(self, session: ConsoleSession) -> ConsoleState:
        t = get_i18n(ToolInfoSlashCommandI18n, session.run_context.language)
        console = console_registry.get()
        console.print(Text.from_markup(t.description))
        return "user"

    def _handle_list(self, session: ConsoleSession) -> ConsoleState:
        console = console_registry.get()

        for index, tool_info in enumerate(session.history.tool_infos):
            console.print(_format_tool_info(tool_info, index), style="blue")

        return "user"

    async def _handle_add(
        self,
        session: ConsoleSession,
        args: Sequence[str],
    ) -> ConsoleState:
        t = get_i18n(ToolInfoSlashCommandI18n, session.run_context.language)
        console = console_registry.get()

        if not args:
            console.print(Text.from_markup(t.add_examples))
            return "user"

        for tool_info_specifier in args:
            tool_info = resolve_tool_info(
                tool_info_specifier,
                language=session.run_context.language,
            )
            session.history.add_tool_info(tool_info)

        if not self.no_save:
            await self.history_repository.save(
                session.history,
                run_context=session.run_context,
            )

        console.print(t.added_n_tool_infos.format(n=len(args)), style="blue")

        return "user"

    async def _handle_remove(self, session: ConsoleSession) -> ConsoleState:
        t = get_i18n(ToolInfoSlashCommandI18n, session.run_context.language)
        console = console_registry.get()

        choices = [
            questionary.Choice(title=_format_tool_info(tool_info, index), value=index)
            for index, tool_info in enumerate(session.history.tool_infos)
        ]

        selected = await questionary.checkbox(
            t.select_tool_infos_to_delete,
            choices=choices,
            use_search_filter=True,
            use_jk_keys=False,
            **create_prompt_toolkit_io(),
        ).ask_async()

        if not selected:
            return "user"

        selected_indexes = set(selected)

        session.history.tool_infos = [
            tool_info
            for index, tool_info in enumerate(session.history.tool_infos)
            if index not in selected_indexes
        ]

        if not self.no_save:
            await self.history_repository.save(
                session.history,
                run_context=session.run_context,
            )

        console.print(t.deleted_n_tool_infos.format(n=len(selected_indexes)), style="blue")

        return "user"

    async def _handle_show(self, session: ConsoleSession) -> ConsoleState:
        t = get_i18n(ToolInfoSlashCommandI18n, session.run_context.language)
        console = console_registry.get()

        index = await self._select_tool_info_index(session, prompt=t.select_tool_info_to_show)

        if index is None:
            return "user"

        tool_info = session.history.tool_infos[index]
        console.print(Syntax(tool_info.model_dump_json(indent=2), "json"))

        return "user"

    async def _handle_edit(self, session: ConsoleSession) -> ConsoleState:
        t = get_i18n(ToolInfoSlashCommandI18n, session.run_context.language)
        console = console_registry.get()

        index = await self._select_tool_info_index(session, prompt=t.select_tool_info_to_edit)

        if index is None:
            return "user"

        tool_info = session.history.tool_infos[index]
        original_text = tool_info.model_dump_json(indent=2)

        def validator(candidate: str) -> ValidationResult:
            try:
                _tool_info_adapter.validate_json(candidate)
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
            extension=".json",
            editing_mode=self.run_options.editing_mode,
        )

        if edited is None:
            console.print(t.edit_cancelled, style="yellow")
            return "user"

        if edited == original_text:
            console.print(t.edit_no_change, style="yellow")
            return "user"

        new_tool_info = _tool_info_adapter.validate_json(edited)
        session.history.tool_infos[index] = new_tool_info

        if not self.no_save:
            await self.history_repository.save(
                session.history,
                run_context=session.run_context,
            )

        console.print(t.tool_info_updated.format(index=index), style="blue")
        return "user"

    async def _handle_arrange(self, session: ConsoleSession) -> ConsoleState:
        t = get_i18n(ToolInfoSlashCommandI18n, session.run_context.language)
        console = console_registry.get()

        tool_infos = session.history.tool_infos
        existing_by_name = {tool_info.name: tool_info for tool_info in tool_infos}

        item_lines = [f"{tool_info.state} {tool_info.name}" for tool_info in tool_infos]
        original_text = f"# {t.arrange_instruction}\n\n" + "\n".join(item_lines)

        def parse(text: str) -> tuple[list[tuple[str, str]] | None, Text | None]:
            entries: list[tuple[str, str]] = []
            seen_names: set[str] = set()

            for line_no, raw_line in enumerate(text.splitlines(), start=1):
                stripped = raw_line.strip()
                if not stripped or stripped.startswith("#"):
                    continue

                parts = stripped.split(None, 1)
                if len(parts) != 2:
                    return None, Text(
                        t.arrange_invalid_line.format(line_no=line_no),
                        style="red",
                    )

                state, name = parts

                if state not in _VALID_STATES:
                    return None, Text(
                        t.arrange_invalid_state.format(line_no=line_no, state=state),
                        style="red",
                    )

                if name not in existing_by_name:
                    return None, Text(
                        t.arrange_unknown_name.format(line_no=line_no, name=name),
                        style="red",
                    )

                if name in seen_names:
                    return None, Text(
                        t.arrange_duplicate_name.format(name=name),
                        style="red",
                    )

                seen_names.add(name)
                entries.append((state, name))

            missing = set(existing_by_name) - seen_names
            if missing:
                return None, Text(
                    t.arrange_missing_names.format(names=", ".join(sorted(missing))),
                    style="red",
                )

            return entries, None

        def validator(candidate: str) -> ValidationResult:
            _, error = parse(candidate)
            if error is not None:
                return ValidationResult(valid=False, message=error)
            return ValidationResult(valid=True)

        edited = await edit_text_with_validation(
            original_text,
            validator=validator,
            extension=".txt",
            editing_mode=self.run_options.editing_mode,
        )

        if edited is None:
            console.print(t.arrange_cancelled, style="yellow")
            return "user"

        entries, _ = parse(edited)
        assert entries is not None  # pragma: no cover

        new_tool_infos = [
            existing_by_name[name].model_copy(update={"state": state}) for state, name in entries
        ]

        if new_tool_infos == tool_infos:
            console.print(t.arrange_no_change, style="yellow")
            return "user"

        session.history.tool_infos = new_tool_infos

        if not self.no_save:
            await self.history_repository.save(
                session.history,
                run_context=session.run_context,
            )

        console.print(t.arranged, style="blue")
        return "user"

    async def _select_tool_info_index(
        self,
        session: ConsoleSession,
        *,
        prompt: str,
    ) -> int | None:
        choices = [
            questionary.Choice(title=_format_tool_info(tool_info, i), value=i)
            for i, tool_info in enumerate(session.history.tool_infos)
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


def _format_tool_info(tool_info: ToolInfo, index: int) -> str:
    return f"{index}: {tool_info.state} {tool_info.name} {_shorten(tool_info.description, 80)}"


def _shorten(text: str, max_length: int) -> str:
    text = text.replace("\n", " ")

    if len(text) <= max_length:
        return text

    return text[: max_length - 3] + "..."
