from pathlib import Path
from typing import Any, Literal

import rich_click as click
from rich.markup import escape
from rich.table import Table

from kiari.core.paths import (
    get_config_file_path,
    get_profile_config_file_path,
    get_profile_run_spec_file_path,
)
from kiari.core.profile import Profile, profile_store
from kiari.core.rich import console_registry

ColumnName = Literal["profile", "description", "updated_at", "run_spec", "config"]
SortName = Literal["name", "updated"]

DEFAULT_COLUMNS: tuple[ColumnName, ...] = (
    "profile",
    "description",
    "updated_at",
    "run_spec",
    "config",
)

VALID_COLUMNS: tuple[ColumnName, ...] = DEFAULT_COLUMNS
VALID_SORTS: tuple[SortName, ...] = ("name", "updated")


@click.command(
    "list",
    short_help="Show the saved profiles managed by kiari.",
    help=(
        "Show the saved `kiari` profiles as a rich table.\n\n"
        "The list includes the current profile, profile descriptions, update times, "
        "and links to profile-specific `run_spec.yaml` and `config.yaml` files. "
        "You can also filter the displayed profiles, choose the sort order, and "
        "limit which columns are shown."
    ),
    epilog=(
        "Examples:\n\n"
        "kiari profile list\n\n"
        "kiari profile list --columns profile,run_spec\n\n"
        "kiari profile list --sort updated\n\n"
        "kiari profile list --query dev\n\n"
        "kiari profile list --show-run-spec-content --show-config-content\n\n"
        "Use `kiari profile use <name>` to switch the current profile."
    ),
)
@click.option(
    "-c",
    "--columns",
    type=str,
    help=(
        "Comma-separated columns to display. "
        "Available: profile, description, updated_at, run_spec, config."
    ),
)
@click.option(
    "-q",
    "--query",
    type=str,
    help="Case-insensitive substring filter for profile names.",
)
@click.option(
    "-s",
    "--sort",
    "sort_name",
    type=click.Choice(VALID_SORTS),
    default="name",
    show_default=True,
    help="Sort profiles by `name` (ascending) or `updated` (newest first).",
)
@click.option(
    "-r",
    "--show-run-spec-content",
    is_flag=True,
    help="Show the full YAML content below the RunSpec link.",
)
@click.option(
    "-f",
    "--show-config-content",
    is_flag=True,
    help="Show the full YAML content below the Config link.",
)
def list_command(**kwargs: Any) -> None:  # pragma: no cover
    """List saved profiles."""
    _list(**kwargs)


def _list(
    columns: str | None = None,
    query: str | None = None,
    sort_name: SortName = "name",
    show_run_spec_content: bool = False,
    show_config_content: bool = False,
) -> None:
    """List saved profiles."""
    console = console_registry.get()

    current_profile_name = profile_store.get_current()
    profiles = profile_store.list_profiles()
    selected_columns = _parse_columns(columns)
    profiles = _filter_profiles(profiles, query)
    profiles = _sort_profiles(profiles, sort_name)

    common_config_path = get_config_file_path()

    if not profiles:
        console.print("No matching profiles found.", style="yellow")
        console.print(f"Common config file: {_format_config_path(common_config_path)}")
        return

    table = Table(
        title="Saved Profiles",
        show_header=True,
        show_edge=True,
        show_lines=True,
        padding=(0, 1),
        border_style="blue",
        caption=_build_table_caption(
            total_profiles=len(profiles),
            current_profile_name=current_profile_name,
            query=query,
            sort_name=sort_name,
        ),
        caption_style="dim",
    )

    if "profile" in selected_columns:
        table.add_column("Profile", style="bold cyan", vertical="top")
    if "description" in selected_columns:
        table.add_column("Description", vertical="top")
    if "updated_at" in selected_columns:
        table.add_column("Updated At", style="dim", vertical="top")
    if "run_spec" in selected_columns:
        table.add_column("RunSpec", style="green", vertical="top", overflow="fold")
    if "config" in selected_columns:
        table.add_column(
            "Config",
            style="blue",
            vertical="top",
            overflow="fold",
        )

    for profile in profiles:
        profile_name = (
            f"[yellow]* {profile.name}[/yellow]"
            if profile.name == current_profile_name
            else profile.name
        )
        run_spec_text = _format_profile_file_cell(
            get_profile_run_spec_file_path(profile.name),
            show_content=show_run_spec_content,
        )
        profile_config_text = _format_profile_file_cell(
            get_profile_config_file_path(profile.name),
            show_content=show_config_content,
        )

        row: list[str] = []
        if "profile" in selected_columns:
            row.append(profile_name)
        if "description" in selected_columns:
            row.append(profile.description or "-")
        if "updated_at" in selected_columns:
            row.append(profile.updated_at.astimezone().strftime("%Y-%m-%d %H:%M:%S %Z"))
        if "run_spec" in selected_columns:
            row.append(run_spec_text)
        if "config" in selected_columns:
            row.append(profile_config_text)

        table.add_row(*row)

    console.print(table)
    console.print()
    console.print(f"Common config file: {_format_config_path(common_config_path)}")


def _format_config_path(path: Path) -> str:
    suffix = "" if path.exists() else " [dim](missing)[/dim]"
    return f"[link=file://{path}]{path}[/link]{suffix}"


def _format_profile_file_cell(path: Path, show_content: bool) -> str:
    if not path.exists():
        return "[dim](missing)[/dim]"

    link = f"[link=file://{path}]Open[/link]"

    if not show_content:
        return link

    content = path.read_text().rstrip()
    if not content:
        return f"{link}\n[dim](empty)[/dim]"

    return f"{link}\n{escape(content)}"


def _parse_columns(columns: str | None) -> tuple[ColumnName, ...]:
    if columns is None:
        return DEFAULT_COLUMNS

    parsed = tuple(column.strip() for column in columns.split(",") if column.strip())

    if not parsed:
        raise click.ClickException("No columns specified.")

    invalid = [column for column in parsed if column not in VALID_COLUMNS]

    if invalid:
        raise click.ClickException(
            f"Unknown columns: {', '.join(invalid)}. Available: {', '.join(VALID_COLUMNS)}."
        )

    return parsed  # type: ignore[return-value]


def _filter_profiles(profiles: list[Profile], query: str | None) -> list[Profile]:
    if not query:
        return profiles

    normalized_query = query.casefold()

    return [profile for profile in profiles if normalized_query in profile.name.casefold()]


def _sort_profiles(profiles: list[Profile], sort_name: SortName) -> list[Profile]:
    if sort_name == "updated":
        return sorted(profiles, key=lambda profile: profile.updated_at, reverse=True)

    return sorted(profiles, key=lambda profile: profile.name.casefold())


def _build_table_caption(
    total_profiles: int,
    current_profile_name: str,
    query: str | None,
    sort_name: SortName,
) -> str:
    parts = [
        f"[yellow]*[/yellow] marks the current profile: [bold]{current_profile_name}[/bold]",
        f"Profiles shown: {total_profiles}",
        f"Sort: {sort_name}",
    ]

    if query:
        parts.append(f"Filter: {escape(query)}")

    return " | ".join(parts)
