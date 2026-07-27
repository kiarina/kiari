import logging
from typing import Any

from kiarina.agi.history import History
from kiarina.agi.run_context import RunContext

from .._types.history_repository import HistoryRepository
from .._types.history_repository_name import HistoryRepositoryName

logger = logging.getLogger(__name__)


class BaseHistoryRepository(HistoryRepository):
    def __init__(self, **kwargs: Any) -> None:
        self.init_kwargs: dict[str, Any] = kwargs
        self._name: HistoryRepositoryName | None = None

    @property
    def name(self) -> HistoryRepositoryName:
        if not self._name:  # pragma: no cover
            raise AssertionError("HistoryRepository name not set")

        return self._name

    @name.setter
    def name(self, value: HistoryRepositoryName) -> None:
        self._name = value

    async def load(self, run_context: RunContext) -> History | None:
        logger.debug(f"Loading history in repository: {self}")
        return await self._load(run_context)

    async def save(self, history: History, run_context: RunContext) -> None:
        logger.debug(f"Saving history in repository: {self}")
        await self._save(history, run_context)

    async def delete(self, run_context: RunContext) -> None:
        logger.debug(f"Deleting history in repository: {self}")
        await self._delete(run_context)

    async def _load(self, run_context: RunContext) -> History | None:
        return None

    async def _save(self, history: History, run_context: RunContext) -> None:
        pass

    async def _delete(self, run_context: RunContext) -> None:
        pass

    def __str__(self) -> str:
        return self.__class__.__name__
