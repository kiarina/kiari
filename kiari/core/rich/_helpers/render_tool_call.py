import json
from typing import Any

from kiarina.agi.message import ToolCall
from rich.console import Group, RenderableType
from rich.style import Style
from rich.syntax import Syntax
from rich.text import Text


def render_tool_call(
    tool_call: ToolCall,
    *,
    style: str | Style = "",
) -> RenderableType:
    renderables: list[RenderableType] = [
        Text(f"[TOOL CALL] {tool_call}", style=style),
    ]

    if tool_call.args:
        renderables.append(_render_tool_call_args(tool_call.args, style=style))

    return Group(*renderables)


def _render_tool_call_args(
    args: dict[str, Any],
    style: str | Style = "",
) -> RenderableType:
    return Syntax(json.dumps(args, indent=2, ensure_ascii=False), "json")
