from collections.abc import Awaitable, Callable

from kiarina.agi.tool import ToolContext, tool

from .._operations.fetch import fetch
from .._operations.search import search
from .._schemas.web_schema import WebSchema
from .._types.action import Action

_OPERATIONS: dict[Action, Callable[[ToolContext, WebSchema], Awaitable[str]]] = {
    "search": search,
    "fetch": fetch,
}


@tool(tool_schema=WebSchema)
async def Web(
    ctx: ToolContext,
    action: Action,
    query: str = "",
    url: str = "",
) -> str:
    args = WebSchema(
        action=action,
        query=query,
        url=url,
    )

    return await _OPERATIONS[action](ctx, args)
