from collections.abc import Sequence

import questionary
from kiarina.agi.tool import Tool, ToolSpecifier, tool_registry
from kiarina.i18n import get_i18n
from rich.console import RenderableType
from rich.text import Text

from kiari.cli.console.console_handler import ConsoleSession
from kiari.cli.console.console_state import ConsoleState
from kiari.cli.console.slash_command import BaseSlashCommand
from kiari.core.rich import console_registry
from kiari.core.terminal import create_prompt_toolkit_io

from .._i18n import ToolSlashCommandI18n

_COMMANDS_REQUIRING_TOOLS: frozenset[str] = frozenset({"list", "remove"})


class ToolSlashCommand(BaseSlashCommand):
    def get_description(self, session: ConsoleSession) -> RenderableType:
        t = get_i18n(ToolSlashCommandI18n, session.run_context.language)
        return Text.from_markup(t.description)

    async def run(
        self,
        session: ConsoleSession,
        args: Sequence[str],
        content: str,
    ) -> ConsoleState:
        t = get_i18n(ToolSlashCommandI18n, session.run_context.language)
        console = console_registry.get()

        if not args:
            return self._handle_help(session)

        command, *rest = args

        if command in _COMMANDS_REQUIRING_TOOLS and not _get_tools(session):
            console.print(t.no_tools, style="yellow")
            return "user"

        if command == "list":
            return self._handle_list(session)

        if command == "add":
            if content:
                rest.append(content)

            return await self._handle_add(session, rest)

        if command == "remove":
            return await self._handle_remove(session)

        console.print(
            t.unknown_subcommand.format(command=command),
            style="yellow",
        )
        return "user"

    def _handle_help(self, session: ConsoleSession) -> ConsoleState:
        t = get_i18n(ToolSlashCommandI18n, session.run_context.language)
        console = console_registry.get()
        console.print(Text.from_markup(t.description))
        return "user"

    def _handle_list(self, session: ConsoleSession) -> ConsoleState:
        _print_tools(_get_tools(session))
        return "user"

    async def _handle_add(
        self,
        session: ConsoleSession,
        args: Sequence[ToolSpecifier],
    ) -> ConsoleState:
        if not args:
            return await self._handle_select_add(session)

        return await self._add_specifiers(session, args)

    async def _handle_select_add(self, session: ConsoleSession) -> ConsoleState:
        t = get_i18n(ToolSlashCommandI18n, session.run_context.language)
        console = console_registry.get()

        available_names = sorted(tool_registry.list_names())

        if not available_names:
            console.print(t.no_available_tools, style="yellow")
            return "user"

        # Show current tools for context (so users know what's already added)
        current_tools = _get_tools(session)

        if current_tools:
            _print_tools(current_tools)

        choices = [questionary.Choice(title=name, value=name) for name in available_names]

        selected = await questionary.checkbox(
            t.select_tools_to_add,
            choices=choices,
            use_search_filter=True,
            use_jk_keys=False,
            **create_prompt_toolkit_io(),
        ).ask_async()

        if not selected:
            return "user"

        return await self._add_specifiers(session, selected)

    async def _add_specifiers(
        self,
        session: ConsoleSession,
        specifiers: Sequence[ToolSpecifier],
    ) -> ConsoleState:
        t = get_i18n(ToolSlashCommandI18n, session.run_context.language)
        console = console_registry.get()

        tools = list(session.tool_options.get("tools") or [])

        for tool_specifier in specifiers:
            tool = tool_registry.resolve(tool_specifier)

            # Replace by name (remove existing with same name, then append)
            tools = [existing for existing in tools if _get_tool_name(existing) != tool.name]
            tools.append(tool)

            # Update tool_info with the configured default state
            tool_info = tool.to_tool_info(session.run_context.language)
            tool_info.state = self.run_options.default_tool_state
            session.history.add_tool_info(tool_info)

        session.tool_options["tools"] = tools

        if not self.no_save:
            await self.history_repository.save(
                session.history,
                run_context=session.run_context,
            )

        console.print(t.added_n_tools.format(n=len(specifiers)), style="blue")
        _print_tools(tools)

        return "user"

    async def _handle_remove(self, session: ConsoleSession) -> ConsoleState:
        t = get_i18n(ToolSlashCommandI18n, session.run_context.language)
        console = console_registry.get()

        tools = _get_tools(session)

        choices = [
            questionary.Choice(title=_format_tool(tool, index), value=index)
            for index, tool in enumerate(tools)
        ]

        selected = await questionary.checkbox(
            t.select_tools_to_delete,
            choices=choices,
            use_search_filter=True,
            use_jk_keys=False,
            **create_prompt_toolkit_io(),
        ).ask_async()

        if not selected:
            return "user"

        selected_indexes = set(selected)
        removed_names = {
            _get_tool_name(tool) for index, tool in enumerate(tools) if index in selected_indexes
        }

        # Update tool_options
        session.tool_options["tools"] = [
            tool for index, tool in enumerate(tools) if index not in selected_indexes
        ]

        # Disable matching tool_infos (do not delete)
        for tool_info in session.history.tool_infos:
            if tool_info.name in removed_names:
                tool_info.state = "disabled"

        # Remove ToolCall / ToolMessage referencing removed tools from events
        _strip_tool_references_from_events(session, removed_names)

        if not self.no_save:
            await self.history_repository.save(
                session.history,
                run_context=session.run_context,
            )

        console.print(
            t.deleted_n_tools.format(n=len(selected_indexes)),
            style="blue",
        )
        _print_tools(_get_tools(session))

        return "user"


def _get_tools(session: ConsoleSession) -> list[Tool | ToolSpecifier]:
    return list(session.tool_options.get("tools") or [])


def _print_tools(tools: Sequence[Tool | ToolSpecifier]) -> None:
    console = console_registry.get()

    for index, tool in enumerate(tools):
        console.print(_format_tool(tool, index), style="blue")


def _format_tool(tool: Tool | ToolSpecifier, index: int) -> str:
    return f"{index}: {_get_tool_name(tool)}"


def _get_tool_name(tool: Tool | ToolSpecifier) -> str:
    if isinstance(tool, str):
        return tool.split("?", 1)[0]

    return tool.name


def _strip_tool_references_from_events(
    session: ConsoleSession,
    removed_names: set[str],
) -> None:
    if not removed_names:
        return  # pragma: no cover

    new_events = []

    for event in session.history.events:
        if event.type == "tool_message":
            if event.message.tool_name in removed_names:
                continue

        elif event.type == "ai_message":
            event.message.tool_calls = [
                tool_call
                for tool_call in event.message.tool_calls
                if tool_call.name not in removed_names
            ]

            if not event.message.tool_calls:
                continue

        new_events.append(event)

    session.history.events = new_events
