import os

from kiarina.agi.tool import ToolContext, ToolError, tool
from kiarina.i18n import get_i18n

from kiari.lib.cwd import create_cwd_manager

from .._i18n import ChangeDirectoryI18n
from .._schemas.change_directory_schema import ChangeDirectorySchema


@tool(tool_schema=ChangeDirectorySchema)
async def ChangeDirectory(ctx: ToolContext, dir_path: str) -> str:
    t = get_i18n(ChangeDirectoryI18n, ctx.run_context.language)

    dir_path = os.path.expandvars(dir_path)
    dir_path = os.path.expanduser(dir_path)

    try:
        cwd_manager = create_cwd_manager(ctx.run_context)
        await cwd_manager.change_directory(dir_path)

    except FileNotFoundError:
        raise ToolError(t.file_not_found_error.format(dir_path=dir_path)) from None
    except PermissionError:
        raise ToolError(t.permission_error.format(dir_path=dir_path)) from None
    except NotADirectoryError:
        raise ToolError(t.not_a_directory_error.format(dir_path=dir_path)) from None

    return t.result.format(dir_path=dir_path)
