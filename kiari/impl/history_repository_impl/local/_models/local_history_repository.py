import logging

from kiarina.agi.history import History
from kiarina.agi.local_repository import create_local_repository
from kiarina.agi.run_context import RunContext
from kiarina.utils.file.asyncio import read_json_dict, remove_file, write_json_dict

from kiari.lib.history_repository import BaseHistoryRepository

from .._settings import LocalHistoryRepositorySettings

logger = logging.getLogger(__name__)


class LocalHistoryRepository(BaseHistoryRepository):
    def __init__(self, settings: LocalHistoryRepositorySettings) -> None:
        self.settings: LocalHistoryRepositorySettings = settings

    async def _load(self, run_context: RunContext) -> History | None:
        file_path = self._get_file_path(run_context)
        logger.info(f"Loading history from {file_path}")

        data = await read_json_dict(file_path)

        if data is None:
            return None

        return History.model_validate(data)

    async def _save(self, history: History, run_context: RunContext) -> None:
        file_path = self._get_file_path(run_context)
        logger.info(f"Saving history to {file_path}")
        await write_json_dict(file_path, history.model_dump(mode="json"))

    async def _delete(self, run_context: RunContext) -> None:
        file_path = self._get_file_path(run_context)
        logger.info(f"Deleting history file {file_path}")
        await remove_file(file_path)

    def _get_file_path(self, run_context: RunContext) -> str:
        local_repository = create_local_repository(run_context)
        return local_repository.generate_data_path(self.settings.file_name)
