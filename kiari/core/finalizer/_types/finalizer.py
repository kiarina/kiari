from typing import Protocol, runtime_checkable

from .finalizer_name import FinalizerName


@runtime_checkable
class Finalizer(Protocol):
    name: FinalizerName

    async def finalize(self) -> None: ...
