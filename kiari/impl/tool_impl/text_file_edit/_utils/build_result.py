import difflib
from copy import deepcopy

from kiarina.agi.content import Content
from kiarina.agi.display_content import DisplayContent, TextDisplayContent
from kiarina.agi.file_info import FileInfo
from kiarina.agi.message import ToolMessage
from kiarina.agi.tool import ToolContext


def build_result(
    ctx: ToolContext,
    *,
    file_path: str,
    old_content: str,
    new_content: str,
    file_info: FileInfo,
    result_text: str,
) -> ToolMessage:
    """
    Build a ToolMessage for a successful edit.

    The resulting file is attached as the model-facing content, while the
    unified diff is attached as a display content for the user.
    """
    display_contents: list[DisplayContent] = []

    diff = "".join(
        difflib.unified_diff(
            old_content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=f"{file_path} (before)",
            tofile=f"{file_path} (after)",
        )
    )

    if diff:
        display_contents.append(TextDisplayContent(text=diff, mime_type="text/x-diff"))

    return ToolMessage(
        tool_name=ctx.tool_call.name,
        tool_call_args=deepcopy(ctx.tool_call.args),
        tool_call_id=ctx.tool_call.id,
        contents=[Content(text=result_text, files=[file_info])],
        display_contents=display_contents,
    )
