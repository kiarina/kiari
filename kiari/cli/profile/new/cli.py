from typing import Any

import rich_click as click

from kiari.core.paths import (
    get_profile_config_file_path,
    get_profile_run_spec_file_path,
)
from kiari.core.profile import Profile, profile_store
from kiari.core.rich import console_registry, render_status_block


@click.command(
    "new",
    short_help="Create a new saved profile and initialize its profile-specific files.",
    help=(
        "Create a new saved `kiari` profile.\n\n"
        "This command creates the profile entry and initializes the profile-specific "
        "`run_spec.yaml` and `config.yaml` files when they do not exist yet. "
        "If the profile already exists, the command fails."
    ),
    epilog=(
        "Examples:\n\n"
        "kiari profile new dev\n\n"
        'kiari profile new production --description "Production settings"\n\n'
        "Use `kiari profile use <name>` to switch to the new profile afterwards."
    ),
)
@click.argument("profile_name", type=str, metavar="PROFILE")
@click.option(
    "-d",
    "--description",
    type=str,
    help="Description to store with the new profile.",
)
def new(**kwargs: Any) -> None:  # pragma: no cover
    """Create a new profile."""
    _new(**kwargs)


def _new(profile_name: str, description: str | None = None) -> None:
    if profile_store.has_profile(profile_name):
        raise click.ClickException(f"Profile already exists: {profile_name}")

    profile = Profile(name=profile_name, description=description or "")
    profile_store.set_profile(profile)

    run_spec_file_path = get_profile_run_spec_file_path(profile_name)
    config_file_path = get_profile_config_file_path(profile_name)
    created_run_spec = profile_store.ensure_run_spec(profile_name)
    created_config = profile_store.ensure_config(profile_name)

    console_registry.get().print(
        render_status_block(
            title=f"Created profile '{profile_name}'.",
            lines=[
                f"Created profile: [bold]{profile_name}[/bold]",
                f"Description: {profile.description or '-'}",
                f"RunSpec file: [dim]{run_spec_file_path}[/dim]",
                f"Config file: [dim]{config_file_path}[/dim]",
                ("Created RunSpec file." if created_run_spec else "RunSpec file already exists."),
                ("Created config file." if created_config else "Config file already exists."),
                "Current profile unchanged.",
            ],
            status="success",
        )
    )
