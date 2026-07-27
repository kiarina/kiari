from kiarina.agi.file_info import FileInfo
from rich.console import RenderableType
from rich.style import Style
from rich.text import Text


def render_file_info(
    file_info: FileInfo,
    *,
    style: str | Style = "",
) -> RenderableType:
    return Text(_format_file_info(file_info), style=style)


def _format_file_info(file_info: FileInfo) -> str:
    parts = [
        f"[{file_info.type.upper()} FILE INFO]",
        file_info.uri,
    ]

    if file_info.name:
        parts.append(f"({file_info.name})")

    return " ".join(parts)
