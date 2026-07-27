import functools
from collections.abc import Callable

import rich_click as click
from kiarina.i18n import get_i18n, get_system_language

from .._i18n import BatchI18n

t = get_i18n(BatchI18n, get_system_language())


def batch_options[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    # fmt: off
    # Persistent batch options. These become RunSpec fields and may be saved to a Profile.
    @click.option("--batch-handler", type=str, help=t.batch_handler_help)
    @click.option("--output-text", is_flag=True, default=None, help=t.output_text_help)
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        # fmt: on
        return func(*args, **kwargs)

    return wrapper
