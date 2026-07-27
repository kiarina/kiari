import logging
from collections.abc import Sequence

from .._services.finalizer_registry import finalizer_registry
from .._types.finalizer_specifier import FinalizerSpecifier

logger = logging.getLogger(__name__)


async def run_finalizers(finalizers: Sequence[FinalizerSpecifier]) -> None:
    for finalizer_specifier in finalizers:
        finalizer = finalizer_registry.resolve(finalizer_specifier)

        try:
            await finalizer.finalize()
        except Exception:
            logger.error(
                f"Finalizer failed: {finalizer_specifier}",
                exc_info=True,
            )
