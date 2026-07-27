from .._models.subprocess_manager import SubprocessManager
from .._settings import settings_manager

_manager: SubprocessManager | None = None


def get_subprocess_manager() -> SubprocessManager:
    global _manager

    if not _manager:
        _manager = SubprocessManager(settings=settings_manager.settings)

    return _manager
