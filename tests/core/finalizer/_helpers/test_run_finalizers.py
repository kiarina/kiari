from collections.abc import AsyncIterator
from typing import Any, ClassVar

import pytest

from kiari.core.finalizer import BaseFinalizer, finalizer_registry, run_finalizers


class RecordingFinalizer(BaseFinalizer):
    events: ClassVar[list[str]] = []

    async def _finalize(self, *args: Any, **kwargs: Any) -> None:
        self.events.append(self.name)


class FailingFinalizer(BaseFinalizer):
    async def _finalize(self, *args: Any, **kwargs: Any) -> None:
        raise RuntimeError(f"failed: {self.name}")


@pytest.fixture(autouse=True)
def reset_recording_finalizer() -> AsyncIterator[None]:
    RecordingFinalizer.events = []
    yield
    for finalizer_name in ["test_first", "test_second", "test_failing"]:
        finalizer_registry.unregister(finalizer_name)


async def test_runs_in_specified_order() -> None:
    finalizer_registry.register("test_first", RecordingFinalizer)
    finalizer_registry.register("test_second", RecordingFinalizer)

    await run_finalizers(["test_first", "test_second"])

    assert RecordingFinalizer.events == ["test_first", "test_second"]


async def test_swallows_finalizer_error() -> None:
    finalizer_registry.register("test_failing", FailingFinalizer)

    await run_finalizers(["test_failing"])
