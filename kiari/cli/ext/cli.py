import asyncio
from typing import Any

import rich_click as click
from rich.table import Table

from kiari import cli
from kiari.core.rich import console_registry
from kiari.core.runtime import setup_runtime

from ._operations.run_ext import run_ext
from .extension_command import extension_command_registry

click.rich_click.OPTION_GROUPS["kiari ext"] = [
    *cli.COMMON_OPTION_GROUPS,
]


# fmt: off
@click.command(
    panel="Run Commands",
    help="Run an extension command in the kiari runtime.",
    context_settings={
        "allow_extra_args": True,
        "allow_interspersed_args": False,
        "ignore_unknown_options": True,
    },
)
@click.argument("command_name", type=str, required=False)
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
@cli.common_options
def ext(**kwargs: Any) -> None:
    # fmt: on
    asyncio.run(_ext(**kwargs))


async def _ext(**kwargs: Any) -> None:
    cli_args = cli.build_cli_args(
        extra_args_keys=["command_name", "args"],
        **kwargs,
    )

    profile_name, run_spec, run_options = cli.setup_profile(
        cli_args.profile_name,
        cli_args.save_mode,
        cli_args.run_spec,
    )

    if renderable := cli.render_bootstrap_message(
        cli_args.exec_file,
        profile_name,
        run_spec,
        run_options,
    ):
        console_registry.get().print(renderable)

    await setup_runtime(profile_name, run_options)

    command_name = cli_args.extra_args.get("command_name")

    if command_name is None:
        _print_command_list()
        return

    await cli.run(
        run_ext,
        profile_name,
        run_options,
        command_name,
        cli_args.extra_args.get("args", []),
    )


def _print_command_list() -> None:
    console = console_registry.get()
    names = extension_command_registry.list_names()

    if not names:
        console.print("No extension commands are available.", style="yellow")
        return

    table = Table(
        title="Available Extension Commands",
        show_header=True,
        show_edge=True,
        padding=(0, 1),
        border_style="blue",
        caption=f"{len(names)} command(s) | Run: kiari ext <command_name> [args...]",
        caption_style="dim",
    )
    table.add_column("Command", style="bold cyan")

    for name in names:
        table.add_row(name)

    console.print(table)
