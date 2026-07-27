from abc import ABC, abstractmethod
from collections.abc import Sequence

from .._schemas.extension_command_context import ExtensionCommandContext
from .._types.extension_command import ExtensionCommand
from .._types.extension_command_name import ExtensionCommandName


class BaseExtensionCommand(ExtensionCommand, ABC):
    def __init__(self) -> None:
        self._name: ExtensionCommandName | None = None

    @property
    def name(self) -> ExtensionCommandName:
        if not self._name:  # pragma: no cover
            raise AssertionError("ExtensionCommand name not set")

        return self._name

    @name.setter
    def name(self, value: ExtensionCommandName) -> None:
        self._name = value

    @abstractmethod
    async def run(
        self,
        context: ExtensionCommandContext,
        args: Sequence[str],
    ) -> None: ...
