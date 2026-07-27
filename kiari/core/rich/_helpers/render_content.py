import json

from kiarina.agi.console_utils import section_header
from kiarina.agi.content import Content
from rich.console import Group, RenderableType
from rich.style import Style
from rich.text import Text

from .render_file_info import render_file_info

DEFAULT_CONTENT = Content()


def render_content(
    content: Content,
    *,
    style: str | Style = "",
) -> RenderableType:
    renderables: list[RenderableType] = []

    if content.tag != DEFAULT_CONTENT.tag:
        renderables.append(Text(f"[TAG] {content.tag}", style=style))

    if content.description:
        renderables.append(Text(f"[DESCRIPTION] {content.description}", style=style))

    if content.file_tags:
        file_tags_str = ", ".join(
            f"{file_type}={tag}" for file_type, tag in content.file_tags.items()
        )
        renderables.append(Text(f"[FILE TAGS] {file_tags_str}", style=style))

    if content.template != DEFAULT_CONTENT.template:
        renderables.extend(
            [
                Text("[TEMPLATE]", style=style),
                Text(section_header("START", fill_char="="), style=style),
                Text(content.template, style=style),
                Text(section_header("END", fill_char="="), style=style),
            ]
        )

    for file_info in content.files:
        renderables.append(render_file_info(file_info, style=style))

    if content.text:
        if renderables:
            renderables.append(Text())

        renderables.append(Text(content.text, style=style))

    if content.cache_control:
        if renderables:
            renderables.append(Text())

        renderables.append(
            Text(f"[CACHE CONTROL] {json.dumps(content.cache_control)}", style=style)
        )

    if not renderables:
        return Text()

    return Group(*renderables)
