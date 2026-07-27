from collections.abc import Sequence

from kiarina.i18n import get_i18n
from rich.console import RenderableType
from rich.text import Text

from kiari.cli.console.console_handler import ConsoleSession
from kiari.cli.console.console_state import ConsoleState
from kiari.cli.console.slash_command import BaseSlashCommand
from kiari.core.rich import console_registry

from .._i18n import BackSlashCommandI18n


class BackSlashCommand(BaseSlashCommand):
    def get_description(self, session: ConsoleSession) -> RenderableType:
        t = get_i18n(BackSlashCommandI18n, session.run_context.language)
        return Text.from_markup(t.description)

    async def run(
        self,
        session: ConsoleSession,
        args: Sequence[str],
        content: str,
    ) -> ConsoleState:
        t = get_i18n(BackSlashCommandI18n, session.run_context.language)
        console = console_registry.get()

        if not session.history.events:
            console.print(t.no_history, style="yellow")
            return "user"

        if not args:
            changed = _revert_to_previous_turn(session)
        else:
            changed = _delete_last_events(session, args)

        if not changed:
            return "user"

        if not self.no_save:
            await self.history_repository.save(
                session.history,
                run_context=session.run_context,
            )

        return "user"


def _revert_to_previous_turn(session: ConsoleSession) -> bool:
    t = get_i18n(BackSlashCommandI18n, session.run_context.language)
    console = console_registry.get()

    if _delete_from_last_event_type(session, "human_message"):
        console.print(t.reverted_to_previous, style="blue")
        return True

    if _delete_from_last_event_type(session, "ai_message"):
        console.print(t.reverted_to_previous, style="blue")
        return True

    console.print(t.no_human_message, style="yellow")
    return False


def _delete_last_events(
    session: ConsoleSession,
    args: Sequence[str],
) -> bool:
    t = get_i18n(BackSlashCommandI18n, session.run_context.language)
    console = console_registry.get()
    events = session.history.events

    try:
        n = int(args[0])
    except ValueError:
        console.print(t.invalid_n, style="yellow")
        return False

    if n <= 0:
        console.print(t.invalid_n, style="yellow")
        return False

    if n >= len(events):
        session.history.events.clear()
        console.print(t.all_history_deleted, style="blue")
    else:
        del session.history.events[-n:]
        console.print(t.deleted_n_events.format(n=n), style="blue")

    return True


def _delete_from_last_event_type(session: ConsoleSession, event_type: str) -> bool:
    events = session.history.events

    for i in range(len(events) - 1, -1, -1):
        if events[i].type == event_type:
            del session.history.events[i:]
            return True

    return False
