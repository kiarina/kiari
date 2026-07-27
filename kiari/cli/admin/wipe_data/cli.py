import shutil
from dataclasses import dataclass
from pathlib import Path

import rich_click as click
from kiarina.utils.app import user_directory

from kiari.core.rich import console_registry, render_status_block


# fmt: off
@click.command(
    name="wipe-data",
    short_help="Remove persistent user data created by kiari runs.",
    help=(
        "Remove persistent user data created by `kiari` agent execution.\n\n"
        "User data means durable data generated while running kiari, such as saved "
        "runtime data and other application-managed persistent files.\n\n"
        "[bold]Profile settings are not deleted.[/bold]"
    ),
)
@click.option("-f", "--force", is_flag=True, help="Delete user data files without asking for confirmation.")
def wipe_data(force: bool) -> None:  # pragma: no cover
    """Delete persistent kiari user data while keeping profile settings."""
    # fmt: on

    @dataclass(frozen=True)
    class FileTarget:
        path: Path
        size_bytes: int

    directory = user_directory.get_user_data_dir()
    file_targets = (
        [
            FileTarget(path=path, size_bytes=path.stat().st_size)
            for path in sorted(directory.rglob("*"))
            if path.is_file()
        ]
        if directory.exists()
        else []
    )
    total_line = (
        f"Total: {len(file_targets)} files, "
        f"{_format_size(sum(file_target.size_bytes for file_target in file_targets))}"
    )

    preview_lines = [f"Directory: {directory}", "Files:"]

    if file_targets:
        preview_lines.extend(
            f"- {file_target.path} ({_format_size(file_target.size_bytes)})"
            for file_target in file_targets
        )
    else:
        preview_lines.append("- (none)")

    preview_lines.append(total_line)

    console_registry.get().print(
        render_status_block(
            title="Wipe User Data",
            lines=preview_lines,
            status="warning",
        )
    )

    if not force and not click.confirm(
        "Delete these user data files?",
        default=False,
    ):
        console_registry.get().print("Wipe User Data cancelled.", style="yellow")
        return

    if directory.exists():
        shutil.rmtree(directory)

    console_registry.get().print(
        render_status_block(
            title="Wipe User Data",
            lines=[
                f"Directory: {directory}",
                "Status: deleted successfully",
                total_line,
            ],
            status="success",
        )
    )


def _format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"

    size = float(size_bytes)
    units = ["KiB", "MiB", "GiB", "TiB"]

    for unit in units:
        size /= 1024
        if size < 1024:
            return f"{size:.1f} {unit}"

    return f"{size:.1f} PiB"
