from collections.abc import Sequence

import questionary
from kiarina.agi.event import Event
from kiarina.agi.event_builder import build_event, parse_event_specifier
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

from .._i18n import EventSlashCommandI18n

_event_adapter: TypeAdapter[Event] = TypeAdapter(Event)

_COMMANDS_REQUIRING_EVENTS: frozenset[str] = frozenset({"list", "remove", "show", "edit"})


class EventSlashCommand(BaseSlashCommand):
    def get_description(self, session: ConsoleSession) -> RenderableType:
        t = get_i18n(EventSlashCommandI18n, session.run_context.language)
        return Text.from_markup(t.description)

    async def run(
        self,
        session: ConsoleSession,
        args: Sequence[str],
        content: str,
    ) -> ConsoleState:
        t = get_i18n(EventSlashCommandI18n, session.run_context.language)
        console = console_registry.get()

        if not args:
            return self._handle_help(session)

        command, *rest = args

        if command in _COMMANDS_REQUIRING_EVENTS and not session.history.events:
            console.print(t.no_events, style="yellow")
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
        t = get_i18n(EventSlashCommandI18n, session.run_context.language)
        console = console_registry.get()
        console.print(Text.from_markup(t.description))
        return "user"

    def _handle_list(self, session: ConsoleSession) -> ConsoleState:
        console = console_registry.get()

        for index, event in enumerate(session.history.events):
            console.print(_format_event(event, index), style="blue")

        return "user"

    async def _handle_add(
        self,
        session: ConsoleSession,
        args: Sequence[str],
    ) -> ConsoleState:
        t = get_i18n(EventSlashCommandI18n, session.run_context.language)
        console = console_registry.get()

        if not args:
            console.print(Text.from_markup(t.add_examples))
            return "user"

        for event_specifier in args:
            event = await build_event(
                parse_event_specifier(event_specifier),
                run_context=session.run_context,
            )
            session.history.add_event(event)

        if not self.no_save:
            await self.history_repository.save(
                session.history,
                run_context=session.run_context,
            )

        console.print(t.added_n_events.format(n=len(args)), style="blue")

        return "user"

    async def _handle_remove(self, session: ConsoleSession) -> ConsoleState:
        t = get_i18n(EventSlashCommandI18n, session.run_context.language)
        console = console_registry.get()

        choices = [
            questionary.Choice(title=_format_event(event, index), value=index)
            for index, event in enumerate(session.history.events)
        ]

        selected = await questionary.checkbox(
            t.select_events_to_delete,
            choices=choices,
            use_search_filter=True,
            use_jk_keys=False,
            **create_prompt_toolkit_io(),
        ).ask_async()

        if not selected:
            return "user"

        selected_indexes = set(selected)

        session.history.events = [
            event
            for index, event in enumerate(session.history.events)
            if index not in selected_indexes
        ]

        if not self.no_save:
            await self.history_repository.save(
                session.history,
                run_context=session.run_context,
            )

        console.print(t.deleted_n_events.format(n=len(selected_indexes)), style="blue")

        return "user"

    async def _handle_show(self, session: ConsoleSession) -> ConsoleState:
        t = get_i18n(EventSlashCommandI18n, session.run_context.language)
        console = console_registry.get()

        index = await self._select_event_index(session, prompt=t.select_event_to_show)

        if index is None:
            return "user"

        event = session.history.events[index]
        console.print(Syntax(event.model_dump_json(indent=2), "json"))

        return "user"

    async def _handle_edit(self, session: ConsoleSession) -> ConsoleState:
        t = get_i18n(EventSlashCommandI18n, session.run_context.language)
        console = console_registry.get()

        index = await self._select_event_index(session, prompt=t.select_event_to_edit)

        if index is None:
            return "user"

        event = session.history.events[index]
        original_text = event.model_dump_json(indent=2)

        def validator(candidate: str) -> ValidationResult:
            try:
                _event_adapter.validate_json(candidate)
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

        new_event = _event_adapter.validate_json(edited)
        session.history.events[index] = new_event

        if not self.no_save:
            await self.history_repository.save(
                session.history,
                run_context=session.run_context,
            )

        console.print(t.event_updated.format(index=index), style="blue")
        return "user"

    async def _select_event_index(
        self,
        session: ConsoleSession,
        *,
        prompt: str,
    ) -> int | None:
        choices = [
            questionary.Choice(title=_format_event(event, i), value=i)
            for i, event in enumerate(session.history.events)
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


def _format_event(event: Event, index: int) -> str:
    text = event.to_text().replace("\n", " ")
    return f"{index}: {event.type} {text[:20]}"
