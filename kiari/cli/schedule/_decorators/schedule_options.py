import functools
from collections.abc import Callable

import rich_click as click


def schedule_options[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    # fmt: off
    @click.option("--interval", type=str, help="Run at a fixed interval, e.g. 5m, 1h, 30s.")
    @click.option("--cron", type=str, help="Run with a cron expression, e.g. '0 */6 * * *'.")
    @click.option("--schedule-handler", type=str, help="Schedule handler name.")
    @click.option("--skip-if-no-events", is_flag=True, default=None, help="Skip execution when no events are available.")
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        # fmt: on
        return func(*args, **kwargs)

    return wrapper
