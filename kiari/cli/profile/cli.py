import rich_click as click

from .copy.cli import copy
from .delete.cli import delete
from .list.cli import list_command
from .new.cli import new
from .set.cli import set_command
from .use.cli import use


@click.group(
    short_help="Manage saved profiles and the current profile used by kiari.",
    help=(
        "Manage saved `kiari` profiles.\n\n"
        "Use this command group to inspect available profiles, create new profiles, "
        "switch the current profile, and delete profiles that are no longer needed."
    ),
    panel="Manage Commands",
)
def profile() -> None:
    """Profile commands."""


profile.add_command(list_command)
profile.add_command(copy)
profile.add_command(new)
profile.add_command(set_command)
profile.add_command(delete)
profile.add_command(use)
