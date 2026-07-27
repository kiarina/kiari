from kiarina.agi.run_context import RunContext

from .._models.cwd_manager import CWDManager


def create_cwd_manager(run_context: RunContext) -> CWDManager:
    return CWDManager(run_context)
