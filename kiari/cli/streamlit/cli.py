from typing import Any

import rich_click as click
from kiarina.i18n import get_i18n, get_system_language

from kiari import cli
from kiari.core.rich import console_registry

from ._constants.streamlit_option_group import STREAMLIT_OPTION_GROUP
from ._decorators.streamlit_options import streamlit_options
from ._i18n import StreamlitI18n
from ._operations.run_streamlit import run_streamlit

t = get_i18n(StreamlitI18n, get_system_language())

click.rich_click.OPTION_GROUPS["kiari streamlit"] = [
    STREAMLIT_OPTION_GROUP,
    *cli.COMMON_OPTION_GROUPS,
]


@click.command(
    panel="Run Commands",
    help=t.command_help,
)
@streamlit_options
@cli.common_options
def streamlit(**kwargs: Any) -> None:
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

    run_streamlit(profile_name, run_options)
