import asyncio
from typing import Any

import rich_click as click

from kiari import cli
from kiari.core.rich import console_registry
from kiari.core.runtime import setup_runtime

from ._constants.watch_option_group import WATCH_OPTION_GROUP
from ._decorators.watch_options import watch_options
from ._operations.run_watch import run_watch

click.rich_click.OPTION_GROUPS["kiari watch"] = [
    WATCH_OPTION_GROUP,
    *cli.COMMON_OPTION_GROUPS,
]


@click.command(
    panel="Run Commands",
    help="Start watch mode.",
)
@click.argument("watchers", nargs=-1, type=str, metavar="[WATCHER]...")
@watch_options
@cli.common_options
def watch(**kwargs: Any) -> None:
    asyncio.run(_watch(**kwargs))


async def _watch(**kwargs: Any) -> None:
    cli_args = cli.build_cli_args(**kwargs)

    profile_name, run_spec, run_options = cli.setup_profile(
        cli_args.profile_name,
        cli_args.save_mode,
        cli_args.run_spec,
    )

    if renderable := cli.render_bootstrap_message(
        cli_args.exec_file, profile_name, run_spec, run_options
    ):
        console_registry.get().print(renderable)

    await setup_runtime(profile_name, run_options)
    await cli.run(run_watch, profile_name, run_options)
