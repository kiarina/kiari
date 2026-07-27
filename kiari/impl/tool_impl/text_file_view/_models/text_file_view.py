import logging
import os

from kiarina.agi.content import Content
from kiarina.agi.file_info_loader import load_file_info
from kiarina.agi.tool import ToolContext, tool
from kiarina.i18n import get_i18n

from .._i18n import TextFileViewI18n
from .._schemas.text_file_view_schema import TextFileViewSchema

logger = logging.getLogger(__name__)

_DIRECTORY_LIST_LIMIT = 100
"""Maximum number of directory entries to list in the directory error message"""


@tool(tool_schema=TextFileViewSchema)
async def TextFileView(
    ctx: ToolContext,
    file_path: str,
    start_line: int = 1,
    end_line: int = -1,
) -> Content:
    t = get_i18n(TextFileViewI18n, ctx.run_context.language)

    resolved_path = _resolve_path(file_path)

    if os.path.isdir(resolved_path):
        return Content(text=_directory_error(t, file_path, resolved_path))

    file_info = await load_file_info(
        {
            "uri_or_file_path": resolved_path,
            "start_line": start_line,
            "end_line": end_line,
        },
        run_context=ctx.run_context,
    )

    if file_info is None:
        return Content(text=t.not_found_error.format(file_path=file_path))

    return Content(text=t.result, files=[file_info])


def _resolve_path(path: str) -> str:
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)
    return os.path.abspath(path)


def _directory_error(
    t: TextFileViewI18n,
    file_path: str,
    resolved_path: str,
) -> str:
    try:
        entries = sorted(os.listdir(resolved_path))

        if entries:
            lines = []

            for entry in entries[:_DIRECTORY_LIST_LIMIT]:
                if os.path.isdir(os.path.join(resolved_path, entry)):
                    lines.append(f"- {entry}/")
                else:
                    lines.append(f"- {entry}")

            if len(entries) > _DIRECTORY_LIST_LIMIT:
                lines.append(f"- ... and {len(entries) - _DIRECTORY_LIST_LIMIT} more")

            file_list = "\n".join(lines)
        else:
            file_list = "(No entries found)"

    except Exception as e:
        logger.error("Error reading directory '%s': %s", resolved_path, e)
        file_list = f"(Error reading directory: {e!s})"

    return t.directory_error.format(file_path=file_path, file_list=file_list)
