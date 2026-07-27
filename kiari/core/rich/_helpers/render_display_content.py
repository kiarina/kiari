from kiarina.agi.display_content import (
    DisplayContent,
    FileDisplayContent,
    TextDisplayContent,
)
from rich.console import Group, RenderableType
from rich.markdown import Markdown
from rich.style import Style
from rich.syntax import Syntax
from rich.text import Text


def render_display_content(
    display_content: DisplayContent,
    *,
    style: str | Style = "",
) -> RenderableType:
    if display_content.type == "text":
        return _render_text_display_content(display_content, style=style)
    elif display_content.type == "file":
        return _render_file_display_content(display_content, style=style)
    else:  # pragma: no cover
        raise AssertionError(f"Unknown display content type: {display_content.type}")


def _render_text_display_content(
    text_display_content: TextDisplayContent,
    *,
    style: str | Style = "",
) -> RenderableType:
    renderables: list[RenderableType] = [
        Text(
            f"[TEXT DISPLAY CONTENT] {text_display_content.mime_type}",
            style=style,
        ),
        Text(),
    ]

    if text_display_content.mime_type in (
        "text/markdown",
        "text/md",
        "text/x-markdown",
    ):
        renderables.append(
            Markdown(
                text_display_content.text,
                code_theme="monokai",
                hyperlinks=True,
            )
        )
    else:
        renderables.append(
            Syntax(
                text_display_content.text,
                _lexer_name(text_display_content.mime_type),
                line_numbers=True,
                word_wrap=True,
                start_line=text_display_content.start_line,
            )
        )

    return Group(*renderables)


def _lexer_name(mime_type: str) -> str:
    if mime_type in ("application/json", "text/json"):
        return "json"
    elif mime_type in ("text/css",):
        return "css"
    elif mime_type in ("text/html", "application/xhtml+xml"):
        return "html"
    elif mime_type in ("text/javascript", "application/javascript"):
        return "javascript"
    elif mime_type in ("text/x-python", "application/x-python-code"):
        return "python"
    else:
        return "text"


def _render_file_display_content(
    file_display_content: FileDisplayContent,
    *,
    style: str | Style = "",
) -> RenderableType:
    return Text(_format_file_display_content(file_display_content), style=style)


def _format_file_display_content(file_display_content: FileDisplayContent) -> str:
    parts = [
        "[FILE DISPLAY CONTENT]",
        file_display_content.mime_type,
        file_display_content.uri,
    ]

    if file_display_content.display_name:
        parts.append(f"({file_display_content.display_name})")

    return " ".join(parts)
