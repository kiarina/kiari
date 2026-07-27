from collections.abc import Sequence

from rich.console import Group, RenderableType
from rich.text import Text


def join_renderables(
    renderables: Sequence[RenderableType | None],
    *,
    separator: RenderableType | None = None,
    markup: bool = False,
) -> Group | None:
    joined: list[RenderableType] = []

    for renderable in renderables:
        if renderable is None:
            continue

        if joined and separator is not None:
            joined.append(_prepare_renderable(separator, markup=markup))

        joined.append(_prepare_renderable(renderable, markup=markup))

    if not joined:
        return None

    return Group(*joined)


def _prepare_renderable(renderable: RenderableType, *, markup: bool) -> RenderableType:
    if markup and isinstance(renderable, str):
        return Text.from_markup(renderable)

    return renderable
