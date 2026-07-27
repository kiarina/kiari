from collections.abc import Awaitable, Callable

from kiarina.agi.content import Content
from kiarina.agi.tool import ToolContext, tool

from .._operations.cancel import cancel
from .._operations.get_list import get_list
from .._operations.get_output import get_output
from .._operations.run import run
from .._operations.run_background import run_background
from .._schemas.subprocess_schema import SubprocessSchema
from .._types.action import Action

_OPERATIONS: dict[Action, Callable[[ToolContext, SubprocessSchema], Awaitable[str | Content]]] = {
    "run": run,
    "run_background": run_background,
    "get_output": get_output,
    "get_list": get_list,
    "cancel": cancel,
}


@tool(tool_schema=SubprocessSchema)
async def Subprocess(
    ctx: ToolContext,
    action: Action,
    argv: list[str] | None = None,
    cwd: str | None = None,
    env: dict[str, str] | None = None,
    input_data: str | None = None,
    wait_time: int | None = None,
    run_id: str = "",
    start_line: int = 1,
    end_line: int = -1,
    graceful_shutdown_timeout: float = 3.0,
) -> str | Content:
    args = SubprocessSchema(
        action=action,
        argv=argv or [],
        cwd=cwd,
        env=env,
        input_data=input_data,
        wait_time=wait_time,
        run_id=run_id,
        start_line=start_line,
        end_line=end_line,
        graceful_shutdown_timeout=graceful_shutdown_timeout,
    )

    return await _OPERATIONS[action](ctx, args)
