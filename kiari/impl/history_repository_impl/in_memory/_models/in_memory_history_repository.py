import logging
from typing import ClassVar

from kiarina.agi.history import History
from kiarina.agi.run_context import RunContext

from kiari.lib.history_repository import BaseHistoryRepository

logger = logging.getLogger(__name__)


class InMemoryHistoryRepository(BaseHistoryRepository):
    _storage: ClassVar[dict[str, History]] = {}

    async def _load(self, run_context: RunContext) -> History | None:
        agent_id = run_context.agent_id
        logger.debug(f"Loading history from in-memory storage for agent_id={agent_id}")

        history = self._storage.get(agent_id)

        if history is None:
            return None

        return history.model_copy(deep=True)

    async def _save(self, history: History, run_context: RunContext) -> None:
        agent_id = run_context.agent_id
        logger.debug(f"Saving history to in-memory storage for agent_id={agent_id}")
        self._storage[agent_id] = history.model_copy(deep=True)

    async def _delete(self, run_context: RunContext) -> None:
        agent_id = run_context.agent_id
        logger.debug(f"Deleting history from in-memory storage for agent_id={agent_id}")
        self._storage.pop(agent_id, None)
