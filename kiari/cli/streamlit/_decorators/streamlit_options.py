import functools
from collections.abc import Callable

import rich_click as click
from kiarina.i18n import get_i18n, get_system_language

from .._i18n import StreamlitI18n

t = get_i18n(StreamlitI18n, get_system_language())


def streamlit_options[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    # fmt: off
    @click.option("--streamlit-host", type=str, help=t.host_help)
    @click.option("--streamlit-port", type=click.IntRange(min=1, max=65535), help=t.port_help)
    @click.option("--streamlit-headless/--no-streamlit-headless", default=None, help=t.headless_help)
    @click.option("--streamlit-title", type=str, help=t.title_help)
    @click.option("--streamlit-icon", type=str, help=t.icon_help)
    @click.option("--streamlit-layout", type=click.Choice(["centered", "wide"]), help=t.layout_help)
    @click.option("--streamlit-handler", type=str, help=t.handler_help)
    @click.option("--streamlit-authenticator", type=str, help=t.authenticator_help)
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        # fmt: on
        return func(*args, **kwargs)

    return wrapper
