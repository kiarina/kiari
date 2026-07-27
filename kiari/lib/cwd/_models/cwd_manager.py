import os

from kiarina.agi.local_repository import LocalRepository, create_local_repository
from kiarina.agi.run_context import RunContext
from kiarina.utils.file.asyncio import read_json_dict, write_json_dict

from .._schemas.cwd_state import CWDState


class CWDManager:
    def __init__(self, run_context: RunContext) -> None:
        self.run_context: RunContext = run_context

    # ----------------------------------------
    # Properties
    # ----------------------------------------

    @property
    def local_repository(self) -> LocalRepository:
        return create_local_repository(run_context=self.run_context)

    # ----------------------------------------
    # Methods
    # ----------------------------------------

    async def recover_directory(self) -> None:
        state = await self._read_state()

        if state is None:
            return

        if state.current_directory == os.getcwd():
            return

        if not os.path.exists(state.current_directory) or not os.path.isdir(
            state.current_directory
        ):
            await self._delete_state()
        else:
            os.chdir(state.current_directory)

    async def change_directory(self, directory_path: str | os.PathLike[str]) -> None:
        abs_path = os.path.abspath(os.fspath(directory_path))

        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"Directory not found: {abs_path}")

        if not os.path.isdir(abs_path):
            raise NotADirectoryError(f"Not a directory: {abs_path}")

        os.chdir(abs_path)

        await self._write_state(CWDState(current_directory=abs_path))

    # ----------------------------------------
    # Private Methods
    # ----------------------------------------

    async def _read_state(self) -> CWDState | None:
        data = await read_json_dict(self._get_state_file_path())

        if data is None:
            return None

        return CWDState.model_validate(data)

    async def _write_state(self, state: CWDState) -> None:
        await write_json_dict(self._get_state_file_path(), state.model_dump())

    async def _delete_state(self) -> None:
        state_file_path = self._get_state_file_path()

        if os.path.exists(state_file_path):
            os.remove(state_file_path)

    def _get_state_file_path(self) -> str:
        return self.local_repository.generate_data_path("runner_state.json")
