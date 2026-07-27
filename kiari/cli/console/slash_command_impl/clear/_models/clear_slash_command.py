import os
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

from kiarina.i18n import get_i18n
from rich.console import RenderableType
from rich.text import Text

from kiari.cli.console.console_handler import ConsoleSession
from kiari.cli.console.console_state import ConsoleState
from kiari.cli.console.slash_command import BaseSlashCommand
from kiari.core.rich import console_registry

from .._i18n import ClearSlashCommandI18n

ClearTarget = Literal["e", "f", "t", "m"]

_ALL_TARGETS: set[ClearTarget] = {"e", "f", "t", "m"}


@dataclass(frozen=True)
class ClearPlan:
    targets: set[ClearTarget]
    invalid_targets: set[str]


class ClearSlashCommand(BaseSlashCommand):
    def get_description(self, session: ConsoleSession) -> RenderableType:
        t = get_i18n(ClearSlashCommandI18n, session.run_context.language)
        return Text.from_markup(t.description)

    async def run(
        self,
        session: ConsoleSession,
        args: Sequence[str],
        content: str,
    ) -> ConsoleState:
        t = get_i18n(ClearSlashCommandI18n, session.run_context.language)
        console = console_registry.get()

        clear_plan = _parse_clear_plan(args)

        if clear_plan.invalid_targets:
            console.print(
                t.invalid_targets.format(targets="".join(sorted(clear_plan.invalid_targets))),
                style="yellow",
            )
            return "user"

        _clear_history(session, clear_plan.targets)

        session.clear_buffer()
        session.last_event = None

        if not self.no_save:
            if clear_plan.targets == _ALL_TARGETS:
                await self.history_repository.delete(session.run_context)
            else:
                await self.history_repository.save(
                    session.history,
                    run_context=session.run_context,
                )

        _clear_terminal()

        console.print(t.history_cleared, style="blue")

        return "user"


def _parse_clear_plan(args: Sequence[str]) -> ClearPlan:
    targets_text = "".join(args)

    if not targets_text:
        return ClearPlan(targets=set(_ALL_TARGETS), invalid_targets=set())

    targets: set[ClearTarget] = set()
    invalid_targets: set[str] = set()

    for target in targets_text:
        if target in _ALL_TARGETS:
            targets.add(target)
        else:
            invalid_targets.add(target)

    return ClearPlan(targets=targets, invalid_targets=invalid_targets)


def _clear_history(session: ConsoleSession, targets: set[ClearTarget]) -> None:
    if "e" in targets:
        session.history.events.clear()
    if "f" in targets:
        session.history.file_infos.clear()
    if "t" in targets:
        session.history.tool_infos.clear()
    if "m" in targets:
        session.history.metadata.clear()


def _clear_terminal() -> None:
    os.system("cls" if os.name == "nt" else "clear")
