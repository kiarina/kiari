import logging

from .._types.finalizer import Finalizer
from .._types.finalizer_name import FinalizerName

logger = logging.getLogger(__name__)


class BaseFinalizer(Finalizer):
    def __init__(self) -> None:
        self._name: FinalizerName | None = None

    @property
    def name(self) -> FinalizerName:
        if not self._name:  # pragma: no cover
            raise AssertionError("Finalizer name not set")

        return self._name

    @name.setter
    def name(self, value: FinalizerName) -> None:
        self._name = value

    async def finalize(self) -> None:
        logger.debug(f"Running finalizer: {self.name}")
        await self._finalize()

    async def _finalize(self) -> None:
        pass
