from collections.abc import Awaitable, Callable
from typing import Any

from kiari.core.finalizer import run_finalizers
from kiari.core.profile import ProfileName, RunOptions


async def run(
    runner: Callable[..., Awaitable[Any]],
    profile_name: ProfileName,
    run_options: RunOptions,
    *args: Any,
    **kwargs: Any,
) -> None:
    try:
        await runner(profile_name, run_options, *args, **kwargs)
    finally:
        await run_finalizers(run_options.finalizers)
