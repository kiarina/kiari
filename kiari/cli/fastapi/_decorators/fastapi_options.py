import functools
from collections.abc import Callable

import rich_click as click
from kiarina.i18n import get_i18n, get_system_language

from .._i18n import FastAPII18n

t = get_i18n(FastAPII18n, get_system_language())


def fastapi_options[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    # fmt: off
    @click.option("--fastapi-path", type=str, help=t.path_help)
    @click.option("--fastapi-host", type=str, help=t.host_help)
    @click.option("--fastapi-port", type=int, help=t.port_help)
    @click.option("--fastapi-workers", type=click.IntRange(min=1), help=t.workers_help)
    @click.option("--fastapi-handler", type=str, help=t.handler_help)
    @click.option("--fastapi-authenticator", type=str, help=t.authenticator_help)
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        # fmt: on
        return func(*args, **kwargs)

    return wrapper
