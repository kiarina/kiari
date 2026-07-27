from typing import Protocol, runtime_checkable

from kiarina.agi.history import History
from kiarina.agi.run_context import RunContext

from .history_repository_name import HistoryRepositoryName


@runtime_checkable
class HistoryRepository(Protocol):
    name: HistoryRepositoryName

    async def load(self, run_context: RunContext) -> History | None: ...
    async def save(self, history: History, run_context: RunContext) -> None: ...
    async def delete(self, run_context: RunContext) -> None: ...
