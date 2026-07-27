import json

from kiarina.agi.tool import ToolContext, ToolError
from kiarina.i18n import get_i18n

from kiari.lib.web import web_registry

from .._i18n import WebI18n
from .._schemas.web_schema import WebSchema


async def search(ctx: ToolContext, args: WebSchema) -> str:
    t = get_i18n(WebI18n, ctx.run_context.language)

    if not args.query:
        raise ToolError(t.search_requires_query_error)

    web = web_registry.resolve()
    results = await web.search(args.query)

    return json.dumps(
        [result.model_dump() for result in results],
        ensure_ascii=False,
    )
