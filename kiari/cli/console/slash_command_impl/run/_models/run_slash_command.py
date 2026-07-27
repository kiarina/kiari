from collections.abc import Sequence
from dataclasses import dataclass, field

from kiarina.agi.tool_info import ToolName
from kiarina.i18n import get_i18n
from rich.console import RenderableType
from rich.text import Text

from kiari.cli.console.console_handler import ConsoleSession
from kiari.cli.console.console_state import ConsoleState
from kiari.cli.console.slash_command import BaseSlashCommand
from kiari.core.rich import console_registry

from .._i18n import RunSlashCommandI18n


@dataclass(frozen=True)
class RunPlan:
    max_iterations: int | None = None
    until_end: bool | None = None
    until_tool_calls: list[ToolName] | None = None
    until_tool_runs: list[ToolName] | None = None
    invalid_args: list[str] = field(default_factory=list)
    missing_value_option: str | None = None


class RunSlashCommand(BaseSlashCommand):
    def get_description(self, session: ConsoleSession) -> RenderableType:
        t = get_i18n(RunSlashCommandI18n, session.run_context.language)
        return Text.from_markup(t.description)

    async def run(
        self,
        session: ConsoleSession,
        args: Sequence[str],
        content: str,
    ) -> ConsoleState:
        t = get_i18n(RunSlashCommandI18n, session.run_context.language)
        console = console_registry.get()
        plan = _parse_run_plan(args)

        if plan.missing_value_option:
            console.print(
                t.missing_value.format(option=plan.missing_value_option),
                style="yellow",
            )
            return "user"

        if plan.invalid_args:
            console.print(
                t.invalid_args.format(args=", ".join(plan.invalid_args)),
                style="yellow",
            )
            return "user"

        _apply_run_plan(session, plan)
        _print_run_plan(session, plan)

        session.text = content

        return "agent"


def _parse_run_plan(args: Sequence[str]) -> RunPlan:
    max_iterations: int | None = None
    until_end: bool | None = None
    until_tool_calls: list[ToolName] = []
    until_tool_runs: list[ToolName] = []
    invalid_args: list[str] = []
    missing_value_option: str | None = None
    index = 0

    while index < len(args):
        arg = args[index]

        if arg == "--until-end":
            until_end = True
            index += 1
            continue

        if arg in {"--until-tool-call", "--until-tool-run"}:
            if index + 1 >= len(args):
                missing_value_option = arg
                break

            tool_name = args[index + 1]

            if tool_name.startswith("--"):
                missing_value_option = arg
                break

            if arg == "--until-tool-call":
                until_tool_calls.append(tool_name)
            else:
                until_tool_runs.append(tool_name)

            index += 2
            continue

        if arg.isdigit():
            max_iterations = int(arg)
            index += 1
            continue

        invalid_args.append(arg)
        index += 1

    return RunPlan(
        max_iterations=max_iterations,
        until_end=until_end,
        until_tool_calls=until_tool_calls or None,
        until_tool_runs=until_tool_runs or None,
        invalid_args=invalid_args,
        missing_value_option=missing_value_option,
    )


def _apply_run_plan(session: ConsoleSession, plan: RunPlan) -> None:
    if plan.max_iterations is not None:
        session.max_iterations = plan.max_iterations
    if plan.until_end is not None:
        session.until_end = plan.until_end
    if plan.until_tool_calls is not None:
        session.until_tool_calls = plan.until_tool_calls
    if plan.until_tool_runs is not None:
        session.until_tool_runs = plan.until_tool_runs


def _print_run_plan(session: ConsoleSession, plan: RunPlan) -> None:
    t = get_i18n(RunSlashCommandI18n, session.run_context.language)
    console = console_registry.get()

    console.print(t.run_started, style="blue")

    if plan.max_iterations is not None:
        console.print(
            t.set_max_iterations.format(max_iterations=plan.max_iterations),
            style="blue",
        )
    if plan.until_end is not None:
        console.print(t.set_until_end, style="blue")
    if plan.until_tool_calls is not None:
        console.print(
            t.set_until_tool_calls.format(tool_names=", ".join(plan.until_tool_calls)),
            style="blue",
        )
    if plan.until_tool_runs is not None:
        console.print(
            t.set_until_tool_runs.format(tool_names=", ".join(plan.until_tool_runs)),
            style="blue",
        )
