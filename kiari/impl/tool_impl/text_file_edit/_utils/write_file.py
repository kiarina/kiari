import kiarina.utils.file.asyncio as kfa
from kiarina.agi.file_info_loader import load_file_info
from kiarina.agi.message import ToolMessage
from kiarina.agi.tool import ToolContext

from .build_result import build_result


async def write_file(
    ctx: ToolContext,
    *,
    file_path: str,
    old_content: str,
    content: str,
    result_text: str,
) -> ToolMessage:
    """Write the full content of a file and build the result ToolMessage."""
    # Ensure the file ends with a newline
    if content and content[-1] != "\n":
        content += "\n"

    await kfa.write_text(file_path, content)

    file_info = await load_file_info(file_path, run_context=ctx.run_context)
    assert file_info is not None  # pragma: no cover

    return build_result(
        ctx,
        file_path=file_path,
        old_content=old_content,
        new_content=content,
        file_info=file_info,
        result_text=result_text,
    )
