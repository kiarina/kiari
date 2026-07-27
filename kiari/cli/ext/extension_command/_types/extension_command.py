from collections.abc import Sequence
from typing import Protocol, runtime_checkable

from .._schemas.extension_command_context import ExtensionCommandContext
from .extension_command_name import ExtensionCommandName


@runtime_checkable
class ExtensionCommand(Protocol):
    name: ExtensionCommandName

    async def run(
        self,
        context: ExtensionCommandContext,
        args: Sequence[str],
    ) -> None: ...
