from datetime import UTC, datetime
from typing import Any

import rich_click as click

from kiari.core.profile import profile_store
from kiari.core.rich import console_registry, render_status_block


@click.command(
    "set",
    short_help="Update metadata for an existing saved profile.",
    help=(
        "Update metadata for an existing saved `kiari` profile.\n\n"
        "When `PROFILE` is omitted, the current profile is updated.\n\n"
        "This command updates editable profile fields such as the description. "
        "If the target profile does not exist, the command fails."
    ),
    epilog=(
        "Examples:\n\n"
        'kiari profile set --description "Development settings"\n\n'
        'kiari profile set dev --description "Development settings"\n\n'
        'kiari profile set production --description ""\n\n'
        "Use `kiari profile list` to inspect profile metadata after updating it."
    ),
)
@click.argument("profile_name", type=str, metavar="PROFILE", required=False)
@click.option(
    "-d",
    "--description",
    type=str,
    default=None,
    help="New description to store for the profile.",
)
def set_command(**kwargs: Any) -> None:  # pragma: no cover
    """Update a profile."""
    _set(**kwargs)


def _set(profile_name: str | None = None, description: str | None = None) -> None:
    profile_name = profile_name or profile_store.get_current()

    if not profile_store.has_profile(profile_name):
        raise click.ClickException(f"Profile not found: {profile_name}")

    if description is None:
        raise click.ClickException("No updates specified.")

    updated_profile = profile_store.get_profile(profile_name).model_copy(
        update={
            "description": description,
            "updated_at": datetime.now(UTC),
        }
    )
    profile_store.set_profile(updated_profile)

    console_registry.get().print(
        render_status_block(
            title=f"Updated profile '{profile_name}'.",
            lines=[
                f"Updated profile: [bold]{profile_name}[/bold]",
                f"Description: {updated_profile.description or '-'}",
                f"Updated at: {updated_profile.updated_at.astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')}",
                "Current profile unchanged.",
            ],
            status="success",
        )
    )
