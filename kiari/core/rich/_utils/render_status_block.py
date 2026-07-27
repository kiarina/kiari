from collections.abc import Sequence
from typing import Literal

from rich.console import Group, RenderableType
from rich.text import Text

Status = Literal["success", "warning", "error", "info"]

_STATUS_STYLES: dict[Status, str] = {
    "success": "green",
    "warning": "yellow",
    "error": "red",
    "info": "cyan",
}


def render_status_block(
    *,
    title: str,
    lines: Sequence[RenderableType] | None = None,
    status: Status = "info",
) -> RenderableType:
    color = _STATUS_STYLES[status]
    renderables: list[RenderableType] = [
        Text(),
        Text("━" * 80, style=color),
        Text(f" {title}", style=f"bold {color}"),
        Text("━" * 80, style=color),
    ]

    if lines:
        renderables.append(Text())

        for line in lines:
            if isinstance(line, str):
                renderables.append(Text.from_markup(line))
            else:
                renderables.append(line)

    renderables.append(Text())
    return Group(*renderables)
