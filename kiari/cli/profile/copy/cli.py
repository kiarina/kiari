from typing import Any

import rich_click as click

from kiari.core.paths import (
    get_profile_config_file_path,
    get_profile_run_spec_file_path,
)
from kiari.core.profile import Profile, profile_store
from kiari.core.rich import console_registry, render_status_block


@click.command(
    "copy",
    short_help="Copy an existing profile into a new saved profile.",
    help=(
        "Copy an existing saved `kiari` profile into a new profile.\n\n"
        "When only `TO_PROFILE` is provided, the current profile is used as the "
        "source.\n\nWhen both `FROM_PROFILE` and `TO_PROFILE` are provided, the source "
        "profile is copied explicitly.\n\nThe description, `run_spec.yaml`, and "
        "`config.yaml` are all copied.\n\nIf the target profile already exists, the "
        "command fails."
    ),
    epilog=(
        "Examples:\n\n"
        "kiari profile copy dev-copy\n\n"
        "kiari profile copy dev dev-copy\n\n"
        "Use `kiari profile use <name>` to switch to the copied profile afterwards."
    ),
)
@click.argument("profile_names", nargs=-1, metavar="[FROM_PROFILE] TO_PROFILE")
def copy(**kwargs: Any) -> None:  # pragma: no cover
    """Copy a profile."""
    _copy(**kwargs)


def _copy(profile_names: tuple[str, ...]) -> None:
    from_profile_name, to_profile_name = _parse_profile_names(profile_names)

    if not profile_store.has_profile(from_profile_name):
        raise click.ClickException(f"Profile not found: {from_profile_name}")

    if profile_store.has_profile(to_profile_name):
        raise click.ClickException(f"Profile already exists: {to_profile_name}")

    source_profile = profile_store.get_profile(from_profile_name)
    source_run_spec = profile_store.load_run_spec(from_profile_name)
    source_config = profile_store.load_config(from_profile_name)

    copied_profile = Profile(
        name=to_profile_name,
        description=source_profile.description,
    )
    profile_store.set_profile(copied_profile)
    profile_store.save_run_spec(to_profile_name, source_run_spec)
    profile_store.save_config(to_profile_name, source_config)

    run_spec_file_path = get_profile_run_spec_file_path(to_profile_name)
    config_file_path = get_profile_config_file_path(to_profile_name)

    console_registry.get().print(
        render_status_block(
            title=f"Copied profile '{from_profile_name}' to '{to_profile_name}'.",
            lines=[
                f"Source profile: [bold]{from_profile_name}[/bold]",
                f"Copied profile: [bold]{to_profile_name}[/bold]",
                f"Description: {copied_profile.description or '-'}",
                f"RunSpec file: [dim]{run_spec_file_path}[/dim]",
                f"Config file: [dim]{config_file_path}[/dim]",
                "Copied RunSpec file.",
                "Copied config file.",
                "Current profile unchanged.",
            ],
            status="success",
        )
    )


def _parse_profile_names(profile_names: tuple[str, ...]) -> tuple[str, str]:
    if len(profile_names) == 1:
        return profile_store.get_current(), profile_names[0]

    if len(profile_names) == 2:
        return profile_names[0], profile_names[1]

    raise click.ClickException("Expected `TO_PROFILE` or `FROM_PROFILE TO_PROFILE`.")
