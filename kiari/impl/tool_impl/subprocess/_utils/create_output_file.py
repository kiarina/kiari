from typing import Any

from kiarina.agi.file_factory import create_file
from kiarina.agi.file_info import FileInfo
from kiarina.agi.tool import ToolContext


async def create_output_file(
    ctx: ToolContext,
    *,
    raw_text: str,
    display_name: str,
    start_line: int = 1,
    end_line: int = -1,
) -> FileInfo:
    """
    Create a text file holding process output.

    The file is shrunk from the end (``keep_from_end``) so that the most recent
    output survives when the content is trimmed for the model.
    """
    file_info_spec_overrides: dict[str, Any] = {
        "name": display_name,
        "keep_from_end": True,
    }

    if start_line != 1 or end_line != -1:
        file_info_spec_overrides["start_line"] = start_line
        file_info_spec_overrides["end_line"] = end_line

    result = await create_file(
        ctx.tool_call.name,
        mime_type="text/plain",
        raw_text=raw_text,
        file_info_spec_overrides=file_info_spec_overrides,
        run_context=ctx.run_context,
    )

    return result.file_info
