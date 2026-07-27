from kiarina.agi.console_utils import divider, section_header
from kiarina.agi.event import (
    CustomEvent,
    Event,
)
from rich.console import Group, RenderableType
from rich.text import Text

from .render_message import render_message


def render_event(event: Event) -> RenderableType:
    if event.type == "human_message" or event.type == "ai_message" or event.type == "tool_message":
        return render_message(event.message)
    elif event.type == "custom":
        return _render_custom_event(event)
    else:  # pragma: no cover
        raise AssertionError(f"Unknown event type: {event.type}")


def _render_custom_event(event: CustomEvent) -> RenderableType:
    style = "magenta"
    fill_char = "="
    title = _format_custom_event_title(event)

    renderables: list[RenderableType] = [
        Text(section_header(title, fill_char=fill_char), style=style),
    ]

    if event.payload:
        for key, value in event.payload.items():
            renderables.append(Text(f"{key}: {_format_value(value)}", style=style))

        renderables.append(Text(divider(fill_char=fill_char), style=style))

    return Group(*renderables)


def _format_custom_event_title(event: CustomEvent) -> str:
    if custom_type := event.payload.get("type"):
        return f"CUSTOM EVENT: {custom_type}"
    else:
        return "CUSTOM EVENT"


def _format_value(value: object) -> str:
    if isinstance(value, (str, int, float, bool)):
        return str(value)
    else:
        return type(value).__name__
