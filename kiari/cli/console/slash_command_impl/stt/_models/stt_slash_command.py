from collections.abc import Sequence

from kiarina.i18n import get_i18n
from rich.console import RenderableType
from rich.text import Text

from kiari.cli.console.console_handler import ConsoleSession
from kiari.cli.console.console_state import ConsoleState
from kiari.cli.console.slash_command import BaseSlashCommand
from kiari.core.rich import console_registry

from .._i18n import STTSlashCommandI18n


class STTSlashCommand(BaseSlashCommand):
    def get_description(self, session: ConsoleSession) -> RenderableType:
        t = get_i18n(STTSlashCommandI18n, session.run_context.language)
        return Text.from_markup(t.description)

    async def run(
        self,
        session: ConsoleSession,
        args: Sequence[str],
        content: str,
    ) -> ConsoleState:
        t = get_i18n(STTSlashCommandI18n, session.run_context.language)
        console = console_registry.get()

        if not args:
            session.stt_enabled = not session.stt_enabled
            console.print(
                t.stt_enabled if session.stt_enabled else t.stt_disabled,
                style="blue",
            )
            return "user"

        if len(args) != 1 or args[0] not in {"on", "off"}:
            console.print(t.invalid_mode, style="yellow")
            return "user"

        session.stt_enabled = args[0] == "on"
        console.print(t.stt_enabled if session.stt_enabled else t.stt_disabled, style="blue")

        return "user"
