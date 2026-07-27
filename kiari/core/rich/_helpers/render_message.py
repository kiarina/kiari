from kiarina.agi.console_utils import divider, section_header
from kiarina.agi.content import Content
from kiarina.agi.display_content import DisplayContent
from kiarina.agi.message import (
    AIMessage,
    HumanMessage,
    Message,
    ToolCall,
    ToolMessage,
)
from rich.console import Group, RenderableType
from rich.style import Style
from rich.text import Text

from .render_content import render_content
from .render_display_content import render_display_content
from .render_tool_call import render_tool_call


def render_message(message: Message) -> RenderableType:
    if message.type == "human":
        return _render_human_message(message)
    elif message.type == "ai":
        return _render_ai_message(message)
    elif message.type == "tool":
        return _render_tool_message(message)
    else:
        raise AssertionError(f"Unsupported message type: {message.type}")


def _render_human_message(message: HumanMessage) -> RenderableType:
    renderables: list[RenderableType] = [
        Text(section_header("HUMAN MESSAGE"), style="cyan"),
    ]

    if renderable := _render_contents(message.contents, style="cyan"):
        renderables.append(Text())
        renderables.append(renderable)

    return Group(*renderables)


def _render_ai_message(message: AIMessage) -> RenderableType:
    renderables: list[RenderableType] = [
        Text(section_header("AI MESSAGE"), style="yellow"),
    ]

    if renderable := _render_contents(message.contents, style="yellow"):
        renderables.append(Text())
        renderables.append(renderable)

    if renderable := _render_tool_calls(message.tool_calls, style="yellow"):
        renderables.append(Text())
        renderables.append(renderable)

    return Group(*renderables)


def _render_tool_message(message: ToolMessage) -> RenderableType:
    style = "green" if not message.failed else "red"

    renderables: list[RenderableType] = [
        Text(section_header(f"TOOL MESSAGE: {message}"), style=style),
    ]

    if message.failed:
        renderables.append(Text("failed: True", style=style))

    if message.return_direct:
        renderables.append(Text("return_direct: True", style=style))

    if message.artifact:
        renderables.append(Text(f"artifacts: {', '.join(message.artifact.keys())}", style=style))

    for key, value in message.metadata.items():
        renderables.append(Text(f"{key}: {value}", style=style))

    if len(renderables) > 1:
        renderables.append(Text(divider(), style=style))

    if renderable := _render_contents(message.contents, style=style):
        renderables.append(Text())
        renderables.append(renderable)

    if renderable := _render_display_contents(message.display_contents, style=style):
        renderables.append(Text())
        renderables.append(renderable)

    return Group(*renderables)


def _render_contents(
    contents: list[Content],
    style: str | Style = "",
) -> RenderableType | None:
    renderables: list[RenderableType] = []

    for content in contents:
        if renderables:
            renderables.append(Text())

        renderables.append(render_content(content, style=style))

    if not renderables:
        return None

    return Group(*renderables)


def _render_tool_calls(
    tool_calls: list[ToolCall],
    style: str | Style = "",
) -> RenderableType | None:
    renderables: list[RenderableType] = []

    for tool_call in tool_calls:
        if renderables:
            renderables.append(Text())

        renderables.append(render_tool_call(tool_call, style=style))

    if not renderables:
        return None

    return Group(*renderables)


def _render_display_contents(
    display_contents: list[DisplayContent],
    style: str | Style = "",
) -> RenderableType | None:
    renderables: list[RenderableType] = []

    for display_content in display_contents:
        if renderables:
            renderables.append(Text())

        renderables.append(render_display_content(display_content, style=style))

    if not renderables:
        return None

    return Group(*renderables)
