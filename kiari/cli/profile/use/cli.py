from typing import Any

import rich_click as click

from kiari.core.paths import (
    get_profile_config_file_path,
    get_profile_run_spec_file_path,
)
from kiari.core.profile import profile_store
from kiari.core.rich import console_registry, render_status_block


@click.command(
    "use",
    short_help="Switch the current profile to an existing saved profile.",
    help=(
        "Switch the current `kiari` profile.\n\n"
        "This command switches the current profile to an existing saved profile. "
        "If the target profile does not exist, the command fails."
    ),
    epilog=(
        "Examples:\n\n"
        "kiari profile use dev\n\n"
        "kiari profile use production\n\n"
        "Use `kiari profile list` to inspect the available profiles after switching."
    ),
)
@click.argument("profile_name", type=str, metavar="PROFILE")
def use(**kwargs: Any) -> None:  # pragma: no cover
    """Switch the current profile."""
    _use(**kwargs)


def _use(profile_name: str) -> None:
    if not profile_store.has_profile(profile_name):
        raise click.ClickException(f"Profile not found: {profile_name}")

    profile_store.set_current(profile_name)
    profile = profile_store.get_profile(profile_name)
    run_spec_file_path = get_profile_run_spec_file_path(profile_name)
    config_file_path = get_profile_config_file_path(profile_name)

    console_registry.get().print(
        render_status_block(
            title=f"Current profile set to '{profile_name}'.",
            lines=[
                f"Current profile: [bold]{profile_name}[/bold]",
                f"Using existing profile '{profile_name}'.",
                f"Description: {profile.description or '-'}",
                f"RunSpec file: [dim]{run_spec_file_path}[/dim]",
                f"Config file: [dim]{config_file_path}[/dim]",
                "RunSpec file unchanged.",
                "Config file unchanged.",
            ],
            status="success",
        )
    )
