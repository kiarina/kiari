from typing import Any

import rich_click as click

from kiari.core.paths import (
    get_profile_config_file_path,
    get_profile_dir_path,
    get_profile_run_spec_file_path,
)
from kiari.core.profile import profile_store
from kiari.core.rich import console_registry, render_status_block


@click.command(
    "delete",
    short_help="Delete a saved profile and its profile-specific files.",
    help=(
        "Delete a saved `kiari` profile.\n\n"
        "This command removes the profile entry from the profile store and also deletes "
        "the profile-specific `config.yaml` and `run_spec.yaml` files when they exist. "
        "The current profile cannot be deleted."
    ),
    epilog=(
        "Examples:\n\n"
        "kiari profile delete dev\n\n"
        "kiari profile delete production\n\n"
        "Use `kiari profile list` to inspect saved profiles before deleting one."
    ),
)
@click.argument("profile_name", type=str, metavar="PROFILE")
def delete(**kwargs: Any) -> None:  # pragma: no cover
    """Delete a profile."""
    _delete(**kwargs)


def _delete(profile_name: str) -> None:
    if not profile_store.has_profile(profile_name):
        raise click.ClickException(f"Profile not found: {profile_name}")

    if profile_store.get_current() == profile_name:
        raise click.ClickException(f"Cannot delete the current profile: {profile_name}")

    profile = profile_store.get_profile(profile_name)
    dir_path = get_profile_dir_path(profile_name)
    run_spec_file_path = get_profile_run_spec_file_path(profile_name)
    config_file_path = get_profile_config_file_path(profile_name)

    profile_store.delete_profile(profile_name)

    removed_run_spec_file = False

    if run_spec_file_path.exists():
        run_spec_file_path.unlink()
        removed_run_spec_file = True

    removed_config_file = False

    if config_file_path.exists():
        config_file_path.unlink()
        removed_config_file = True

    if dir_path.exists():
        try:
            dir_path.rmdir()
        except OSError:  # pragma: no cover
            pass

    console_registry.get().print(
        render_status_block(
            title=f"Deleted profile '{profile_name}'.",
            lines=[
                f"Deleted profile: [bold]{profile_name}[/bold]",
                f"Description: {profile.description or '-'}",
                f"Profile config file: [dim]{config_file_path}[/dim]",
                f"RunSpec file: [dim]{run_spec_file_path}[/dim]",
                (
                    "Removed profile config file."
                    if removed_config_file
                    else "Profile config file did not exist."
                ),
                (
                    "Removed RunSpec file."
                    if removed_run_spec_file
                    else "RunSpec file did not exist."
                ),
            ],
            status="success",
        )
    )
