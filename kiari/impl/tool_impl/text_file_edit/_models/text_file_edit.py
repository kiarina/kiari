from kiarina.agi.message import ToolMessage
from kiarina.agi.tool import ToolContext, tool

from .._operations.create import create
from .._operations.line_replace import line_replace
from .._operations.str_replace import str_replace
from .._operations.update import update
from .._schemas.text_file_edit_schema import TextFileEditSchema
from .._types.action import Action

_OPERATIONS = {
    "create": create,
    "update": update,
    "line_replace": line_replace,
    "str_replace": str_replace,
}


@tool(tool_schema=TextFileEditSchema)
async def TextFileEdit(
    ctx: ToolContext,
    action: Action,
    file_path: str,
    content: str = "",
    start_line: int = 1,
    end_line: int = 1,
    replace: str = "",
    search: str = "",
    replace_all: bool = False,
) -> ToolMessage:
    args = TextFileEditSchema(
        action=action,
        file_path=file_path,
        content=content,
        start_line=start_line,
        end_line=end_line,
        replace=replace,
        search=search,
        replace_all=replace_all,
    )

    return await _OPERATIONS[action](ctx, args)
