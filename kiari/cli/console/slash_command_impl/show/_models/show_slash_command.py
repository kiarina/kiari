from collections.abc import Sequence

from kiarina.agi.event import Event, EventType
from kiarina.i18n import get_i18n
from rich.console import RenderableType
from rich.text import Text

from kiari.cli.console.console_handler import ConsoleSession
from kiari.cli.console.console_state import ConsoleState
from kiari.cli.console.slash_command import BaseSlashCommand
from kiari.core.rich import console_registry, join_renderables, render_event

from .._i18n import ShowSlashCommandI18n

_TARGET_MAP: dict[str, set[EventType]] = {
    "a": {"ai_message"},
    "h": {"human_message"},
    "t": {"tool_message"},
    "c": {"custom"},
}

_ALL_TARGETS: set[EventType] = {
    "ai_message",
    "human_message",
    "tool_message",
    "custom",
}


class ShowSlashCommand(BaseSlashCommand):
    def get_description(self, session: ConsoleSession) -> RenderableType:
        t = get_i18n(ShowSlashCommandI18n, session.run_context.language)
        return Text.from_markup(t.description)

    async def run(
        self,
        session: ConsoleSession,
        args: Sequence[str],
        content: str,
    ) -> ConsoleState:
        t = get_i18n(ShowSlashCommandI18n, session.run_context.language)
        console = console_registry.get()

        events = session.history.events

        if not events:
            console.print(t.no_history, style="yellow")
            return "user"

        target = args[0] if args else "*"
        range_str = args[1] if len(args) > 1 else None

        filtered = _filter_by_target(events, target)

        if range_str is not None:
            try:
                filtered = _apply_range(filtered, range_str)
            except ValueError:
                console.print(t.invalid_range.format(range=range_str), style="red")
                return "user"

        if not filtered:
            console.print(t.no_matching_events, style="yellow")
            return "user"

        console.print(Text())

        if renderable := join_renderables(
            [render_event(event) for event in filtered],
            separator=Text(),
        ):
            console.print(renderable)

        return "user"


def _filter_by_target(events: list[Event], target: str) -> list[Event]:
    if target == "*":
        return [e for e in events if e.type in _ALL_TARGETS]

    types: set[EventType] = set()
    for char in target:
        if char in _TARGET_MAP:
            types.update(_TARGET_MAP[char])

    if not types:
        return [e for e in events if e.type in _ALL_TARGETS]

    return [e for e in events if e.type in types]


def _apply_range(events: list[Event], range_str: str) -> list[Event]:
    if ":" not in range_str:
        raise ValueError(f"Range must contain ':' (got: {range_str})")

    parts = range_str.split(":")

    if len(parts) != 2:
        raise ValueError(f"Range must be 'start:end' format (got: {range_str})")

    start_str, end_str = parts
    start = int(start_str) if start_str else None
    end = int(end_str) if end_str else None

    return events[start:end]
