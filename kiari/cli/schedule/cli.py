import asyncio
from typing import Any

import rich_click as click

from kiari import cli
from kiari.core.rich import console_registry
from kiari.core.runtime import setup_runtime

from ._constants.schedule_option_group import SCHEDULE_OPTION_GROUP
from ._decorators.schedule_options import schedule_options
from ._operations.run_schedule import run_schedule

click.rich_click.OPTION_GROUPS["kiari schedule"] = [
    SCHEDULE_OPTION_GROUP,
    *cli.COMMON_OPTION_GROUPS,
]


@click.command(
    panel="Run Commands",
    help="Start schedule mode.",
)
@click.argument("watchers", nargs=-1, type=str, metavar="[WATCHER]...")
@schedule_options
@cli.common_options
def schedule(**kwargs: Any) -> None:
    asyncio.run(_schedule(**kwargs))


async def _schedule(**kwargs: Any) -> None:
    cli_args = cli.build_cli_args(**kwargs)

    profile_name, run_spec, run_options = cli.setup_profile(
        cli_args.profile_name,
        cli_args.save_mode,
        cli_args.run_spec,
    )

    if not run_options.interval and not run_options.cron:
        raise click.UsageError("Schedule mode requires --interval or --cron.")

    if run_options.interval and run_options.cron:
        raise click.UsageError("Schedule mode accepts either --interval or --cron, not both.")

    if renderable := cli.render_bootstrap_message(
        cli_args.exec_file,
        profile_name,
        run_spec,
        run_options,
    ):
        console_registry.get().print(renderable)

    await setup_runtime(profile_name, run_options)
    await cli.run(run_schedule, profile_name, run_options)
