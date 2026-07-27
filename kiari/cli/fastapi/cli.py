from typing import Any

import rich_click as click
from kiarina.i18n import get_i18n, get_system_language

from kiari import cli
from kiari.core.rich import console_registry

from ._constants.fastapi_option_group import FASTAPI_OPTION_GROUP
from ._decorators.fastapi_options import fastapi_options
from ._i18n import FastAPII18n
from ._operations.run_fastapi import run_fastapi

t = get_i18n(FastAPII18n, get_system_language())

click.rich_click.OPTION_GROUPS["kiari fastapi"] = [
    FASTAPI_OPTION_GROUP,
    *cli.COMMON_OPTION_GROUPS,
]


@click.command(
    panel="Run Commands",
    help=t.command_help,
)
@fastapi_options
@cli.common_options
def fastapi(**kwargs: Any) -> None:
    cli_args = cli.build_cli_args(**kwargs)

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

    run_fastapi(profile_name, run_options)
