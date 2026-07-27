import functools
from collections.abc import Callable

import rich_click as click


def watch_options[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    # fmt: off
    @click.option("--watch-handler", type=str)
    @click.option("--watch-max-concurrent", type=int)
    @click.option("--watch-queue-size", type=int)
    @click.option("--watch-queue-put-timeout", type=float)
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        # fmt: on
        return func(*args, **kwargs)

    return wrapper
