from kiari.core.finalizer import BaseFinalizer
from kiari.lib.subprocess import terminate_all_sessions


class SubprocessFinalizer(BaseFinalizer):
    async def _finalize(self) -> None:
        terminate_all_sessions()
