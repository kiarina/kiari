from kiarina.agi.tool import ToolContext, ToolError
from kiarina.i18n import get_i18n

from kiari.lib.web import web_registry

from .._i18n import WebI18n
from .._schemas.web_schema import WebSchema


async def fetch(ctx: ToolContext, args: WebSchema) -> str:
    t = get_i18n(WebI18n, ctx.run_context.language)

    if not args.url:
        raise ToolError(t.fetch_requires_url_error)

    web = web_registry.resolve()
    return await web.fetch(args.url)
